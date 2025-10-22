import streamlit as st

st.set_page_config(page_title="파이 암기 게임", layout="centered", page_icon="🧠")

st.title("🧠 π(파이) 암기 도전!")
st.caption("소수점 아래 숫자를 하나씩 입력하세요. 3번 틀리면 게임이 끝납니다!")

# ---------- 파이 숫자 ----------
PI_DIGITS = "14159265358979323846264338327950288419716939937510"  # 필요시 더 늘릴 수 있음

# ---------- 세션 상태 초기화 ----------
if "index" not in st.session_state:
    st.session_state.index = 0  # 현재 맞춘 자리수
if "lives" not in st.session_state:
    st.session_state.lives = 3  # 남은 기회
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# ---------- 게임 중단 시 ----------
if st.session_state.game_over:
    st.error("💀 게임 종료! 다시 도전해보세요!")
    st.write(f"👉 지금까지 맞춘 자리수: {st.session_state.index}자리")
    if st.button("🔄 다시 시작하기"):
        st.session_state.index = 0
        st.session_state.lives = 3
        st.session_state.game_over = False
        st.experimental_rerun()
else:
    # ---------- 안내 ----------
    st.write(f"✅ 현재까지 맞춘 숫자: `3.{PI_DIGITS[:st.session_state.index]}`")
    st.write(f"❤️ 남은 기회: {st.session_state.lives}번")

    # ---------- 입력 ----------
    user_input = st.text_input("다음 숫자를 입력하세요:", max_chars=1)

    if st.button("확인"):
        if not user_input.isdigit():
            st.warning("숫자를 입력해주세요!")
        else:
            correct_digit = PI_DIGITS[st.session_state.index]
            if user_input == correct_digit:
                st.session_state.index += 1
                st.success("🎯 정답입니다!")
            else:
                st.session_state.lives -= 1
                st.error(f"❌ 틀렸어요! 정답은 {correct_digit} 입니다.")
                if st.session_state.lives <= 0:
                    st.session_state.game_over = True
            st.experimental_rerun()

