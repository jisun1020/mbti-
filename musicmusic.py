# app.py
import streamlit as st
import pandas as pd
import random
from typing import List

st.set_page_config(page_title="MBTI 노래 추천", page_icon="🎧", layout="centered")

st.title("🎵 MBTI별 노래 추천 앱")
st.caption("간단한 데모입니다. 자신만의 곡 CSV를 업로드하면 더 잘 맞는 추천을 받을 수 있어요.")

# -- 샘플 데이터 (CSV 업로드 없을 때 사용) --
SAMPLE_SONGS = [
    {"title": "Blissful Day", "artist": "Daylight Ensemble", "genre": "pop", "mood": 8, "mbti_tags": "ENFP,ESFP,INFP", "preview_url": ""},
    {"title": "Midnight City", "artist": "Synth Harbor", "genre": "electronic", "mood": 4, "mbti_tags": "INTJ,ISTP,INFP", "preview_url": ""},
    {"title": "Coffee & Rain", "artist": "Quiet Corner", "genre": "indie", "mood": 5, "mbti_tags": "INFJ,ISFJ,INTP", "preview_url": ""},
    {"title": "Drive Away", "artist": "Roadtone", "genre": "rock", "mood": 7, "mbti_tags": "ESTP,ENTP,ISTP", "preview_url": ""},
    {"title": "Warm Glow", "artist": "Amber Choir", "genre": "acoustic", "mood": 9, "mbti_tags": "ESFJ,ENFJ,ISFP", "preview_url": ""},
    {"title": "City Lights", "artist": "Nightshift", "genre": "r&b", "mood": 6, "mbti_tags": "ISFP,INFP,ESFP", "preview_url": ""},
    {"title": "Study Focus", "artist": "LoFi Library", "genre": "lofi", "mood": 3, "mbti_tags": "INTJ,ISTJ,INFP", "preview_url": ""},
    {"title": "Epic Horizon", "artist": "Orchestra Nova", "genre": "classical", "mood": 5, "mbti_tags": "INFJ,INTP,INTJ", "preview_url": ""},
    {"title": "Heartbeat", "artist": "Pulse", "genre": "pop", "mood": 8, "mbti_tags": "ENFP,ESFP,ENTP", "preview_url": ""},
    {"title": "Solitude", "artist": "Blue Room", "genre": "indie", "mood": 2, "mbti_tags": "INTP,INFP,ISFP", "preview_url": ""},
    {"title": "Adrenaline", "artist": "Fast Lane", "genre": "electronic", "mood": 9, "mbti_tags": "ESTP,ENTP,ESFP", "preview_url": ""},
    {"title": "Reflection", "artist": "Mirrorlake", "genre": "folk", "mood": 4, "mbti_tags": "INFJ,ISFJ,INFP", "preview_url": ""},
]

# -- 유틸리티 함수 --
def load_songs_from_uploaded(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    # 필수 컬럼 체크 & 정리
    expected = {"title", "artist", "genre", "mood", "mbti_tags"}
    if not expected.issubset(set(df.columns.str.lower())):
        # try case-insensitive mapping
        cols = {c.lower(): c for c in df.columns}
        missing = expected - set(cols.keys())
        if missing:
            raise ValueError(f"CSV에 필요한 열이 없습니다: {missing}. 최소한 title, artist, genre, mood, mbti_tags 필요.")
        # rename
        df = df.rename(columns={cols[k]: k for k in cols})
    # ensure mood numeric 1-10
    df["mood"] = pd.to_numeric(df["mood"], errors="coerce").fillna(5).clip(1,10).astype(int)
    # normalize mbti_tags to uppercase strings
    df["mbti_tags"] = df["mbti_tags"].astype(str).str.upper()
    return df

def prepare_song_df() -> pd.DataFrame:
    uploaded = st.file_uploader("원한다면 노래 CSV 파일 업로드 (옵션)", type=["csv"])
    if uploaded:
        try:
            df = load_songs_from_uploaded(uploaded)
            st.success("CSV 업로드 성공 — 사용자 데이터 사용 중")
            return df
        except Exception as e:
            st.error(f"CSV 로드 에러: {e}. 기본 샘플 데이터 사용합니다.")
    # fallback to sample
    df = pd.DataFrame(SAMPLE_SONGS)
    df["mood"] = pd.to_numeric(df["mood"], errors="coerce").fillna(5).astype(int)
    df["mbti_tags"] = df["mbti_tags"].str.upper()
    return df

def mbti_relevance_score(song_mbti_tags: str, chosen_mbti: str) -> int:
    tags = [t.strip() for t in song_mbti_tags.split(",") if t.strip()]
    return 1 if chosen_mbti.upper() in tags else 0

def recommend_songs(df: pd.DataFrame, chosen_mbti: str, mood_pref: int, genres: List[str], top_n: int, shuffle: bool):
    # 필터 장르
    if genres:
        df_filtered = df[df["genre"].str.lower().isin([g.lower() for g in genres])]
    else:
        df_filtered = df.copy()
    # compute score: MBTI match (primary), mood distance (smaller distance => higher score)
    df_filtered = df_filtered.copy()
    df_filtered["mbti_match"] = df_filtered["mbti_tags"].apply(lambda s: mbti_relevance_score(s, chosen_mbti))
    df_filtered["mood_dist"] = (df_filtered["mood"] - mood_pref).abs()
    # Score: prioritize MBTI match, then lower mood_dist
    # We'll create combined score where higher is better
    df_filtered["score"] = df_filtered["mbti_match"] * 100 - df_filtered["mood_dist"]
    # If none match MBTI, fall back to mood-based sorting
    if df_filtered["mbti_match"].sum() == 0:
        df_filtered["score"] = -df_filtered["mood_dist"]
    # sort
    df_sorted = df_filtered.sort_values(by=["score", "mood"], ascending=[False, False]).reset_index(drop=True)
    if shuffle:
        # shuffle top candidates to add variety but keep ordering by score
        top_chunk = df_sorted.head(50).sample(frac=1, random_state=random.randint(0, 9999))
        rest = df_sorted.tail(max(0, len(df_sorted)-50))
        df_sorted = pd.concat([top_chunk, rest]).reset_index(drop=True)
    return df_sorted.head(top_n)

# -- 앱 UI --
with st.sidebar:
    st.header("설정")
    mbti_list = [
        "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
        "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
    ]
    chosen_mbti = st.selectbox("당신의 MBTI를 선택하세요", mbti_list, index=mbti_list.index("INFP"))
    mood_pref = st.slider("현재 기분(무드) — 낮을수록 차분/우울, 높을수록 활기 (1-10)", min_value=1, max_value=10, value=6)
    top_n = st.number_input("추천 곡 개수", min_value=3, max_value=30, value=8)
    genres_available = sorted({g.lower() for g in pd.DataFrame(SAMPLE_SONGS)["genre"].unique()})
    genres = st.multiselect("원하는 장르(선택시 해당 장르만 추천)", options=genres_available, format_func=lambda x: x.capitalize())
    shuffle = st.checkbox("추천에 무작위성 추가 (같은 설정でも 결과가 바뀔 수 있음)", value=True)
    st.markdown("---")
    st.caption("CSV 업로드 시 다음 칼럼을 권장: title, artist, genre, mood(1-10), mbti_tags(예: ENFP,INFP), preview_url(optional)")

# Load data (uploaded or sample)
df_songs = prepare_song_df()

# Show small preview of dataset
with st.expander("데이터 미리보기 (업로드한 경우)"):
    st.dataframe(df_songs.head(10))

if st.button("추천 시작 🎧"):
    # run recommendation
    recs = recommend_songs(df_songs, chosen_mbti, mood_pref, genres, top_n, shuffle)
    if recs.empty:
        st.warning("조건에 맞는 곡이 없습니다. 장르 필터를 해제하거나 CSV를 업로드해 보세요.")
    else:
        st.success(f"{len(recs)}곡 추천 완료 — {chosen_mbti} / 무드 {mood_pref}")
        # Show as pretty cards
        for idx, row in recs.reset_index(drop=True).iterrows():
            title = row.get("title", "Unknown Title")
            artist = row.get("artist", "Unknown Artist")
            genre = row.get("genre", "")
            mood = int(row.get("mood", 5))
            mbti_tags = row.get("mbti_tags", "")
            preview = row.get("preview_url", "")
            st.markdown(f"**{idx+1}. {title}** — *{artist}*")
            st.write(f"장르: `{genre}`  |  무드: `{mood}`  |  MBTI 태그: `{mbti_tags}`")
            if isinstance(preview, str) and preview.strip():
                st.markdown(f"[미리듣기/링크]({preview})")
            st.divider()
        # allow download
        to_download = recs[["title","artist","genre","mood","mbti_tags","preview_url"]] if "preview_url" in recs.columns else recs[["title","artist","genre","mood","mbti_tags"]]
        csv_bytes = to_download.to_csv(index=False).encode("utf-8")
        st.download_button("추천 결과 CSV로 다운로드", data=csv_bytes, file_name="mbti_recommendations.csv", mime="text/csv")
else:
    st.info("왼쪽 사이드바에서 MBTI와 무드를 선택한 뒤 '추천 시작 🎧' 버튼을 눌러주세요.")

# 하단에 확장 팁
st.markdown("---")
st.subheader("확장 팁")
st.markdown(
    """
- 더 많은 데이터: Spotify API나 YouTube 데이터로 곡 정보를 확장하면 훨씬 좋습니다. (API 키 필요)
- 개선 아이디어: MBTI 성향별 가중치 맵을 만들어 좀 더 정교한 점수 산정 적용 가능.
- UI 개선: album art URL 컬럼을 추가하면 `st.image()`로 카드형 UI 제공 가능.
"""
)
