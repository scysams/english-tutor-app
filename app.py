
import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="LinguaFlow (DeepSeek)", page_icon="🇭🇰")
st.title("LinguaFlow: HK Edition")
st.caption("Powered by DeepSeek-V3 - Natively supported in HK")

# --- 1. 獲取 Key ---
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except FileNotFoundError:
    st.error("請在 Secrets 設定 DEEPSEEK_API_KEY")
    st.stop()

# --- 2. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 設定")
    user_level = st.selectbox("你的程度", ["Beginner", "Intermediate", "Advanced"])
    
    # DeepSeek 主要有一個超強模型：DeepSeek-V3 (Chat)
    st.info("Model: DeepSeek-V3 (Smart & Fast)")

    st.divider()
    
    mode = st.radio("模式", ["預設場景", "自由對話"])
    if mode == "預設場景":
        scenario = st.selectbox("場景", ["Ordering Coffee", "Job Interview", "Travel"])
    else:
        scenario = "Free Chat"

    if st.button("重新開始"):
        st.session_state.messages = []
        st.rerun()

# --- 3. 初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hi! I am ready. Let's practice English!"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 處理輸入 ---
if user_input := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prompt (保持原本的教學邏輯)
    system_prompt = f"You are an English Tutor. Level: {user_level}. Scenario: {scenario}. Keep it short."

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 關鍵修改：DeepSeek 設定
            client = OpenAI(
                base_url="https://api.deepseek.com",  # 指向 DeepSeek 官方接口
                api_key=api_key
            )
            
            stream = client.chat.completions.create(
                model="deepseek-chat", # 這是 DeepSeek V3 的模型代碼
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True,
                temperature=1.3 # DeepSeek 建議設高一點比較自然
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Error: {e}")
            st.error("如果顯示餘額不足，請確認 DeepSeek 後台是否有免費額度。")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
