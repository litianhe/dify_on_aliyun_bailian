import logging
import requests
import json
from requests import Response
from http import HTTPStatus
from collections.abc import Generator
from typing import Optional, Union

from dify_plugin import LargeLanguageModel
from dify_plugin.entities import I18nObject
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
)
from dify_plugin.entities.model import (
    AIModelEntity,
    FetchFrom,
    ModelType,
)
from dify_plugin.entities.model.llm import (
    LLMResult
)
from dify_plugin.entities.model.message import (
    PromptMessage,
    PromptMessageTool,
)

from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

from dashscope.common.error import (
    AuthenticationError,
    InvalidParameter,
    RequestFailure,
    ServiceUnavailableError,
    UnsupportedHTTPMethod,
    UnsupportedModel,
)
from dify_plugin.entities.model.llm import LLMResult, LLMResultChunk, LLMResultChunkDelta
from dify_plugin.entities.model.message import (
    AssistantPromptMessage,
    ImagePromptMessageContent,
    PromptMessage,
    PromptMessageContentType,
    PromptMessageTool,
    UserPromptMessage,
    VideoPromptMessageContent,
)

logger = logging.getLogger(__name__)


class AliYunLargeLanguageModel(LargeLanguageModel):
    """
    Model class for AliYun large language model.
    """

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        return self._generate(model, credentials, prompt_messages, model_parameters, tools, stop, stream, user)
   
    def get_num_tokens(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        tools: Optional[list[PromptMessageTool]] = None,
    ) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param tools: tools for tool calling
        :return:
        """
        return 0

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            api_key = credentials["api_key"]
            app_id = credentials["app_id"]
            if api_key and app_id:
                r = self.send_input_message(app_id, api_key, "hello")
                if r.status_code == 200:
                    return True
                else:
                    self._handle_error(r)
                    return False
            else:
                raise CredentialsValidateFailedError("Invalid credentials")
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def send_input_message(self, app_id: str, api_key: str, prompt_message:str, stream:bool = True) -> Response:
        url = f"https://dashscope.aliyuncs.com/api/v1/apps/{app_id}/completion"
        headers = self._prepare_headers(api_key, stream=stream)
        body = {
            "input": {
                "prompt": prompt_message,
            },
            "parameters": {},
            "debug": {},
        }
        if stream:
            body["parameters"] = {"incremental_output": True}
        return self._post_request(url, body, headers, stream=stream)

    def get_customizable_model_schema(
        self, model: str, credentials: dict
    ) -> AIModelEntity:
        """
        If your model supports fine-tuning, this method returns the schema of the base model
        but renamed to the fine-tuned model name.

        :param model: model name
        :param credentials: credentials

        :return: model schema
        """
        entity = AIModelEntity(
            model=model,
            label=I18nObject(zh_Hans=model, en_US=model),
            model_type=ModelType.LLM,
            features=[],
            fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
            model_properties={},
            parameter_rules=[],
        )
        return entity

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeConnectionError: [RequestFailure],
            InvokeServerUnavailableError: [ServiceUnavailableError],
            InvokeRateLimitError: [],
            InvokeAuthorizationError: [AuthenticationError],
            InvokeBadRequestError: [InvalidParameter, UnsupportedModel, UnsupportedHTTPMethod],
        }

    def _prepare_headers(self, api_key, stream):
        h = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        if stream:
            h["X-DashScope-SSE"] = "enable"
        return h

    def _post_request(self, url, data, headers, stream):
        return requests.post(url, headers=headers, json=data, stream=stream)
    
    def _handle_error(self, response):
        if response.status_code in {402, 409, 500}:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(f"Failed to authorize. Status code: {response.status_code}. Error: {error_message}")
        else:
            if response.text:
                error_message = json.loads(response.text).get("error", "Unknown error occurred")
                raise Exception(f"Failed to authorize. Status code: {response.status_code}. Error: {error_message}")
            raise Exception(f"Unexpected error occurred while trying to authorize. Status code: {response.status_code}")


    def _generate(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param tools: tools for tool calling
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        # stream = False
        prompt = self._convert_prompt_messages_to_yunbailian_messages(prompt_messages)
        credentials_kwargs = {"api_key": credentials["api_key"], "app_id": credentials["app_id"]}
        r = self.send_input_message(**credentials_kwargs, prompt_message=prompt, stream=stream)
        if stream:
            return self._handle_generate_stream_response(model, credentials, r, prompt_messages)
        return self._handle_generate_response(model, credentials, r, prompt_messages)

    def _handle_generate_stream_response(
        self, model: str, credentials: dict, r: Response, prompt_messages: list[PromptMessage]
    ) -> Generator:
        """
        Handle llm stream response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response chunk generator result
        """
        if r.status_code not in {200, HTTPStatus.OK}:
            raise ServiceUnavailableError(r.text)
        for index, line in enumerate(r.iter_lines()):
            if line:
                line = line.decode("utf-8")
                line = line.strip()
                if line.startswith("data:"):
                    json_data = line[5:].strip()
                    if json_data:
                        chunk_data = json.loads(json_data)
                        output_text = chunk_data.get("output", {}).get("text", "")
                        assistant_message = AssistantPromptMessage(content=output_text)
                        chunk = LLMResultChunk(
                            model=model,
                            delta=LLMResultChunkDelta(index=index, message=assistant_message),
                            prompt_messages=prompt_messages,
                        )
                        yield chunk

    def _handle_generate_response(
        self, model: str, credentials: dict, r: Response, prompt_messages: list[PromptMessage]
    ) -> LLMResult:
        """
        Handle llm response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response
        """
        if r.status_code not in {200, HTTPStatus.OK}:
            raise ServiceUnavailableError(r.text)
        response_json = r.json()
        output_text = response_json.get("output", {}).get("text")
        prompt_tokens = 0
        completion_tokens = 0
        for m in response_json.get("usage", {}).get("models",[]):
            input_token = m.get("input_tokens", 0)
            output_token = m.get("output_tokens", 0)
            prompt_tokens += input_token
            completion_tokens += output_token
        assistant_prompt_message = AssistantPromptMessage(content=output_text)
        usage = self._calc_response_usage(
            model,
            credentials,
            prompt_tokens,
            completion_tokens
        )
        result = LLMResult(
            model=model, 
            prompt_messages=prompt_messages, 
            message=assistant_prompt_message, 
            usage=usage)
        return result

    def _convert_prompt_messages_to_yunbailian_messages(
        self, prompt_messages: list[PromptMessage], rich_content: bool = False
    ) -> str:
        for prompt_message in prompt_messages:
            if isinstance(prompt_message, UserPromptMessage):
                if isinstance(prompt_message.content, str):
                    return prompt_message.content
        raise ValueError(f"Got unknown type {prompt_message}")
        

