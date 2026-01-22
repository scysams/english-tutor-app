import streamlit as st
from openai import OpenAI

# 1. 頁面基礎設定
st.set_page_config(page_title="LinguaFlow AI", page_icon="🎓")

st.title("LinguaFlow AI: Adaptive English Tutor")
st.markdown("Your personal AI tutor that adapts to your speaking level.")

# 2. 側邊欄：設定與 API Key
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 這是最簡單的 API Key 處理方式：讓用戶自己輸入
    # 如果是你自己用，這很安全，因為 Streamlit 不會儲存它
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    
    st.divider()
    
    # 選擇難度與場景
    user_level = st.selectbox("Your Current Level", ["Beginner (A1-A2)", "Intermediate (B1-B2)", "Advanced (C1-C2)"])
    scenario = st.selectbox("Choose Scenario", [
        "Ordering Coffee", 
        "Job Interview", 
        "Making Friends at a Party", 
        "Checking into a Hotel",
        "Debating AI Ethics"
    ])
    
    st.info(f"Current Mode: **{scenario}**")
    
    if st.button("Clear Chat / Restart"):
        st.session_state.messages = []
        st.rerun()

# 3. 初始化 Session State (記憶體)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 處理用戶輸入
if user_input := st.chat_input("Type your response here..."):
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to start.")
        st.stop()

    # 顯示用戶的訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 6. 建構 System Prompt (核心教學邏輯)
    system_prompt = f"""
    Role: Adaptive English Tutor.
    Current User Level: {user_level}
    Scenario: {scenario}

    Logic:
    1. If user makes mistakes -> Gently correct (Implicit Recasting) and lower difficulty.
    2. If user is fluent -> Increase difficulty, use idioms, ask 'Why'.
    3. Keep responses concise (1-3 sentences).
    4. Stay in character as a partner in the scenario.
    """

    # 準備發送給 OpenAI 的訊息列表
    # 我們把 system prompt 放在最前面，然後接上歷史對話
    full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # 7. 呼叫 AI (串流顯示效果)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model="gpt-4o", # 建議使用 gpt-4o 或 gpt-3.5-turbo
                messages=full_messages,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Sorry, I encountered an error. Please check your API Key."

    # 記錄 AI 的回應
    st.session_state.messages.append({"role": "assistant", "content": full_response})
