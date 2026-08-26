"""Skill 执行器:用生成的 Skill 分析用户数据 -> 输出复盘报告"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

os.environ["NO_PROXY"] = "open.bigmodel.cn"

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

def execute_skill(skill: dict, user_data: str) -> str:
    """核心函数:Skill 配置 + 业务数据 -> 分析报告(流式输出)"""
    system_prompt = f"""{skill['agent_prompt']}

**分析流程(必须严格按此顺序执行):**
{chr(10).join(skill['analysis_steps'])}

**输出模板(必须严格按此结构输出):**
{skill['output_template']}
"""
    stream = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分析以下直播数据:\n\n{user_data}"}
        ],
        temperature=0.5,
        stream=True,
        timeout=300,
    )
    chunks = []
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)  # 实时打印
        chunks.append(delta)
    print()
    return "".join(chunks)



#网页渲染
def execute_skill_stream(skill: dict, user_data: str):
    """流式版本:逐段 yield 内容,供 Web 界面实时渲染"""
    system_prompt = f"""{skill['agent_prompt']}

**分析流程(必须严格按此顺序执行):**
{chr(10).join(skill['analysis_steps'])}

**输出模板(必须严格按此结构输出):**
{skill['output_template']}
"""
    stream = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分析以下业务数据:\n\n{user_data}"}
        ],
        temperature=0.5,
        stream=True,
        timeout=300,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta



if __name__ == "__main__":
    import os.path
    from generator import generate_skill

    # 优先加载已保存的 Skill,没有才重新生成
    if os.path.exists("sample_skill.json"):
        with open("sample_skill.json", "r", encoding="utf-8") as f:
            skill = json.load(f)
        print(f"已加载缓存 Skill: {skill['skill_name']}\n")
    else:
        print("正在生成 Skill...")
        skill = generate_skill("帮我创建一个抖音直播运营复盘 Skill")
        with open("sample_skill.json", "w", encoding="utf-8") as f:
            json.dump(skill, f, ensure_ascii=False, indent=2)  # 生成后立刻保存
        print(f"Skill 生成完成: {skill['skill_name']}\n")

    sample_data = """
直播日期: 2026-08-20
直播时长(分钟): 180
场观人数(PV): 52000
进房率: 4.2%
平均停留时长(秒): 22
互动率: 3.1%
点击率(CTR): 2.8%
转化率(CVR): 0.7%
客单价(AOV): 89元
GMV: 91000元
ROI: 1.8
主播姓名: AAA
推广产品: 秋季新款连衣裙
异常事件备注: 直播中段(约90分钟处)有10分钟网络卡顿
"""
    print("正在执行分析...\n")
    report = execute_skill(skill, sample_data)