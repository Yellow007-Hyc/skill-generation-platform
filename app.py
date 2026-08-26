"""企业岗位经验 Skill 生成平台 - Web Demo"""
import json
import streamlit as st
from generator import generate_skill
from executor import execute_skill_stream  # 稍后在 executor.py 里加这个函数

st.set_page_config(page_title="Skill 生成平台", page_icon="🛠️", layout="wide")
st.title("🛠️ 企业岗位经验 Skill 生成平台")
st.caption("用自然语言描述岗位需求,自动生成可执行的 AI 员工 Skill")

# 会话状态:保存生成的 Skill
if "skill" not in st.session_state:
    st.session_state.skill = None

# ========== 第一步:生成 Skill ==========
st.header("① 描述你的需求")
user_request = st.text_input(
    "自然语言输入",
    placeholder="例如:帮我创建一个抖音直播运营复盘 Skill",
)
if st.button("生成 Skill", type="primary"):
    if not user_request.strip():
        st.warning("请先输入需求描述")
    else:
        with st.spinner("正在生成 Skill,约需 1-2 分钟..."):
            try:
                st.session_state.skill = generate_skill(user_request)
                st.success("Skill 生成成功!")
            except Exception as e:
                st.error(f"生成失败: {e}")

# ========== 第二步:展示 Skill 配置 ==========
skill = st.session_state.skill
if skill:
    st.header(f"② Skill 配置:{skill['skill_name']}")
    st.write(skill["skill_description"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("使用场景")
        for uc in skill["use_cases"]:
            st.markdown(f"- {uc}")
        st.subheader("分析流程")
        for step in skill["analysis_steps"]:
            st.markdown(f"- {step}")
    with col2:
        st.subheader("输入数据定义")
        st.table([
            {"字段": f["field_name"], "类型": f["field_type"],
             "必填": "是" if f["required"] else "否", "说明": f["description"]}
            for f in skill["input_definition"]
        ])
    with st.expander("查看 Agent Prompt"):
        st.code(skill["agent_prompt"], language=None)
    with st.expander("查看输出模板"):
        st.code(skill["output_template"], language="markdown")
    st.download_button("下载 Skill 配置 (JSON)",
                       json.dumps(skill, ensure_ascii=False, indent=2),
                       file_name="skill.json", mime="application/json")

    # ========== 第三步:执行 Skill ==========
    st.header("③ 输入业务数据,执行分析")
    fields_hint = "\n".join(f"{f['field_name']}: " for f in skill["input_definition"])
    user_data = st.text_area("按输入定义粘贴/填写数据", value=fields_hint, height=280)
    if st.button("执行分析", type="primary"):
        st.header("④ 分析结果")
        placeholder = st.empty()
        acc = ""
        try:
            for delta in execute_skill_stream(skill, user_data):
                acc += delta
                placeholder.markdown(acc)  # 流式渲染
            st.download_button("下载报告 (Markdown)", acc,
                               file_name="report.md", mime="text/markdown")
        except Exception as e:
            st.error(f"执行失败: {e}")