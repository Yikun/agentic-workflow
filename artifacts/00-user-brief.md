# User brief
[Describe your project here before running the orchestrator]

我需要开发一个基于Github Issue的Agentic Workflow，它可以自动化地从Github Issue中提取需求，设计系统架构，生成代码，并执行测试。

建议拆分为3个阶段，
第一个阶段，需求分析阶段，Agent会从Github Issue中提取需求，并生成结构化的需求文档。包含requirements和requirements-qa两个Agent，并将需求的结果，通过Github issue评论。用户批准后，进入第二个阶段。

第二个阶段，设计、开发阶段，Agent会根据需求文档设计系统架构并生成代码。完成开发后，提交PR，CI通过并在issue评论**自动**进入第三阶段。

第三个阶段，测试阶段，Agent会根据测试用例执行测试并生成测试报告。

请完成Github Action Workflow的需求分析、设计、开发。请使用中文。

DASHSCOPE_API_KEY 已经配置，opencode GLM-5
Alibaba (China)

！！请使用中文输出