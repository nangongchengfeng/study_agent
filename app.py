"""
智能编程学习导师 - Streamlit 网页版
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from src.workflows import TeachingWorkflow

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="智能编程学习导师",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化会话状态
if 'workflow' not in st.session_state:
    st.session_state.workflow = TeachingWorkflow()

if 'current_step' not in st.session_state:
    st.session_state.current_step = -1

if 'viewing_step' not in st.session_state:
    st.session_state.viewing_step = -1

if 'state' not in st.session_state:
    st.session_state.state = None

if 'steps_completed' not in st.session_state:
    st.session_state.steps_completed = []

# 步骤定义
STEPS = [
    ("understanding", "📊 理解评估"),
    ("memory_retrieval", "🔍 记忆检索"),
    ("explanation", "📚 个性化讲解"),
    ("example_generation", "💻 示例生成"),
    ("practice_generation", "📝 练习生成"),
    ("validation", "🎯 学习验证"),
    ("memory_update", "💾 记忆更新"),
]


def init_state(user_query, user_level):
    """初始化工作流状态"""
    st.session_state.state = {
        "user_input": user_query,
        "user_query": user_query,
        "user_level": user_level,
        "conversation_history": [],
        "current_step": "start",
        "workflow_id": "streamlit_demo",
        "supplement_count": 0,
        "existing_knowledge": [],
        "new_knowledge": {},
        "code_execution_result": "",
        "documentation_result": "",
        "practice_evaluation_result": "",
        "understanding_result": {},
        "memory_retrieval_result": {},
        "explanation_result": "",
        "example_result": "",
        "practice_result": "",
        "validation_result": {},
        "memory_update_result": {},
        "is_complete": False,
        "error_message": None,
        "feedback": "",
    }
    st.session_state.current_step = 0
    st.session_state.viewing_step = 0
    st.session_state.steps_completed = []


def execute_step(step_idx):
    """执行指定步骤"""
    workflow = st.session_state.workflow
    state = st.session_state.state
    step_name, step_display = STEPS[step_idx]

    try:
        if step_name == "understanding":
            update = workflow._run_understanding(state)
            state.update(update)
        elif step_name == "memory_retrieval":
            update = workflow._run_memory_retrieval(state)
            state.update(update)
        elif step_name == "explanation":
            update = workflow._run_explanation(state)
            state.update(update)
        elif step_name == "example_generation":
            update = workflow._run_example_generation(state)
            state.update(update)
        elif step_name == "practice_generation":
            update = workflow._run_practice_generation(state)
            state.update(update)
        elif step_name == "validation":
            update = workflow._run_validation(state)
            state.update(update)
        elif step_name == "memory_update":
            update = workflow._run_memory_update(state)
            state.update(update)

        st.session_state.steps_completed.append(step_idx)
        return True
    except Exception as e:
        st.error(f"执行步骤失败: {str(e)}")
        logger.error(f"步骤执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def display_step_result(step_idx):
    """显示步骤结果"""
    state = st.session_state.state
    step_name, step_display = STEPS[step_idx]

    if step_name == "understanding":
        result = state["understanding_result"]
        st.subheader("📊 理解评估结果")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("查询类型", result.get('query_type', 'N/A'))
        col2.metric("难度", result.get('difficulty', 'N/A'))
        col3.metric("学习目标", result.get('learning_objective', 'N/A'))
        col4.metric("置信度", f"{result.get('confidence', 0):.2f}")
        st.write("**主题:**", ", ".join(result.get('topics', [])))
        st.write("**关键词:**", ", ".join(result.get('keywords', [])))

    elif step_name == "memory_retrieval":
        result = state["memory_retrieval_result"]
        knowledge = result.get('related_knowledge', [])
        st.subheader("🔍 记忆检索结果")
        st.info(f"检索到 {len(knowledge)} 条相关知识")
        if knowledge:
            for i, k in enumerate(knowledge, 1):
                with st.expander(f"{k.get('title', f'知识 {i}')}"):
                    st.write(k.get('content', ''))

    elif step_name == "explanation":
        result = state["explanation_result"]
        st.subheader("📚 讲解内容")
        st.markdown(result)

    elif step_name == "example_generation":
        result = state["example_result"]
        st.subheader("💻 示例代码")
        st.code(result, language='python')

    elif step_name == "practice_generation":
        result = state["practice_result"]
        st.subheader("📝 练习题")
        st.markdown(result)

    elif step_name == "validation":
        result = state["validation_result"]
        st.subheader("🎯 学习验证")
        col1, col2 = st.columns(2)
        score = result.get('score', 0)
        col1.metric("掌握分数", f"{score:.2f}")
        col2.metric("掌握程度", result.get('mastery_level', 'N/A'))
        st.write("**反馈:**")
        st.success(result.get('feedback', ''))
        suggestions = result.get('suggestions', [])
        if suggestions:
            st.write("**建议:**")
            for s in suggestions:
                st.write(f"- {s}")

    elif step_name == "memory_update":
        st.subheader("💾 记忆更新")
        st.success("学习记忆已更新！")


# 主界面
st.title("🎓 智能编程学习导师")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    user_level = st.selectbox(
        "选择您的水平",
        ["beginner", "intermediate", "advanced"],
        index=1,
        format_func=lambda x: {
            "beginner": "🌱 初级",
            "intermediate": "📖 中级",
            "advanced": "🚀 高级"
        }.get(x, x)
    )

    st.markdown("---")
    st.header("📋 步骤进度")

    # 显示可点击的步骤
    for i, (_, step_name) in enumerate(STEPS):
        is_completed = i in st.session_state.steps_completed
        is_current = i == st.session_state.current_step
        is_viewing = i == st.session_state.viewing_step

        if is_viewing:
            st.info(f"👁️ {step_name}")
        elif is_completed:
            if st.button(f"✅ {step_name}", key=f"step_{i}", use_container_width=True):
                st.session_state.viewing_step = i
                st.rerun()
        elif is_current:
            st.info(f"⏳ {step_name}")
        else:
            st.text(f"⏸️ {step_name}")

    st.markdown("---")
    if st.button("🔄 重置", type="secondary", use_container_width=True):
        st.session_state.current_step = -1
        st.session_state.viewing_step = -1
        st.session_state.state = None
        st.session_state.steps_completed = []
        st.rerun()

# 主内容区
if st.session_state.current_step == -1:
    # 初始状态：输入问题
    st.header("💬 请输入您的编程问题")
    user_query = st.text_area(
        "问题内容",
        placeholder="例如：什么是Python的继承？",
        height=100
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🚀 开始学习", type="primary", disabled=not user_query):
            init_state(user_query, user_level)
            st.rerun()

    # 快速示例
    st.markdown("---")
    st.subheader("💡 快速示例")
    example_queries = [
        "什么是Python的装饰器？",
        "如何使用列表推导式？",
        "解释一下Python的继承",
        "什么是生成器和迭代器？",
    ]
    for q in example_queries:
        if st.button(q, key=f"example_{q}"):
            init_state(q, user_level)
            st.rerun()

else:
    # 显示当前正在查看的步骤
    viewing_step_idx = st.session_state.viewing_step
    current_step_idx = st.session_state.current_step

    if viewing_step_idx >= 0 and viewing_step_idx < len(STEPS):
        # 如果当前步骤未完成，先执行它
        if current_step_idx == viewing_step_idx and current_step_idx not in st.session_state.steps_completed:
            step_name, step_display = STEPS[current_step_idx]
            with st.spinner(f"正在执行: {step_display}..."):
                success = execute_step(current_step_idx)
                if success:
                    st.rerun()

        # 显示正在查看的步骤
        if viewing_step_idx in st.session_state.steps_completed:
            display_step_result(viewing_step_idx)

        st.markdown("---")

        # 操作按钮区域
        col1, col2, col3 = st.columns([1, 1, 4])

        # 如果查看的是当前步骤且还有下一步
        if viewing_step_idx == current_step_idx and current_step_idx < len(STEPS) - 1:
            with col1:
                if st.button("➡️ 下一步", type="primary"):
                    st.session_state.current_step += 1
                    st.session_state.viewing_step += 1
                    st.rerun()
        elif viewing_step_idx == current_step_idx and current_step_idx == len(STEPS) - 1:
            st.success("🎉 所有步骤完成！")
            with col1:
                if st.button("🔄 新问题", type="primary"):
                    st.session_state.current_step = -1
                    st.session_state.viewing_step = -1
                    st.session_state.state = None
                    st.session_state.steps_completed = []
                    st.rerun()

        # 如果查看的不是当前步骤，提供返回当前步骤的按钮
        elif viewing_step_idx != current_step_idx:
            with col1:
                if st.button("↩️ 返回当前", type="secondary"):
                    st.session_state.viewing_step = current_step_idx
                    st.rerun()
