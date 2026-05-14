"""
职业规划智能体 - Streamlit 前端应用
支持简历上传、智能体对话、人岗匹配和职业规划功能
"""
import streamlit as st
import sys
import json
import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="职业规划智能体",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 样式定制 ====================
st.markdown("""
<style>
.stChatMessage {
    font-size: 14px;
}
.stAlert {
    font-size: 13px;
}
.reasoning-block {
    background-color: #f0f2f6;
    border-left: 4px solid #1f77b4;
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 4px;
    font-size: 13px;
    color: #555;
}
.tool-block {
    background-color: #fff8e1;
    border-left: 4px solid #ff9800;
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 4px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ==================== Session State 初始化 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None

if "student_profile" not in st.session_state:
    st.session_state.student_profile = None

if "job_profile" not in st.session_state:
    st.session_state.job_profile = None

if "match_result" not in st.session_state:
    st.session_state.match_result = None

# 用于控制显示详情
if "show_student_profile" not in st.session_state:
    st.session_state.show_student_profile = False
if "show_job_profile" not in st.session_state:
    st.session_state.show_job_profile = False
if "show_match_result" not in st.session_state:
    st.session_state.show_match_result = False

# API 后端配置 - 使用流式输出
USE_API_BACKEND = True
API_BASE_URL = "http://localhost:8000/api"
USE_STREAMING = True  # 启用流式输出

# 保存后端会话 ID
if "backend_session_id" not in st.session_state:
    st.session_state.backend_session_id = None

# ==================== 辅助函数 ====================
def read_resume_file(uploaded_file) -> Optional[str]:
    """读取上传的简历文件"""
    # 惰性导入，避免页面加载时触发
    from studentprofile_agent.utils.file_reader import read_word, read_pdf

    try:
        file_path = uploaded_file.getvalue()
        file_ext = uploaded_file.name.lower().split('.')[-1]

        # 保存临时文件
        temp_path = ROOT_DIR / "temp_resume"
        temp_path.mkdir(exist_ok=True)
        file_save_path = temp_path / uploaded_file.name

        with open(file_save_path, 'wb') as f:
            f.write(file_path)

        # 根据文件类型读取
        if file_ext == 'txt':
            with open(file_save_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == 'docx':
            content = read_word(str(file_save_path))
        elif file_ext == 'pdf':
            content = read_pdf(str(file_save_path))
        else:
            st.error(f"不支持的文件格式：{file_ext}")
            return None

        # 清理临时文件
        file_save_path.unlink()

        return content
    except Exception as e:
        st.error(f"读取简历失败：{str(e)}")
        return None

def remove_emojis(text: str) -> str:
    """移除 emoji 字符以便在控制台显示"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def get_or_create_workflow():
    """获取或创建工作流实例"""
    # 惰性导入，避免页面加载时触发 RAG 初始化
    from main_agent.workflow import create_workflow

    if st.session_state.workflow_app is None:
        st.session_state.workflow_app = create_workflow()
    return st.session_state.workflow_app

def reset_agent_state():
    """重置智能体状态"""
    st.session_state.agent_state = {
        "messages": [],
        "resume_text": st.session_state.resume_text,
        "student_profile": st.session_state.student_profile,
        "target_job_name": None,
        "job_profile": None,
        "match_result": None,
        "next_step": "agent"
    }

def get_student_profile_from_api(session_id: str) -> Optional[Dict]:
    """从 API 获取学生画像"""
    try:
        response = requests.get(f"{API_BASE_URL}/profile/student", params={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            return data.get('student_profile')
    except Exception as e:
        st.error(f"获取学生画像失败：{str(e)}")
    return None

def get_job_profile_from_api(session_id: str) -> Optional[Dict]:
    """从 API 获取岗位画像"""
    try:
        response = requests.get(f"{API_BASE_URL}/profile/job", params={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            return data.get('job_profile')
    except Exception as e:
        st.error(f"获取岗位画像失败：{str(e)}")
    return None

def get_match_result_from_api(session_id: str) -> Optional[Dict]:
    """从 API 获取匹配结果"""
    try:
        response = requests.get(f"{API_BASE_URL}/match/result", params={"session_id": session_id})
        if response.status_code == 200:
            data = response.json()
            return data.get('match_result')
    except Exception as e:
        st.error(f"获取匹配结果失败：{str(e)}")
    return None

def analyze_job_from_api(job_name: str, session_id: str, job_description: str = "") -> Optional[Dict]:
    """从 API 分析岗位"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/job/analyze",
            json={"job_name": job_name, "job_description": job_description},
            params={"session_id": session_id}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data
    except Exception as e:
        st.error(f"分析岗位失败：{str(e)}")
    return None


def run_agent_step_stream(prompt: str, placeholder, session_id: Optional[str] = None):
    """流式运行智能体，实时显示思考过程和回答"""
    try:
        # 调用后端流式 API
        response = requests.post(
            f"{API_BASE_URL}/chat/stream",
            json={"message": prompt, "session_id": session_id},
            stream=True,
            timeout=120
        )

        reasoning_buffer = ""
        answer_buffer = ""
        tool_calls = []
        final_answer = ""
        display_content = ""

        with placeholder.container():
            status_area = st.empty()
            content_area = st.empty()
            tool_area = st.empty()

            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8'))
                        event_type = event.get('type', 'unknown')

                        if event_type == 'reasoning':
                            reasoning_buffer += event.get('content', '')
                            status_area.markdown(f"🤔 **思考中...**")
                        elif event_type == 'answer':
                            answer_buffer += event.get('content', '')
                            display_content = remove_emojis(answer_buffer)
                            content_area.markdown(f"💬 **正在回复...**\n\n{display_content}")
                        elif event_type == 'tool_call':
                            tool_name = event.get('name', '')
                            tool_args = event.get('args', {})
                            tool_calls.append({'name': tool_name, 'args': tool_args})
                            tools_display = "\n\n".join([
                                f"""<div class="tool-block">
                                    🔧 <strong>调用工具:</strong> {t['name']}<br>
                                    <small>参数：{json.dumps(t['args'], ensure_ascii=False)[:100]}...</small>
                                </div>"""
                                for t in tool_calls
                            ])
                            tool_area.markdown(tools_display, unsafe_allow_html=True)
                        elif event_type == 'tool_result':
                            tool_name = event.get('name', '')
                            tool_result = str(event.get('result', ''))[:200]
                            tools_display = f"""<div class="tool-block">
                                📊 <strong>{tool_name} 返回:</strong><br>
                                <small>{tool_result}...</small>
                            </div>"""
                            tool_area.markdown(tools_display, unsafe_allow_html=True)
                        elif event_type == 'final_answer':
                            final_answer = event.get('content', '')
                            display_content = remove_emojis(final_answer)
                            content_area.markdown(f"✅ **回答完成:**\n\n{display_content}")
                            status_area.markdown("✅ 完成")

                    except json.JSONDecodeError:
                        pass

        # 更新会话状态：从独立 API 获取画像和匹配结果
        if session_id:
            try:
                # 获取学生画像
                profile_resp = requests.get(f"{API_BASE_URL}/profile/student", params={"session_id": session_id})
                if profile_resp.status_code == 200:
                    data = profile_resp.json()
                    if data.get('student_profile'):
                        st.session_state.student_profile = data['student_profile']

                # 获取岗位画像
                job_resp = requests.get(f"{API_BASE_URL}/profile/job", params={"session_id": session_id})
                if job_resp.status_code == 200:
                    data = job_resp.json()
                    if data.get('job_profile'):
                        st.session_state.job_profile = data['job_profile']

                # 获取匹配结果
                match_resp = requests.get(f"{API_BASE_URL}/match/result", params={"session_id": session_id})
                if match_resp.status_code == 200:
                    data = match_resp.json()
                    if data.get('match_result'):
                        st.session_state.match_result = data['match_result']
            except Exception as e:
                print(f"[WARN] 获取画像/匹配结果失败：{e}")

        # 更新会话状态
        if final_answer:
            return final_answer
        return answer_buffer if answer_buffer else reasoning_buffer

    except requests.exceptions.RequestException as e:
        st.error(f"API 请求失败：{str(e)}")
        return "抱歉，连接后端服务失败，请稍后重试。"
    except Exception as e:
        st.error(f"执行出错：{str(e)}")
        return "抱歉，处理过程中出现错误，请重试。"

def run_agent_step(user_message: str):
    """运行智能体一步（本地模式，备用）"""
    # 惰性导入，避免页面加载时触发 RAG 初始化
    from main_agent.workflow import create_workflow
    from langchain_core.messages import HumanMessage

    app = get_or_create_workflow()

    # 初始化或更新状态
    if st.session_state.agent_state is None:
        reset_agent_state()

    # 添加用户消息到状态
    st.session_state.agent_state["messages"].append(HumanMessage(content=user_message))

    # 运行工作流
    responses = []
    try:
        for output in app.stream(st.session_state.agent_state, config={"recursion_limit": 50}):
            for node_name, state_update in output.items():
                # 更新状态
                if "student_profile" in state_update:
                    st.session_state.student_profile = state_update["student_profile"]
                    st.session_state.agent_state["student_profile"] = state_update["student_profile"]

                if "job_profile" in state_update:
                    st.session_state.job_profile = state_update["job_profile"]
                    st.session_state.agent_state["job_profile"] = state_update["job_profile"]

                if "match_result" in state_update:
                    st.session_state.match_result = state_update["match_result"]
                    st.session_state.agent_state["match_result"] = state_update["match_result"]

                if "messages" in state_update:
                    last_msg = state_update["messages"][-1]
                    # 移除 emoji 以便显示
                    content = remove_emojis(last_msg.content)
                    responses.append(content)

                # 更新整个状态
                st.session_state.agent_state.update(state_update)

    except Exception as e:
        st.error(f"执行出错：{str(e)}")
        return "抱歉，处理过程中出现错误，请重试。"

    return "\n".join(responses) if responses else "抱歉，我没有理解您的问题。"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("🎯 职业规划智能体")
    st.markdown("---")

    # 简历上传区域
    st.subheader("📄 上传简历")
    uploaded_file = st.file_uploader(
        "支持 .txt, .docx, .pdf 格式",
        type=["txt", "docx", "pdf"],
        help="上传简历后，系统会自动提取您的能力画像"
    )

    if uploaded_file:
        if st.session_state.resume_text is None:
            with st.spinner("正在上传简历..."):
                # 调用后端 API 上传简历
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.resume_text = True  # 只需标记已上传，不需要保存文本
                        st.session_state.backend_session_id = data.get('session_id')

                        st.success("✅ 简历上传完成！")
                        st.info("💡 请点击侧边栏的 '👤 获取学生画像' 按钮查看您的能力画像，或输入岗位名称进行岗位分析！")
                    else:
                        st.error(f"上传失败：{response.status_code}")
                except Exception as e:
                    st.error(f"上传失败：{str(e)}")
        else:
            st.success("✅ 简历已上传")
            if st.button("🔄 重新上传"):
                st.session_state.resume_text = None
                st.session_state.student_profile = None
                st.session_state.agent_state = None
                st.rerun()

    # 状态显示
    st.markdown("---")
    st.subheader("📊 当前状态")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.resume_text:
            st.markdown("📝 简历：✅")
        else:
            st.markdown("📝 简历：❌")

    with col2:
        if st.session_state.student_profile:
            st.markdown("👤 画像：✅")
        else:
            st.markdown("👤 画像：⏳")

    if st.session_state.job_profile:
        st.markdown("💼 岗位画像：✅")

    if st.session_state.match_result:
        st.markdown("📈 匹配结果：✅")

    # 操作按钮
    st.markdown("---")
    st.subheader("🔧 操作")

    # 获取学生画像按钮
    if st.session_state.backend_session_id:
        if st.button("👤 获取学生画像", use_container_width=True):
            with st.spinner("正在获取学生画像..."):
                profile = get_student_profile_from_api(st.session_state.backend_session_id)
                if profile:
                    st.session_state.student_profile = profile
                    st.success("✅ 学生画像获取成功!")
                    # 显示画像摘要
                    skills = profile.get('skills', [])
                    if skills:
                        st.markdown(f"**提取到 {len(skills)} 项技能:**")
                        for skill in skills[:5]:
                            st.markdown(f"- {skill.get('name')}")
                else:
                    st.warning("⚠️ 未获取到学生画像，请先上传简历")

        st.markdown("---")

        # 岗位分析区域
        st.markdown("### 💼 岗位分析")
        job_name = st.text_input("岗位名称", placeholder="例如：Java 开发工程师")
        job_desc = st.text_area("岗位描述（可选）", placeholder="请输入岗位职责和要求...")

        if st.button("🔍 分析岗位", use_container_width=True):
            if not job_name:
                st.warning("请输入岗位名称")
            else:
                with st.spinner("正在分析岗位..."):
                    result = analyze_job_from_api(job_name, st.session_state.backend_session_id, job_desc)
                    if result and result.get('success'):
                        st.success("✅ 岗位分析完成!")
                        if result.get('job_profile'):
                            st.session_state.job_profile = result['job_profile']
                            st.markdown(f"**岗位名称:** {result['job_profile'].get('name', 'N/A')}")
                        if result.get('match_result'):
                            st.session_state.match_result = result['match_result']
                            summary = result['match_result'].get('summary', {})
                            st.markdown(f"**匹配度:** {summary.get('matching_degree', 'N/A')}")
                    else:
                        st.error("❌ 岗位分析失败，请重试")

        st.markdown("---")

        # 查看详情按钮
        st.markdown("#### 📋 查看详情")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👤 学生画像", use_container_width=True,
                         disabled=not st.session_state.get('student_profile')):
                st.session_state.show_student_profile = True
                st.rerun()
        with col2:
            if st.button("💼 岗位画像", use_container_width=True,
                         disabled=not st.session_state.get('job_profile')):
                st.session_state.show_job_profile = True
                st.rerun()
        with col3:
            if st.button("📊 匹配结果", use_container_width=True,
                         disabled=not st.session_state.get('match_result')):
                st.session_state.show_match_result = True
                st.rerun()

        st.markdown("---")

        # 手动刷新画像和匹配结果按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 刷新画像", use_container_width=True):
                with st.spinner("正在获取岗位画像..."):
                    profile = get_job_profile_from_api(st.session_state.backend_session_id)
                    if profile:
                        st.session_state.job_profile = profile
                        st.success("✅ 获取成功!")
                    else:
                        st.warning("⚠️ 暂无岗位画像")

        with col2:
            if st.button("📊 刷新匹配", use_container_width=True):
                with st.spinner("正在获取匹配结果..."):
                    result = get_match_result_from_api(st.session_state.backend_session_id)
                    if result:
                        st.session_state.match_result = result
                        st.success("✅ 获取成功!")
                    else:
                        st.warning("⚠️ 暂无匹配结果")

        if st.button("🗑️ 清除所有对话", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent_state = None
            st.session_state.job_profile = None
            st.session_state.match_result = None
            st.rerun()

# ==================== 主界面 ====================
st.title("🎯 职业规划智能体")

# 欢迎信息
if not st.session_state.messages:
    st.markdown("""
    ### 👋 欢迎使用职业规划智能体!

    我可以帮您:
    - 📄 **分析简历**: 上传简历后，我会自动提取您的技能和能力
    - 💼 **岗位匹配**: 告诉您与目标岗位的匹配度和差距
    - 📈 **职业规划**: 根据您的情况给出发展建议和学习路径

    **请先上传简历，然后告诉我您想申请的岗位!**
    """)

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==================== 聊天输入 ====================
if prompt := st.chat_input("请输入您的问题，例如：'我想申请 Java 开发工程师岗位'..."):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 运行智能体（流式输出模式）
    with st.chat_message("assistant"):
        placeholder = st.empty()
        # 使用后端 session_id（如果有）
        session_id = st.session_state.get('backend_session_id', None)
        response = run_agent_step_stream(prompt, placeholder, session_id)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ==================== 匹配结果展示 ====================
if st.session_state.match_result:
    st.markdown("---")
    st.subheader("📊 匹配分析结果")

    match_data = st.session_state.match_result

    # 显示匹配度
    if "summary" in match_data:
        summary = match_data["summary"]
        matching_degree = summary.get("matching_degree", "未知")

        # 根据匹配度显示不同颜色
        degree_emoji = {"高": "✅", "中": "⚠️", "低": "❌"}.get(matching_degree, "❓")
        st.markdown(f"### 匹配度：{degree_emoji} {matching_degree}")

        if "summary" in summary:
            st.markdown(f"**总体评价**: {summary['summary']}")

    # 显示技能匹配情况
    if "skills" in match_data:
        st.markdown("#### 技能匹配")
        for skill in match_data["skills"]:
            status_emoji = "✅" if skill.get("status") == "具备" else "❌"
            st.markdown(f"- {status_emoji} **{skill.get('name')}**: {skill.get('evidence', 'N/A')[:100]}...")

    # 显示发展建议
    if st.session_state.job_profile and "paths" in st.session_state.job_profile:
        st.markdown("---")
        st.subheader("🚀 职业发展路径建议")
        for path_info in st.session_state.job_profile["paths"]:
            with st.expander(f"📍 {path_info.get('path', '发展路径')}"):
                st.markdown(path_info.get('requisitions', '暂无详细说明'))


# ==================== 详情弹窗 ====================
# 学生画像详情
if st.session_state.get('show_student_profile') and st.session_state.student_profile:
    with st.sidebar:
        st.markdown("### 👤 学生画像详情")
        profile = st.session_state.student_profile

        # 技能
        st.markdown("#### 技能")
        skills = profile.get('skills', [])
        for skill in skills:
            st.markdown(f"- **{skill.get('name')}**: {skill.get('evidence', '')[:80]}...")

        # 项目/工作经历
        st.markdown("#### 经历")
        for exp in profile.get('Experience', []):
            st.markdown(f"- **{exp.get('name')}**")
            st.markdown(f"  {exp.get('evidence', '')[:100]}...")

        # 专业素养
        st.markdown("#### 专业素养")
        professionalism = profile.get('Professionalism', {})
        st.markdown(f"- 等级：{professionalism.get('level', 'N/A')}")

        # 潜力
        st.markdown("#### 潜力")
        potential = profile.get('Potential', {})
        st.markdown(f"- 等级：{potential.get('level', 'N/A')}")

        if st.button("关闭", key="close_student_profile"):
            st.session_state.show_student_profile = False
            st.rerun()

# 岗位画像详情
if st.session_state.get('show_job_profile') and st.session_state.job_profile:
    with st.sidebar:
        st.markdown("### 💼 岗位画像详情")
        profile = st.session_state.job_profile

        st.markdown(f"**岗位名称**: {profile.get('name', 'N/A')}")
        st.markdown(f"**岗位描述**: {profile.get('summary', 'N/A')[:200]}...")

        # 技能要求
        st.markdown("#### 技能要求")
        for skill in profile.get('skills', []):
            st.markdown(f"- **{skill.get('name')}**")

        # 门槛要求
        st.markdown("#### 门槛要求")
        for threshold in profile.get('thresholds', []):
            st.markdown(f"- **{threshold.get('name')}**")

        # 专业素养
        st.markdown("#### 专业素养")
        for prof in profile.get('professionalism', []):
            st.markdown(f"- {prof.get('name')}")

        # 发展路径
        st.markdown("#### 发展路径")
        for path in profile.get('paths', []):
            st.markdown(f"- {path.get('path', '')}")

        if st.button("关闭", key="close_job_profile"):
            st.session_state.show_job_profile = False
            st.rerun()

# 匹配结果详情
if st.session_state.get('show_match_result') and st.session_state.match_result:
    with st.sidebar:
        st.markdown("### 📊 匹配结果详情")
        match_data = st.session_state.match_result

        # 匹配度
        summary = match_data.get('summary', {})
        matching_degree = summary.get('matching_degree', '未知')
        degree_emoji = {"高": "✅", "中": "⚠️", "低": "❌"}.get(matching_degree, "❓")
        st.markdown(f"### 匹配度：{degree_emoji} {matching_degree}")
        st.markdown(f"**总体评价**: {summary.get('summary', 'N/A')[:200]}...")

        # 技能匹配
        st.markdown("#### 技能匹配")
        for skill in match_data.get('skills', []):
            status = "✅" if skill.get('status') == '具备' else "❌"
            st.markdown(f"{status} **{skill.get('name')}**")

        # 门槛要求
        st.markdown("#### 门槛要求")
        for threshold in match_data.get('thresholds', []):
            status = "✅" if threshold.get('status') == '具备' else "❌"
            st.markdown(f"{status} **{threshold.get('name')}**")

        # 专业素养
        st.markdown("#### 专业素养")
        for prof in match_data.get('professionalism', []):
            status = "✅" if prof.get('status') == '具备' else "❌"
            st.markdown(f"{status} {prof.get('name')}")

        if st.button("关闭", key="close_match_result"):
            st.session_state.show_match_result = False
            st.rerun()
