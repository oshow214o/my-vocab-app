import streamlit as st
import json
import os
from datetime import date

# 오늘 날짜
today = date.today()
day = today.day
month = today.month

# 파일 이름 (예: monthly_words(5).json)
filename = f"words/monthly_words({month}).json"

st.set_page_config(page_title="오늘의 영어 단어 학습")
st.title("📘 오늘의 영어 단어 학습")
st.markdown(f"📅 날짜: **{today.strftime('%Y-%m-%d')}**")
st.write("토익 700점 목표! 매일 20개의 핵심 단어를 학습해보세요.")

if st.button("🚀 오늘의 단어 학습 시작하기"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            all_words = json.load(f)

        # 오늘 날짜에 해당하는 day 필드만 필터링
        today_words = [w for w in all_words if w["day"] == day]

        if not today_words:
            st.warning(f"{day}일에 해당하는 단어가 아직 준비되지 않았습니다.")
        else:
            st.subheader(f"📚 {day}일차 단어 학습")
            for i, word in enumerate(today_words, 1):
                st.markdown(f"""
                ### {i}. **{word['word']}** ({word['part_of_speech']})
                - 뜻: {word['meaning']}
                - IPA: `{word['ipa']}` / 한국식 발음: {word['korean_pronunciation']}
                - 동사 활용형: {word['verb_forms']}
                - 예문: _{word['example']}_
                - 해석: {word['example_translation']}
                - 예문 발음: {word['example_korean_pronunciation']}
                """)
    except FileNotFoundError:
        st.error(f"❌ `{filename}` 파일이 없습니다. 올바른 JSON 파일이 words 폴더에 있는지 확인해 주세요.")
