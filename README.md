<p align="center">
  <a href="./README.md"><img alt="README in English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="./README_CN.md"><img alt="简体中文版自述文件" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
</p>

# Overview
![](_assets/yunbailian_s_en.png) 
The Dify `Tongyi Qianwen` plugin enables Dify to easily utilize various models provided by Alibaba Cloud for building rich LLM applications. In this scenario, Dify only uses the model APIs provided by Alibaba Cloud, while other resources required for building LLM applications (e.g., UI, API management) are provided by Dify.

However, the **Alibaba Cloud Bailian platform** also offers capabilities for building LLM applications. Through the [Alibaba Cloud Bailian App Center](https://bailian.console.aliyun.com/#/app-center), you can create various types of LLM applications such as knowledge bases, workflows, and agent applications. Applications built here can seamlessly integrate with data stored on Alibaba Cloud (including structured and unstructured databases), enabling functionalities like knowledge base Q&A, knowledge base workflows, and knowledge base agent applications. While this overlaps with Dify's capabilities, it eliminates the need to configure Dify to use Alibaba Cloud-hosted data. Since both models and data reside on Alibaba Cloud, this approach avoids transferring data to Dify, reduces configuration/maintenance complexity, and eliminates latency/security risks from local data processing. The tradeoff is losing some of Dify's rich features and configuration flexibility.

**This plugin allows Dify to  leverage AliYun BaiLian LLM application on Alibaba Cloud**, combining the benefits above while retaining Dify's functionalities to build more powerful LLM applications.

---

# Advantages of Using This Plugin
✅ **Seamless Bridging of Non-OpenAI-Compatible APIs**  
- Alibaba Cloud Bailian applications **natively use APIs incompatible with OpenAI specifications**. This plugin integrates Bailian applications with Dify **without modifying existing Bailian applications**.  

✅ **Retain Dify Features While Reusing Alibaba Cloud Capabilities**  
- Leverage Dify's UI interactions, Prompt engineering, and API management while invoking pre-built Bailian applications (e.g., knowledge base Q&A, workflows) **without reconfiguring databases/knowledge bases in Dify**.  

✅ **Eliminate Complex Infrastructure Maintenance**  
- Data storage, vectorization, and model inference are fully managed by Alibaba Cloud. Dify acts only as an interaction/agent layer, **avoiding maintenance of databases/vector engines**.  

✅ **Data Security & Compliance**  
- Data remains entirely within Alibaba Cloud environments. The plugin **only transmits inputs/responses** with no local caching or secondary storage risks.  

✅ **Improved Development Efficiency**  
- Reuse pre-configured LLM applications from Bailian App Center (e.g., customer service bots, document analysis) to **avoid redundant development in Dify**, accelerating deployment.  

# Notes When Using This Plugin
- **Prerequisite**: You must first create applications in the [Alibaba Cloud Bailian App Center](https://bailian.console.aliyun.com/#/app-center).  You can also config the data source and/or setup workflows/agents for it.
- Dify's logging system cannot directly track internal Bailian API states (e.g., vector search latency, model shard load).  

---

# Configuration
After installing the plugin in Dify:  
1. Obtain API keys from the [Alibaba Cloud Bailian Platform](https://bailian.console.aliyun.com/?apiKey=1#/api-key) and configure them under **Settings > Model Provider**.  
2. If you haven't created an LLM application, build one in the [Alibaba Cloud App Center](https://bailian.console.aliyun.com/#/app-center).  
3. Each LLM application has a unique **App ID** (a 32-character string like `65ce7884f97fd4365471e76989eaa25d`), obtainable from the Alibaba Cloud App Center. 

# Contact Author
tianhe.li@outlook.com









