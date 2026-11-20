import base64
import os
import random
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Santa's Secret Mission RPG",
    page_icon="🎅",
    layout="centered"
)

# ==========================================
# 1. 이미지 로드 및 4분할 카드 크롭 헬퍼
# ==========================================
def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data
def get_cropped_card(room_name: str, card_sheet_path: str = "cards.png"):
    """cards.png (2x2 그리드)에서 각 방에 해당하는 카드 영역만 자동 크롭"""
    if not os.path.exists(card_sheet_path):
        return None
    img = Image.open(card_sheet_path)
    w, h = img.size
    boxes = {
        "Kitchen": (0, 0, w // 2, h // 2),          # 좌상단: a stove
        "Bedroom": (w // 2, 0, w, h // 2),          # 우상단: two beds
        "Living Room": (0, h // 2, w // 2, h),      # 좌하단: a TV
        "Garden": (w // 2, h // 2, w, h),           # 우하단: three trees
    }
    return img.crop(boxes[room_name])

# ==========================================
# 2. house_map.png (14x14 그리드) 실제 벽/통로 좌표 매핑
# 0: 이동 가능 바닥, 1: 벽/가구 장애물
# ==========================================
HOUSE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 0: 상단 외벽
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 1: 상단 가구/벽
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 2: 상단 싱크대/옷장/침대
    [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1],  # 3: 주방/침실 상단 바닥
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # 4: 주방 <-> 침실 통로 개방
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # 5: 주방 <-> 침실 통로 개방
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 6: 주방<->거실 / 침실<->정원 통로
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],  # 7: 주방<->거실 / 침실<->정원 통로
    [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1],  # 8: 거실(TV 옆) / 정원 상단
    [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1],  # 9: 거실 / 정원 중단
    [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],  # 10: 거실 / 정원 중앙
    [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1],  # 11: 거실 하단 / 정원 나무 사이
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],  # 12: 소파/나무 하단
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 13: 하단 외벽
]

# 각 방의 조사 포인트(✨) 4곳 좌표
ROOM_SPOTS = {
    "Kitchen": [(3, 2), (3, 4), (5, 2), (5, 5)],
    "Bedroom": [(3, 8), (3, 10), (5, 8), (5, 10)],
    "Living Room": [(8, 2), (8, 5), (11, 2), (11, 5)],
    "Garden": [(8, 8), (9, 10), (10, 8), (11, 10)],
}

# 4개 방 미션 데이터
MISSIONS = {
    "Kitchen": {
        "room_ko": "주방 (Kitchen)",
        "silhouette": "⬛ 사각형 조리 기구 (그림자)",
        "visual_icons": "🔥 (1개)",
        "base_word": "stove",
        "sentence_prefix": "There is a",
        "sentence_suffix": ".",
        "target_word": "stove",
        "question": "What's in the kitchen?",
        "options": [
            "There is a stove.",
            "There are a stove.",
            "There is two stoves."
        ],
        "answer": "There is a stove.",
        "grammar_tip": "가스레인지가 1개(단수)이므로 'There is a stove.'를 써요!"
    },
    "Bedroom": {
        "room_ko": "침실 (Bedroom)",
        "silhouette": "⬛ 푹신한 침구 가구 (그림자)",
        "visual_icons": "🛏️ 🛏️ (2개)",
        "base_word": "bed",
        "sentence_prefix": "There are two",
        "sentence_suffix": ".",
        "target_word": "beds",
        "question": "What's in the bedroom?",
        "options": [
            "There is two beds.",
            "There are two beds.",
            "There are a bed."
        ],
        "answer": "There are two beds.",
        "grammar_tip": "침대가 2개(복수)이므로 단어 뒤에 '-s'를 붙여 'beds'라고 써요!"
    },
    "Living Room": {
        "room_ko": "거실 (Living Room)",
        "silhouette": "⬛ 네모난 화면 가전 (그림자)",
        "visual_icons": "📺 (1개)",
        "base_word": "TV",
        "sentence_prefix": "There is a",
        "sentence_suffix": ".",
        "target_word": "tv",
        "question": "What's in the living room?",
        "options": [
            "There are a TV.",
            "There is two TVs.",
            "There is a TV."
        ],
        "answer": "There is a TV.",
        "grammar_tip": "TV가 1개(단수)이므로 'There is a TV.'를 써요!"
    },
    "Garden": {
        "room_ko": "정원 (Garden)",
        "silhouette": "⬛ 눈 덮인 초록 나무 (그림자)",
        "visual_icons": "🌲 🌲 🌲 (3그루)",
        "base_word": "tree",
        "sentence_prefix": "There are three",
        "sentence_suffix": ".",
        "target_word": "trees",
        "question": "What's in the garden?",
        "options": [
            "There is three trees.",
            "There are three trees.",
            "There are a tree."
        ],
        "answer": "There are three trees.",
        "grammar_tip": "나무가 3그루(복수)이므로 단어 뒤에 '-s'를 붙여 'trees'라고 써요!"
    }
}

DECOYS = [
    ("🐱", "낮잠 자는 고양이 (Cat) — 찾는 물건이 아니에요!"),
    ("🧦", "산타의 빈 양말 (Sock) — 여긴 선물이 없어요!"),
    ("🧸", "낡은 곰인형 (Teddy Bear) — 다른 반짝이(✨)를 찾아보세요!")
]

def get_team_plan(team_code: str):
    """팀 코드별 동일한 미션 순서와 숨겨진 좌표 생성 (2태블릿 자동 동기화)"""
    rng = random.Random(team_code)
    rooms = list(MISSIONS.keys())
    rng.shuffle(rooms)
    plan = []
    for room in rooms:
        spots = ROOM_SPOTS[room].copy()
        rng.shuffle(spots)
        plan.append({
            "room": room,
            "target_coord": spots[0],
            "decoy_map": {
                spots[1]: DECOYS[0],
                spots[2]: DECOYS[1],
                spots[3]: DECOYS[2],
            }
        })
    return plan

def get_room_name(r: int, c: int) -> str:
    if r <= 5 and c <= 5:
        return "🍳 Kitchen (주방)"
    elif r <= 5 and c >= 8:
        return "🛏️ Bedroom (침실)"
    elif r >= 8 and c <= 5:
        return "🛋️ Living Room (거실)"
    elif r >= 8 and c >= 8:
        return "🌳 Garden (정원)"
    return "🚪 Hallway / Doorway (통로)"

# ==========================================
# 3. 세션 상태 초기화
# ==========================================
if "started" not in st.session_state:
    st.session_state.started = False
if "round_idx" not in st.session_state:
    st.session_state.round_idx = 0
if "pos" not in st.session_state:
    st.session_state.pos = [4, 3]  # 주방 중앙에서 출발
if "checked_spots" not in st.session_state:
    st.session_state.checked_spots = set()
if "word_solved" not in st.session_state:
    st.session_state.word_solved = False

# ==========================================
# 4. 초기 작전 설정 화면 (팀 코드 + 역할 선택)
# ==========================================
if not st.session_state.started:
    st.title("🎅 산타의 비밀 작전: 2인 1조 RPG")
    st.markdown("커피가 쏟아져 지워진 산타의 선물 리스트를 짝과 함께 복원하세요!")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        team_code = st.selectbox(
            "1️⃣ 우리 팀 작전 코드 선택 (짝과 동일하게!)",
            [f"TEAM {i}" for i in range(1, 13)]
        )
    with col2:
        initial_role = st.radio(
            "2️⃣ 시작 역할 선택 (서로 다르게!)",
            ["A: 본부 요원 (질문 & 리스트 복원)", "B: 현장 요원 (ZEP 맵 숨은그림찾기)"]
        )

    my_name = st.text_input("3️⃣ 내 이름 입력 (예: 김민수)", placeholder="이름을 입력하세요")

    if st.button("🚀 작전 개시!", type="primary", use_container_width=True):
        st.session_state.team_code = team_code
        st.session_state.initial_role = "A" if initial_role.startswith("A") else "B"
        st.session_state.my_name = my_name.strip() if my_name.strip() else "산타 요원"
        st.session_state.started = True
        st.rerun()
    st.stop()

plan = get_team_plan(st.session_state.team_code)
r_idx = st.session_state.round_idx

# ==========================================
# 5. 전체 4단계 클리어 화면 (complete.png + Padlet 인증용)
# ==========================================
if r_idx >= 4:
    st.balloons()
    if os.path.exists("complete.png"):
        st.image("complete.png", use_container_width=True)
    else:
        st.title("🎉 MISSION COMPLETE!")

    st.success(f"**[{st.session_state.team_code} - {st.session_state.my_name}]** 산타의 선물 리스트를 완벽히 복원했습니다!")
    st.subheader("📜 복원 완료된 산타의 선물 리스트")
    for idx, step in enumerate(plan, 1):
        m = MISSIONS[step["room"]]
        st.markdown(f"**{idx}. {m['room_ko']}** : `{m['answer']}` — {m['visual_icons']}")

    st.info("📸 **이 화면을 캡처해서 우리 반 Padlet에 업로드해 주세요!**")
    if st.button("🔄 처음 화면으로 돌아가기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# 현재 라운드 정보 및 3~4단계 자동 역할 교대
current_step = plan[r_idx]
target_room = current_step["room"]
mission = MISSIONS[target_room]

if r_idx < 2:
    active_role = st.session_state.initial_role
else:
    active_role = "B" if st.session_state.initial_role == "A" else "A"

# 상단 상태바
st.markdown(f"### 🎄 {st.session_state.team_code} | 단계: **{r_idx + 1} / 4** | 요원: **{st.session_state.my_name}**")
if r_idx == 2:
    st.warning("🔄 **후반전 역할 교대!** 3~4단계에서는 본부 요원과 현장 요원의 임무가 서로 바뀝니다!")

# ==========================================
# 화면 A: 본부 요원 (List Keeper)
# ==========================================
if active_role == "A":
    st.info("🎧 **현재 임무: [본부 요원]** — 짝(현장 요원)에게 방 위치를 알려주고 영어로 질문하세요!")

    col_list, col_quiz = st.columns([1, 1.3])

    with col_list:
        st.markdown("#### 📋 산타의 선물 리스트")
        for i, step in enumerate(plan):
            m_item = MISSIONS[step["room"]]
            if i < r_idx:
                st.success(f"✅ {m_item['room_ko']}\n\n**{m_item['answer']}**")
            elif i == r_idx:
                st.warning(f"☕ **[조사 필요] {m_item['room_ko']}**\n\n힌트: {m_item['silhouette']}\n\n*(개수 얼룩짐)*")
            else:
                st.markdown(f"🔒 {i+1}단계: 잠김")

    with col_quiz:
        st.markdown("#### 🗣️ 작전 지령 및 정답 입력")
        st.markdown(f"1️⃣ 짝에게 이동 지시하기: **\"Go to the {target_room.lower()}!\"**")
        st.markdown(f"2️⃣ 짝이 문장을 완성하면 질문하기:\n### 👉 *\"{mission['question']}\"*")
        st.divider()

        choice = st.radio(
            "3️⃣ 짝의 영어 대답을 듣고 알맞은 문장을 고르세요:",
            mission["options"],
            key=f"quiz_{r_idx}"
        )

        if st.button("✨ 리스트 복원하기 (정답 제출)", type="primary", use_container_width=True):
            if choice == mission["answer"]:
                st.session_state.round_idx += 1
                st.session_state.checked_spots = set()
                st.session_state.word_solved = False
                st.rerun()
            else:
                st.error(f"❌ 짝의 대답을 다시 들어보세요! ({mission['grammar_tip']})")

# ==========================================
# 화면 B: 현장 요원 (ZEP 2D 맵 숨은그림찾기)
# ==========================================
else:
    st.info("🕹️ **현재 임무: [현장 요원]** — 짝이 알려준 방으로 이동해 반짝이(✨)를 조사하세요!")

    col_map, col_ctrl = st.columns([1.35, 1.05])

    with col_map:
        st.caption(f"📍 현재 위치: **{get_room_name(*st.session_state.pos)}**")
        target_coord = current_step["target_coord"]
        decoy_map = current_step["decoy_map"]
        map_b64 = get_base64_image("house_map.png")

        if map_b64:
            table_style = (
                f"border-collapse: collapse; margin: auto; width: 100%; max-width: 420px; "
                f"aspect-ratio: 1 / 1; background-image: url('data:image/png;base64,{map_b64}'); "
                f"background-size: 100% 100%; border-radius: 10px; overflow: hidden; "
                f"box-shadow: 0 4px 12px rgba(0,0,0,0.18);"
            )
        else:
            table_style = (
                "border-collapse: collapse; margin: auto; width: 100%; max-width: 420px; "
                "aspect-ratio: 1 / 1; background-color: #FFFDF7; border: 2px solid #8D6E63;"
            )

        html = f"<table style='{table_style}'>"
        for r in range(len(HOUSE_MAP)):
            html += "<tr>"
            for c in range(len(HOUSE_MAP[0])):
                cell = ""
                cell_bg = "transparent"
                if not map_b64 and HOUSE_MAP[r][c] == 1:
                    cell_bg = "#D7CCC8"

                if [r, c] == st.session_state.pos:
                    cell = "<span style='filter: drop-shadow(0 2px 3px rgba(0,0,0,0.75)); font-size: 20px;'>🧑‍🎄</span>"
                elif (r, c) == target_coord and (r, c) in st.session_state.checked_spots:
                    cell = "<span style='filter: drop-shadow(0 2px 3px rgba(0,0,0,0.6)); font-size: 18px;'>🎁</span>"
                elif (r, c) in decoy_map and (r, c) in st.session_state.checked_spots:
                    cell = f"<span style='font-size: 16px;'>{decoy_map[(r, c)][0]}</span>"
                elif any((r, c) in spots for spots in ROOM_SPOTS.values()):
                    cell = "<span style='filter: drop-shadow(0 0 4px #FFD54F); font-size: 16px;'>✨</span>"

                html += (
                    f"<td style='width: 7.1428%; height: 7.1428%; text-align: center; "
                    f"vertical-align: middle; padding: 0; border: none; background: {cell_bg};'>{cell}</td>"
                )
            html += "</tr>"
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
        st.caption("좌상단: Kitchen | 우상단: Bedroom | 좌하단: Living Room | 우하단: Garden")

    with col_ctrl:
        st.markdown("#### 🎮 이동 컨트롤러")

        def move(dr: int, dc: int):
            nr, nc = st.session_state.pos[0] + dr, st.session_state.pos[1] + dc
            if 0 <= nr < len(HOUSE_MAP) and 0 <= nc < len(HOUSE_MAP[0]):
                if HOUSE_MAP[nr][nc] == 0:
                    st.session_state.pos = [nr, nc]
                    if any((nr, nc) in spots for spots in ROOM_SPOTS.values()):
                        st.session_state.checked_spots.add((nr, nc))

        _, c_up, _ = st.columns(3)
        with c_up:
            if st.button("⬆️", use_container_width=True):
                move(-1, 0)
                st.rerun()

        c_left, c_mid, c_right = st.columns(3)
        with c_left:
            if st.button("⬅️", use_container_width=True):
                move(0, -1)
                st.rerun()
        with c_mid:
            st.markdown("<div style='text-align:center; padding-top:6px;'>🧑‍🎄</div>", unsafe_allow_html=True)
        with c_right:
            if st.button("➡️", use_container_width=True):
                move(0, 1)
                st.rerun()

        _, c_down, _ = st.columns(3)
        with c_down:
            if st.button("⬇️", use_container_width=True):
                move(1, 0)
                st.rerun()

        st.divider()
        curr_tuple = tuple(st.session_state.pos)

        # 탐색 결과 카드 팝업 & 빈칸 단어 문장 완성
        if curr_tuple == current_step["target_coord"]:
            st.success("🎉 **목표 사물 발견!**")
            cropped_card = get_cropped_card(target_room)
            if cropped_card is not None:
                st.image(cropped_card, use_container_width=True)
            else:
                st.markdown(f"### {mission['visual_icons']}")

            st.caption(f"🔤 단어 힌트: **`{mission['base_word']}`** (그림의 개수를 보고 빈칸에 단어를 넣으세요!)")

            if not st.session_state.word_solved:
                s_col1, s_col2, s_col3 = st.columns([1.3, 1.3, 0.2])
                with s_col1:
                    st.markdown(
                        f"<div style='padding-top:8px; font-weight:bold; font-size:15px;'>{mission['sentence_prefix']}</div>",
                        unsafe_allow_html=True
                    )
                with s_col2:
                    user_word = st.text_input(
                        "단어 입력",
                        placeholder="단어 입력",
                        label_visibility="collapsed",
                        key=f"word_input_{r_idx}"
                    )
                with s_col3:
                    st.markdown(
                        f"<div style='padding-top:8px; font-weight:bold; font-size:15px;'>{mission['sentence_suffix']}</div>",
                        unsafe_allow_html=True
                    )

                if st.button("✨ 문장 완성 확인", type="primary", use_container_width=True):
                    cleaned = user_word.strip().lower().rstrip(".")
                    if cleaned == mission["target_word"]:
                        st.session_state.word_solved = True
                        st.rerun()
                    elif cleaned == mission["base_word"].lower() and mission["target_word"].endswith("s"):
                        st.warning(f"💡 아깝다! 그림에 물건이 여러 개 있어요. `{mission['base_word']}` 뒤에 **`-s`**를 붙여볼까요?")
                    else:
                        st.error(f"❌ 다시 확인해 보세요! 단어 힌트 `{mission['base_word']}`를 개수에 맞게 넣어보세요.")
            else:
                st.info(f"🗣️ **완성된 문장:**\n### *\"{mission['answer']}\"*")
                st.caption("짝이 영어 질문을 하면 위 문장을 큰 소리로 대답한 뒤 아래 버튼을 누르세요!")
                if st.button("✅ 영어 보고 완료! 다음 단계로", type="primary", use_container_width=True):
                    st.session_state.round_idx += 1
                    st.session_state.checked_spots = set()
                    st.session_state.word_solved = False
                    st.rerun()

        elif curr_tuple in current_step["decoy_map"]:
            _, decoy_text = current_step["decoy_map"][curr_tuple]
            st.warning(decoy_text)
        else:
            st.caption("💡 짝이 알려준 방의 반짝이(✨) 칸 위로 산타를 이동시키세요!")
