"""Skill 数据结构定义:平台的核心资产"""

SKILL_SCHEMA = {
    "type": "object",
    "properties": {
        "skill_name": {"type": "string", "description": "Skill 名称,简洁有辨识度"},
        "skill_description": {"type": "string", "description": "一段话说明该 Skill 的能力与价值"},
        "use_cases": {
            "type": "array", "items": {"type": "string"},
            "description": "3-5 个典型使用场景"
        },
        "input_definition": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field_name": {"type": "string"},
                    "field_type": {"type": "string", "description": "如 数值/文本/日期/百分比"},
                    "required": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["field_name", "field_type", "required", "description"]
            },
            "description": "执行该 Skill 需要的输入数据字段定义"
        },
        "analysis_steps": {
            "type": "array", "items": {"type": "string"},
            "description": "分析流程,按顺序的步骤列表,体现岗位专家的分析方法论"
        },
        "agent_prompt": {
            "type": "string",
            "description": "执行时使用的系统提示词:定义 AI 员工的角色、分析框架、判断标准、输出要求"
        },
        "output_template": {
            "type": "string",
            "description": "Markdown 格式的输出结果模板,含各章节标题与占位说明"
        }
    },
    "required": ["skill_name", "skill_description", "use_cases",
                 "input_definition", "analysis_steps", "agent_prompt", "output_template"]
}