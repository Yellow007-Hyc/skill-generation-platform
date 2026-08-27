# 企业岗位经验 Skill 生成平台

用自然语言描述岗位需求,自动将企业岗位经验沉淀为结构化、可复用、可执行的 AI 员工 Skill,并支持直接调用 Skill 完成业务数据分析。

> 面试项目 Demo:数花智算 DataAgent「企业岗位经验 Skill 生成平台设计」

## 核心闭环

```
自然语言输入 ──▶ Skill 自动生成 ──▶ Skill 配置展示 ──▶ 调用 Skill 执行 ──▶ 输出分析报告
```

例如输入"帮我创建一个抖音直播运营复盘 Skill",系统自动生成包含以下 7 个组成部分的完整 Skill 配置:

Skill 名称、Skill 描述、使用场景、输入数据定义、分析流程、Agent Prompt、输出结果模板。

随后用户按输入定义粘贴业务数据(如直播场次数据),即可调用该 Skill 生成结构化复盘报告。

## 在线演示

- 演示视频:demo演示视频黄彦铖.mp4
- 在线地址:通过网盘分享的文件：demo演示视频黄彦铖.mp4
链接: https://pan.baidu.com/s/1mXC9e4MkiLem78ciMXJ_5w?pwd=6666 提取码: 6666

## 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/Yellow007-Hyc/skill-generation-platform.git
cd skill-generation-platform

# 2. 安装依赖(建议使用虚拟环境)
pip install -r requirements.txt

# 3. 配置 API Key
# 复制 .env.example 为 .env,填入你的智谱 API Key(免费申请:https://open.bigmodel.cn)

# 4. 启动
streamlit run app.py
```

浏览器打开 http://localhost:8501 即可使用。本项目使用智谱 GLM-4.7-Flash(官方免费模型),零成本即可完整运行。

## 项目结构

```
skill_platform/
├── app.py              # Streamlit Web 界面:四步闭环交互
├── generator.py        # Skill 生成器:元 Prompt + JSON 校验 + 失败重试
├── executor.py         # Skill 执行器:组装 Agent Prompt,流式输出分析报告
├── skill_schema.py     # Skill JSON Schema:平台核心数据契约(7 个组成部分)
├── sample_skill.json   # 示例:自动生成的「抖音直播运营复盘」Skill
├── docs/
│   ├── PRD.md          # 产品设计文档
│   ├── 技术方案.md      # 技术方案说明
│   ├── report_v1_有幻觉.md  # 治理前报告存档(模型虚构了目标值)
│   └── report_v2_修复后.md  # 治理后报告存档(未提供数据标注"未提供")
└── requirements.txt
```

## 关键设计

**Schema 约束生成。** Skill 不是一段自由文本,而是一份符合 JSON Schema 的结构化配置。生成阶段将 Schema 注入元 Prompt,要求模型只输出合规 JSON;生成后由程序校验必填字段与结构,校验失败自动把错误信息回传给模型重试(最多 3 次)。

**幻觉治理的真实案例。** 开发过程中发现:执行阶段模型会虚构输入中不存在的"目标值/同环比"数据。通过在元 Prompt 中加入数据纪律规则(未提供的数据一律标注"未提供",不得虚构,计算须注明过程)修复,治理前后的报告均存档于 docs/ 目录。进一步测试也暴露了 Prompt 治理的边界:它能防"编造数据",但防不住"计算与概念错误"(如把 GMV÷人数误当转化率),对应的演进方向是将确定性指标计算下沉到代码层,LLM 只负责解读与归因,详见技术方案。

**生成与执行分离。** LLM 承担双重角色:生成阶段是"Skill 架构师"(低温度,保结构稳定),执行阶段按 Skill 中的 Agent Prompt 扮演"岗位专家"(流式输出,保演示体验)。两阶段解耦,Skill 配置可存储、可编辑、可复用。

## 文档

- [产品设计文档(PRD)](docs/PRD.md)
- [技术方案说明](docs/技术方案.md)
