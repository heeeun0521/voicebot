# 필요한 패키지 불러오기
import os  # 파일 삭제용
import base64  # 음원 파일 인코딩
import streamlit as st  # 웹 UI
from datetime import datetime  # 시간 표시용
from gtts import gTTS  # 텍스트 → 음성 변환
import openai  # OpenAI API 사용

##### 기능 구현 함수 #####

# STT: Whisper API (음성 → 텍스트)
def STT(audio_file, api_key):
    client = openai.OpenAI(api_key=api_key)  # OpenAI 클라이언트 생성
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcript.text  # 인식된 텍스트 반환

# GPT: 텍스트 질문(prompt) → GPT 응답 생성
def ask_gpt(prompt, model, api_key):
    client = openai.OpenAI(api_key=api_key)  # OpenAI 클라이언트 생성
    response = client.chat.completions.create(
        model=model,  # gpt-3.5-turbo 또는 gpt-4
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content  # GPT 응답 텍스트 반환

# TTS: 텍스트 → 음성 파일 생성 및 자동 재생
def TTS(response_text):
    filename = "output.mp3"  # 임시 파일명 지정
    tts = gTTS(text=response_text, lang="ko")  # 텍스트를 한국어 음성으로 변환
    tts.save(filename)  # mp3 파일로 저장

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()  # base64로 인코딩

    md = f"""
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)  # HTML 오디오 태그 출력
    os.remove(filename)  # 재생 후 mp3 파일 삭제

##### 메인 함수 #####

def main():
    st.set_page_config(page_title="음성 비서 프로그램", layout="wide")
    st.header("음성 비서 프로그램")
    st.markdown("---")

    # 프로그램 설명 출력
    with st.expander("프로그램 설명", expanded=True):
        st.write("""
        - STT: OpenAI Whisper API 사용 (음성 → 텍스트)
        - GPT: OpenAI GPT 모델로 답변 생성
        - TTS: gTTS 사용 (답변 → 음성)
        - UI: Streamlit 사용
        """)

    st.markdown("---")

    # 사이드바: API 키 입력 / 모델 선택 / 초기화
    with st.sidebar:
        st.session_state["OPENAI_API"] = st.text_input("OpenAI API 키", type="password")
        model = st.radio("GPT 모델 선택", ["gpt-4", "gpt-3.5-turbo"])
        if st.button("초기화"):
            st.session_state["chat"] = []

    # 채팅 세션 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    # 좌우 컬럼 구성
    col1, col2 = st.columns(2)

    # 왼쪽: 음성 파일 업로드 및 질문 처리
    with col1:
        st.subheader("질문하기")
        uploaded_file = st.file_uploader("음성 파일 업로드 (mp3)", type=["mp3"])

        if uploaded_file and st.session_state["OPENAI_API"]:
            # 음성 인식 처리
            with st.spinner("음성 인식 중..."):
                user_input = STT(uploaded_file, st.session_state["OPENAI_API"])
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"].append(("user", now, user_input))

            # GPT 응답 처리
            with st.spinner("GPT 답변 생성 중..."):
                response = ask_gpt(user_input, model, st.session_state["OPENAI_API"])
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"].append(("bot", now, response))
                TTS(response)  # 음성 출력

    # 오른쪽: 채팅 히스토리 출력
    with col2:
        st.subheader("질문/답변")
        for sender, time, message in st.session_state["chat"]:
            if sender == "user":
                # 사용자 메시지 말풍선 (왼쪽 정렬)
                st.write(f"""
                    <div style="display:flex; align-items:center; margin-bottom:8px;">
                        <div style="background-color:#007AFF; color:white; border-radius:12px;
                                    padding:8px 12px; max-width:70%;">
                            {message}
                        </div>
                        <div style="font-size:0.8rem; color:gray; margin-left:8px;">{time}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # GPT 응답 말풍선 (오른쪽 정렬)
                st.write(f"""
                    <div style="display:flex; justify-content:flex-end; align-items:center; margin-bottom:8px;">
                        <div style="font-size:0.8rem; color:gray; margin-right:8px;">{time}</div>
                        <div style="background-color:#E5E5EA; color:black; border-radius:12px;
                                    padding:8px 12px; max-width:70%;">
                            {message}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# 프로그램 실행 시작점
if __name__ == "__main__":
    main()

    