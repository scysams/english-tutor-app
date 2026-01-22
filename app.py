import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="LinguaFlow AI", page_icon="🗣️")
st.title("LinguaFlow AI: Any Topic English Tutor")

# --- 1. API Key 設定 (保持不變) ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except FileNotFoundError:
    st.error("請在 Streamlit 後台設定 Secrets: OPENAI_API_KEY")
    st.stop()

# --- 2. 側邊欄：強化的主題選擇功能 ---
with st.sidebar:
    st.header("⚙️ 設定 (Settings)")
    
    user_level = st.selectbox("你的英文程度", ["Beginner (A1-A2)", "Intermediate (B1-B2)", "Advanced (C1-C2)"])
    
    st.divider()
    
    # [修改重點 A]：增加模式選擇
    mode = st.radio(
        "選擇練習模式 (Choose Mode)",
        ["預設場景 (Presets)", "自訂主題 (Custom Topic)", "自由對話 (Free Chat)"]
    )
    
    final_scenario = "" # 這是我們要傳給 AI 的最終主題
    
    if mode == "預設場景 (Presets)":
        # 顯示原本的選單
        selected_preset = st.selectbox("選擇場景", [
            "Ordering Coffee", 
            "Job Interview", 
            "Making Friends", 
            "Travel Help",
            "Debating AI Ethics"
        ])
        final_scenario = selected_preset
        
    elif mode == "自訂主題 (Custom Topic)":
        # [修改重點 B]：顯示文字輸入框讓學生自己打
        custom_topic = st.text_input("輸入你想聊的主題 (例如: Harry Potter, Basketball...)", "My favorite movie")
        final_scenario = custom_topic
        
    else: # 自由對話
        final_scenario = "Free Conversation (No specific topic, just chat naturally)"
    
    st.info(f"當前模式: **{final_scenario}**")
    
    if st.button("重新開始 (Restart)"):
        st.session_state.messages = []
        st.rerun()

# --- 3. 初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # 根據不同模式，AI 的第一句話要有變化
    if mode == "自由對話 (Free Chat)":
        greeting = f"Hi! I'm your English tutor. We can talk about anything. How is your day?"
    else:
        greeting = f"Hi! I'm ready to practice '{final_scenario}' with you. I'll adjust to {user_level} level."
        
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# --- 4. 顯示對話 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. 處理輸入與 Prompt ---
if user_input := st.chat_input("Type here..."):

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # [修改重點 C]：根據模式調整 Prompt
    # 這裡的邏輯告訴 AI：如果是自由對話，就不要扮演特定角色，而是當一個朋友
    role_instruction = ""
    if mode == "自由對話 (Free Chat)":
        role_instruction = "You are a friendly casual chat partner. Discuss whatever the user wants."
    else:
        role_instruction = f"Roleplay scenario: {final_scenario}. Stay in character."

    system_prompt = f"""
    You are an Adaptive English Tutor.
    Current User Level: {user_level}
    {role_instruction}
    
    Key Rules:
    1. If user makes mistakes -> Gently correct them (Implicit Recasting).
    2. Keep responses concise (1-3 sentences) to encourage conversation.
    3. If the user changes the topic, follow them naturally.
    """

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
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

    st.session_state.messages.append({"role": "assistant", "content": full_response})
