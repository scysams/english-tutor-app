import streamlit as st

st.title("LinguaFlow AI 測試版 🎤")
st.write("你好！這是我用 Python 搭建的第一個英文教學網站。")

# 簡單的互動區
user_input = st.text_input("試著輸入一句英文：")
if user_input:
    st.success(f"你輸入了：{user_input}")
    st.info("AI 功能尚未連接 API Key，但網站已經上線了！")
