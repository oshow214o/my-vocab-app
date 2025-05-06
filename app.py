import streamlit as st
import json
import base64
import os
import random
from gtts import gTTS
from pathlib import Path
from datetime import datetime
import calendar
from PIL import Image

# ===================== [1] 경로 및 데이터 로딩 설정 =====================
data_path = Path("data/monthly_words(5).json")
history_path = Path("history/history.json")
history_path.parent.mkdir(parents=True, exist_ok=True)

# ===================== [2] 학습 이력 불러오기 및 저장 =====================
def load_history():
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(day_key, score, total):
    history = load_history()
    history[day_key] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": score,
        "total": total
    }
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ===================== [3] 달력 형태 학습 이력 표시 =====================
def render_learning_calendar():
    st.markdown("## 📆 학습 달력 보기")

    # [1] 현재 연/월을 세션에 저장하여 유지
    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = datetime.today().year
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = datetime.today().month

    # [2] 월 이동 버튼 (좌우 화살표)
    col_prev, col_label, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("⬅️ 이전 달"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
    with col_next:
        if st.button("➡️ 다음 달"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1

    year = st.session_state.calendar_year
    month = st.session_state.calendar_month
    month_name = datetime(year, month, 1).strftime("%B")

    # [3] 학습 이력 불러오기
    history_path = Path("history/history.json")
    completed_data = {}
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            completed_data = {
                v["date"]: {
                    "score": v["score"],
                    "total": v["total"],
                    "day": k
                } for k, v in raw.items()
            }

    # [4] 달력 날짜 생성
    cal = calendar.Calendar()
    month_days = list(cal.itermonthdates(year, month))

    st.markdown(f"### <span style='color:#6C63FF'>{month_name} {year}</span>", unsafe_allow_html=True)

    # [5] 요일 표시
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    cols = st.columns(7)
    for i in range(7):
        cols[i].markdown(f"**{weekdays[i]}**", unsafe_allow_html=True)

    # [6] 날짜 셀 출력
    for i in range(0, len(month_days), 7):
        week = month_days[i:i + 7]
        cols = st.columns(7)
        for j, day in enumerate(week):
            if day.month != month:
                cols[j].markdown(" ")
                continue

            date_str = day.strftime("%Y-%m-%d")
            label = f"<div style='border:1px solid #ddd; border-radius:6px; padding:10px; text-align:center;'>"
            label += f"<b>{day.day}</b><br>"

            if date_str in completed_data:
                data = completed_data[date_str]
                day_num = data["day"].split("_")[1]
                label += f"<span style='color:green;'>✅ Day {day_num}<br>{data['score']}/{data['total']}</span>"
            else:
                label += "<span style='color:#aaa;'>-</span>"

            label += "</div>"
            cols[j].markdown(label, unsafe_allow_html=True)

# ===================== [4] TTS 발음 재생 함수 =====================
def tts_play_autoplay(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    temp_path = "temp.mp3"
    tts.save(temp_path)
    with open(temp_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    audio_html = f'''
        <audio autoplay="true" style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)
    os.remove(temp_path)

# ===================== [5] 산리오 캐릭터 이미지 랜덤 불러오기 =====================
def get_two_character_images():
    all_imgs = [f for f in os.listdir("data") if f.endswith((".png", ".jpg")) and f != "background.png"]
    selected = random.sample(all_imgs, 2) if len(all_imgs) >= 2 else all_imgs * 2
    return os.path.join("data", selected[0]), os.path.join("data", selected[1])

left_img_path, right_img_path = get_two_character_images()

# ===================== [6] 헤더 UI 출력 =====================
col_l, col_center, col_r = st.columns([1, 3, 1])
with col_l:
    st.image(Image.open(left_img_path), width=150)
with col_center:
    st.markdown("<h1 style='text-align:center; color:#6C63FF;'>💜 영어 단어 학습 앱 💜</h1>", unsafe_allow_html=True)
with col_r:
    st.image(Image.open(right_img_path), width=150)

# ===================== [7] 사이드바 달력 보기 기능 =====================
st.sidebar.markdown("## 📆 학습 이력")
show_calendar = st.sidebar.checkbox("📅 학습 달력 보기", value=False)
if show_calendar:
    render_learning_calendar()
    st.stop()
# ===================== [8] 자동 이어 학습 Day 설정 =====================
history = load_history()
completed_days = sorted([int(k.split("_")[1]) for k in history.keys()])
default_day = max(completed_days + [0]) + 1 if len(completed_days) < 30 else 1
# ✅ [자동 이어 학습 Day 설정] - 보기 좋게 "2일차!" 형태로
day_options = [f"{i}일차!" for i in range(1, 31)]
day_labels = {f"{i}일차!": i for i in range(1, 31)}
default_label = f"{default_day}일차!"

day_label = st.selectbox("🎯 학습할 Day를 선택하세요", day_options, index=default_day - 1)
day_num = day_labels[day_label]
day_key = f"day_{day_num}"

# ===================== [9] 세션 상태 초기화 =====================
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "wrong_words" not in st.session_state:
    st.session_state.wrong_words = []

# ===================== [10] 제출 처리 함수 =====================
def on_submit():
    st.session_state.submitted = True

# ===================== [11] 단어 데이터 로딩 =====================
if not data_path.exists():
    st.error("❌ 단어 데이터 파일이 없습니다. data/monthly_words.json 확인.")
else:
    with open(data_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    if day_key not in all_data:
        st.warning(f"⚠️ {day_key} 데이터가 없습니다.")
    else:
        words = all_data[day_key]
        total = len(words)
        idx = st.session_state.current_index
        if idx >= total:
            st.success("🎉 오늘의 단어를 모두 완료했습니다!")
            st.markdown(f"🟣 총 점수: **{st.session_state.score} / {total}**")
            wrong_set = list(dict.fromkeys(st.session_state.wrong_words))
            st.markdown(f"💔 오답 단어 수: **{len(wrong_set)} 개**")

            if day_key not in history:
                save_history(day_key, st.session_state.score, total)

            if st.button("🔁 다시 학습하기"):
                st.session_state.current_index = 0
                st.session_state.submitted = False
                st.session_state.score = 0
                st.session_state.wrong_words = []
                if "user_answer" in st.session_state:
                    del st.session_state["user_answer"]
                st.rerun()
        else:
            word = words[idx]
            # 하단: 단어명만 표시 (작은 배경 포함)
            st.markdown(f"""
                <div style='background-color:#f3e5f5; padding:10px; border-radius:10px; margin-bottom:15px;'>
                    <h2 style='text-align:center; font-size:28px; color:#6C63FF;'>{word['word']}</h2>
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_input("뜻 입력:", key="user_answer", on_change=on_submit,
                              label_visibility="collapsed", placeholder="뜻을 입력하고 Enter를 누르세요")
            with col2:
                st.button("🎀 제출", on_click=on_submit)

            if st.session_state.submitted:
                if st.session_state.user_answer.strip() == word["meaning"].strip():
                    st.success("✅ 정답입니다!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ 오답입니다. 정답: {word['meaning']}")
                    st.session_state.wrong_words.append(word['word'])

                with st.expander("📝 정답 해설 보기", expanded=True):
                    st.markdown(f"**뜻:** {word['meaning']} ({word['part_of_speech']})")
                    st.markdown(f"**한글 발음:** {word['korean_pronunciation']}")
                    st.markdown(f"**예문:** {word['example']}")
                    st.markdown(f"**예문 해석:** {word['example_translation']}")
                    st.markdown(f"**예문 한글 발음:** {word['example_korean_pronunciation']}")
                    if word["part_of_speech"] == "verb":
                        st.markdown(f"**동사 변화:** {word['verb_forms'].get('past', '')} / {word['verb_forms'].get('future', '')}")
                    st.text_area("✍️ 예문 따라 쓰기:", key=f"writing_{idx}", height=80,
                                 placeholder=word["example"], label_visibility="collapsed")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📢 단어 발음 듣기", key=f"word_audio_{idx}"):
                            tts_play_autoplay(word["word"])
                    with col_b:
                        if st.button("📢 예문 발음 듣기", key=f"ex_audio_{idx}"):
                            tts_play_autoplay(word["example"])

                col_prev, col_next = st.columns(2)
                with col_prev:
                    if st.button("⬅ 이전 단어"):
                        st.session_state.current_index -= 1
                        st.session_state.submitted = False
                        if "user_answer" in st.session_state:
                            del st.session_state["user_answer"]
                        st.rerun()
                with col_next:
                    if st.button("➡ 다음 단어"):
                        st.session_state.current_index += 1
                        st.session_state.submitted = False
                        if "user_answer" in st.session_state:
                            del st.session_state["user_answer"]
                        st.rerun()

            st.markdown(f"📊 <b>진도율:</b> {idx + 1} / {total}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
