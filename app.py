import streamlit as st
from openai import OpenAI
import os

# 1. 頁面基礎設定
st.set_page_config(page_title="LinguaFlow AI", page_icon="🎓")
st.title("LinguaFlow AI: Adaptive English Tutor")
st.markdown("Your personal AI tutor. Just type/speak to start!")

# 2. 自動獲取 API Key (從 Secrets)
# 這裡會嘗試從 Streamlit Secrets 讀取，如果沒有設定，則會報錯提示
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except FileNotFoundError:
    st.error("請老師在 Streamlit 後台設定 Secrets: OPENAI_API_KEY")
    st.stop()

# 3. 側邊欄：只保留場景設定 (不再顯示 Key 輸入框)
with st.sidebar:
    st.header("⚙️ Settings")
    
    user_level = st.selectbox("Your Level", ["Beginner (A1-A2)", "Intermediate (B1-B2)", "Advanced (C1-C2)"])
    scenario = st.selectbox("Choose Scenario", [
        "Ordering Coffee", 
        "Job Interview", 
        "Making Friends", 
        "Travel Help"
    ])
    
    if st.button("Restart Conversation"):
        st.session_state.messages = []
        st.rerun()

# 4. 初始化記憶體
if "messages" not in st.session_state:
    st.session_state.messages = []
    # AI 先發制人，主動打招呼
    welcome_msg = f"Hi! I am ready to help you practice '{scenario}'. I'll adjust to your {user_level} level."
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# 5. 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 處理用戶輸入
if user_input := st.chat_input("Type here..."):

    # 顯示用戶訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 準備 Prompt
    system_prompt = f"""
    You are an English Tutor. 
    Level: {user_level}. Scenario: {scenario}.
    Rules: 
    - Keep answers short (1-2 sentences).
    - If user makes a grammar mistake, correct it gently inside the reply.
    """

    # 呼叫 AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 直接使用從 Secrets 拿到的 Key
            client = OpenAI(api_key=api_key)
            
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Sorry, connection error."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
