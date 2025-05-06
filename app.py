# app.py

import streamlit as st
from datetime import date

st.set_page_config(page_title="영어 단어 학습", layout="centered")

# 오늘 날짜
today = date.today().strftime("%Y-%m-%d")

# 제목
st.title("📘 오늘의 영어 단어 학습")
st.markdown(f"📅 날짜: **{today}**")

# 설명
st.write("""
토익 700점 목표!
매일 20개의 핵심 단어를 학습해보세요.
""")

# 시작 버튼
if st.button("🚀 오늘의 단어 학습 시작하기"):
    st.success("단어 학습 화면으로 이동합니다 (추후 구현 예정)")

# 하단 정보
st.markdown("---")
st.caption("개발: 나만의 영어 GPT 앱")

