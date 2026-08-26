"""Skill 生成器:自然语言需求 -> 结构化 Skill 配置"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from skill_schema import SKILL_SCHEMA

load_dotenv()

os.environ["NO_PROXY"] = "open.bigmodel.cn"

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

META_PROMPT = f"""你是一个企业岗位经验 Skill 架构师。你的任务是:根据用户的自然语言需求,\
把某个企业岗位的优秀员工经验,沉淀为一个结构化、可复用、可执行的 AI 员工 Skill 配置。

要求:
1. 站在该岗位资深专家的视角设计:分析流程要体现真实的业务方法论(如电商复盘要看流量-转化-客单价拆解、\
同环比、异常归因),不要泛泛而谈。
2. input_definition 要贴合该业务场景真实可获得的数据字段。
3. agent_prompt 是给执行阶段 AI 用的系统提示词,必须包含:角色设定、分析框架、判断标准(如什么算异常)、\
输出格式要求。写详细,这是 Skill 的灵魂。
4. output_template 用 Markdown,包含清晰的章节结构,每个章节注明应填入什么内容。
5. agent_prompt 中必须包含一条数据纪律规则:分析时只能使用用户实际提供的数据;\
用户未提供的信息(如目标值、历史数据、同比环比、行业均值)一律不得虚构,\
相关内容应标注"未提供"或直接省略;所有计算必须基于输入数据,并注明计算过程。
6. 全部使用中文。


严格按照以下 JSON Schema 输出,只输出 JSON 本身,不要任何解释、前言或 Markdown 代码块标记:
{json.dumps(SKILL_SCHEMA, ensure_ascii=False, indent=2)}
"""

def validate_skill(skill: dict) -> list:
    """轻量校验:检查必填字段是否齐全、类型是否正确,返回错误列表"""
    errors = []
    for field in SKILL_SCHEMA["required"]:
        if field not in skill or not skill[field]:
            errors.append(f"缺少必填字段: {field}")
    if "input_definition" in skill and isinstance(skill["input_definition"], list):
        for i, item in enumerate(skill["input_definition"]):
            if not isinstance(item, dict) or "field_name" not in item:
                errors.append(f"input_definition[{i}] 结构不完整")
    return errors

def generate_skill(user_request: str, max_retries: int = 3) -> dict:
    """核心函数:自然语言 -> Skill 配置,失败自动重试"""
    messages = [
        {"role": "system", "content": META_PROMPT},
        {"role": "user", "content": user_request}
    ]
    last_error = ""
    for attempt in range(max_retries):
        resp = client.chat.completions.create(
            model="glm-4.7-flash",
            messages=messages,
            temperature=0.3,  # 低温度保证结构稳定
        )
        raw = resp.choices[0].message.content.strip()
        # 清理可能的 markdown 代码块包裹
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw[4:] if raw.startswith("json") else raw
        try:
            skill = json.loads(raw)
            errors = validate_skill(skill)
            if not errors:
                return skill
            last_error = "; ".join(errors)
        except json.JSONDecodeError as e:
            last_error = f"JSON 解析失败: {e}"
        # 把错误反馈给模型重试
        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user",
                         "content": f"你的输出有问题:{last_error}。请修正后重新输出完整 JSON。"})
    raise RuntimeError(f"生成失败(已重试{max_retries}次): {last_error}")

if __name__ == "__main__":
    skill = generate_skill("帮我创建一个抖音直播运营复盘 Skill")
    print(json.dumps(skill, ensure_ascii=False, indent=2))