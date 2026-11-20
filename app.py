import base64
import json
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Santa's Secret Mission RPG",
    page_icon="🎅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 상단 여백 최소화 (게임 화면 몰입감)
st.markdown(
    """
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 960px; }
        header[data-testid="stHeader"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

def load_b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 깃허브에 업로드된 이미지 3장 로드
IMG_MAP = load_b64("house_map.png")
IMG_CARDS = load_b64("cards.png")
IMG_COMPLETE = load_b64("complete.png")

if "game_started" not in st.session_state:
    st.session_state.game_started = False

# ==========================================
# 1. 작전 설정 로비 (팀 코드 & 시작 역할 선택)
# ==========================================
if not st.session_state.game_started:
    st.markdown("## 🎅 산타의 비밀 작전 : 2D 협동 RPG")
    st.caption("2인 1조(태블릿 2대)로 접속해 같은 작전 코드를 고르고, 역할을 나누어 산타의 선물 리스트를 복원하세요!")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        team_code = st.selectbox(
            "1️⃣ 우리 팀 작전 코드 (짝과 똑같이 선택!)",
            [f"TEAM {i}" for i in range(1, 13)]
        )
    with c2:
        role_choice = st.radio(
            "2️⃣ 시작 역할 (짝과 서로 다르게 선택!)",
            [
                "A: 본부 관제 요원 (관제실 RPG · 지령 & 해독)",
                "B: 현장 탐색 요원 (산타하우스 RPG · 숨은그림찾기)"
            ]
        )

    player_name = st.text_input("3️⃣ 내 이름 입력", placeholder="예: 김민수")

    if st.button("🎮 RPG 게임 시작하기!", type="primary", use_container_width=True):
        st.session_state.team_code = team_code
        st.session_state.initial_role = "A" if role_choice.startswith("A") else "B"
        st.session_state.player_name = player_name.strip() if player_name.strip() else "산타 요원"
        st.session_state.game_started = True
        st.rerun()
    st.stop()

# 상단 미니 바 (처음으로 리셋 버튼)
top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown(
        f"**🎄 {st.session_state.team_code}** | 요원: **{st.session_state.player_name}** "
        f"(초기 역할: **{st.session_state.initial_role}**) — *방향키 또는 화면 터치패드로 이동하세요!*"
    )
with top_col2:
    if st.button("🔄 팀/역할 재설정", use_container_width=True):
        st.session_state.game_started = False
        st.rerun()

# ==========================================
# 2. HTML5 Canvas + JS 실시간 2D RPG 게임 엔진
# ==========================================
config_json = json.dumps({
    "teamCode": st.session_state.team_code,
    "initialRole": st.session_state.initial_role,
    "playerName": st.session_state.player_name,
    "imgMap": IMG_MAP,
    "imgCards": IMG_CARDS,
    "imgComplete": IMG_COMPLETE,
})

html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<style>
  * {{ box-sizing: border-box; user-select: none; -webkit-user-select: none; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }}
  body {{ margin: 0; padding: 0; background: #1e1b2e; color: #fff; border-radius: 14px; overflow: hidden; }}
  
  .game-wrapper {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    background: linear-gradient(135deg, #1b1f3b 0%, #2a1b3d 100%);
    border: 3px solid #f4c430;
    border-radius: 14px;
  }}

  /* 왼쪽: 2D RPG 캔버스 영역 */
  .canvas-zone {{
    position: relative;
    flex: 1 1 420px;
    max-width: 460px;
    margin: 0 auto;
  }}
  canvas#rpgCanvas {{
    width: 100%;
    aspect-ratio: 1 / 1;
    display: block;
    border-radius: 10px;
    border: 3px solid #ffd166;
    background: #2b2d42;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
  }}
  .hud-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 20, 40, 0.9);
    border: 2px solid #4cc9f0;
    border-radius: 8px;
    padding: 6px 10px;
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: bold;
  }}
  .badge-role {{
    background: #f72585;
    padding: 3px 8px;
    border-radius: 6px;
    color: #fff;
  }}
  .badge-role.hq {{ background: #3a86ff; }}

  /* 오른쪽: 인벤토리 + RPG 대화창 + 터치 컨트롤러 */
  .side-zone {{
    flex: 1 1 320px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
  }}

  /* 인벤토리 4칸 */
  .inv-box {{
    background: rgba(16, 22, 42, 0.92);
    border: 2px solid #ffd166;
    border-radius: 10px;
    padding: 8px 10px;
  }}
  .inv-title {{ font-size: 12px; color: #ffd166; font-weight: bold; margin-bottom: 6px; }}
  .inv-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }}
  .inv-slot {{
    background: #252d4a;
    border: 1px solid #4a5568;
    border-radius: 6px;
    padding: 5px 7px;
    font-size: 11.5px;
    color: #a0aec0;
    min-height: 36px;
    display: flex;
    align-items: center;
  }}
  .inv-slot.done {{
    background: #1b4332;
    border-color: #52b788;
    color: #d8f3dc;
    font-weight: bold;
  }}

  /* 클래식 RPG 대화창 */
  .dialogue-box {{
    flex: 1;
    background: #0d1321;
    border: 3px solid #f8f9fa;
    box-shadow: inset 0 0 0 2px #3a86ff;
    border-radius: 10px;
    padding: 12px;
    min-height: 210px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .dlg-speaker {{
    font-size: 13px;
    font-weight: bold;
    color: #ffd166;
    margin-bottom: 6px;
    border-bottom: 1px solid #2d3748;
    padding-bottom: 4px;
  }}
  .dlg-text {{
    font-size: 14px;
    line-height: 1.5;
    color: #f1faee;
    margin-bottom: 8px;
  }}
  .card-preview {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: #1d2d44;
    padding: 6px;
    border-radius: 8px;
    margin-bottom: 8px;
  }}
  canvas#cardCanvas {{
    width: 78px;
    height: 78px;
    border-radius: 6px;
    border: 2px solid #ffd166;
    background: #fff;
    flex-shrink: 0;
  }}
  .word-form {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    background: #1b263b;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #4cc9f0;
  }}
  .word-input {{
    width: 105px;
    padding: 5px 8px;
    font-size: 14px;
    font-weight: bold;
    border-radius: 5px;
    border: 2px solid #ffd166;
    background: #fff;
    color: #111;
    user-select: text;
    -webkit-user-select: text;
  }}
  .btn-rpg {{
    background: #06d6a0;
    color: #073b4c;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 3px 0 #048a67;
  }}
  .btn-rpg:active {{ transform: translateY(2px); box-shadow: 0 1px 0 #048a67; }}
  .btn-rpg.blue {{ background: #4cc9f0; color: #03045e; box-shadow: 0 3px 0 #0077b6; }}
  .feedback-msg {{ font-size: 12.5px; margin-top: 5px; font-weight: bold; }}

  /* 태블릿용 D-Pad & 액션 버튼 */
  .controls-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 20, 40, 0.92);
    border: 2px solid #4a5568;
    border-radius: 10px;
    padding: 8px 14px;
  }}
  .dpad {{
    display: grid;
    grid-template-columns: 44px 44px 44px;
    grid-template-rows: 40px 40px 40px;
    gap: 3px;
  }}
  .dpad button {{
    background: #334155;
    color: #fff;
    border: 2px solid #64748b;
    border-radius: 8px;
    font-size: 18px;
    cursor: pointer;
    touch-action: manipulation;
  }}
  .dpad button:active, .dpad button.pressed {{ background: #ffd166; color: #111; }}
  .action-btn {{
    width: 118px;
    height: 86px;
    border-radius: 14px;
    border: 3px solid #ffd166;
    background: #e63946;
    color: #fff;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 5px 0 #9b2226;
    touch-action: manipulation;
  }}
  .action-btn.ready {{
    background: #06d6a0;
    color: #073b4c;
    box-shadow: 0 5px 0 #048a67;
    animation: pulse 1s infinite;
  }}
  @keyframes pulse {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.04); }}
    100% {{ transform: scale(1); }}
  }}

  /* 역할 교대 및 엔딩 오버레이 */
  .overlay-modal {{
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 30, 0.94);
    z-index: 99;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
  }}
  .overlay-modal.hidden {{ display: none; }}
  .complete-img {{
    max-width: 420px;
    width: 90%;
    border-radius: 12px;
    border: 3px solid #ffd166;
    margin-bottom: 12px;
  }}
  .summary-list {{
    background: #1b263b;
    border: 2px solid #4cc9f0;
    border-radius: 10px;
    padding: 10px 18px;
    text-align: left;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 12px;
  }}
</style>
</head>
<body>

<div class="game-wrapper">
  <!-- 왼쪽 2D RPG 맵 -->
  <div class="canvas-zone">
    <div class="hud-top">
      <span id="hudLocation">📍 위치: Kitchen</span>
      <span id="hudStage">퀘스트: 1 / 4</span>
      <span id="hudRoleBadge" class="badge-role">현장 요원</span>
    </div>
    <canvas id="rpgCanvas" width="500" height="500"></canvas>
  </div>

  <!-- 오른쪽 인벤토리 + RPG 대화창 + 컨트롤러 -->
  <div class="side-zone">
    <div class="inv-box">
      <div class="inv-title">🎒 복원된 산타 리스트 (인벤토리)</div>
      <div class="inv-grid" id="invGrid">
        <div class="inv-slot" id="slot0">1. ☕ 얼룩짐</div>
        <div class="inv-slot" id="slot1">2. ☕ 얼룩짐</div>
        <div class="inv-slot" id="slot2">3. ☕ 얼룩짐</div>
        <div class="inv-slot" id="slot3">4. ☕ 얼룩짐</div>
      </div>
    </div>

    <div class="dialogue-box">
      <div>
        <div class="dlg-speaker" id="dlgSpeaker">🎅 산타 본부 통신</div>
        <div class="dlg-text" id="dlgText">방향키로 이동해 반짝이는 곳(✨) 앞에서 [조사/대화]를 누르세요!</div>
        <div id="dlgInteractive"></div>
      </div>
      <div id="dlgHintFooter" style="font-size:11.5px; color:#94a3b8;">
        💡 물건이나 NPC 가까이 다가가면 오른쪽 버튼이 초록색으로 빛납니다.
      </div>
    </div>

    <div class="controls-bar">
      <div class="dpad">
        <div></div>
        <button id="btnUp">⬆️</button>
        <div></div>
        <button id="btnLeft">⬅️</button>
        <div style="display:flex;align-items:center;justify-content:center;font-size:16px;">🧑‍🎄</div>
        <button id="btnRight">➡️</button>
        <div></div>
        <button id="btnDown">⬇️</button>
        <div></div>
      </div>
      <button id="btnAction" class="action-btn">🔍 조사 / 대화<br><span style="font-size:11px;font-weight:normal;">(Space)</span></button>
    </div>
  </div>
</div>

<!-- 역할 교대 팝업 (2단계 완료 후) -->
<div id="switchModal" class="overlay-modal hidden">
  <h2 style="color:#ffd166; margin-bottom:8px;">🔄 후반전 작전 교대! (ROLE SWITCH)</h2>
  <p style="font-size:15px; max-width:440px; line-height:1.6;">
    1·2단계 리스트 복원 성공!<br>
    3·4단계부터는 <b>본부 관제 요원</b>과 <b>현장 탐색 요원</b>의 역할이 서로 바뀝니다!
  </p>
  <button class="btn-rpg" style="font-size:16px; padding:10px 24px; margin-top:10px;" onclick="closeSwitchModal()">
    🚀 바뀐 역할로 출발하기!
  </button>
</div>

<!-- 최종 클리어 인증 화면 (Padlet 업로드용) -->
<div id="completeModal" class="overlay-modal hidden">
  <img id="completeImgEl" class="complete-img" alt="Mission Complete" />
  <h3 id="completeHeader" style="color:#ffd166; margin:4px 0 8px 0;"></h3>
  <div class="summary-list" id="completeList"></div>
  <div style="color:#4cc9f0; font-weight:bold; font-size:14px;">
    📸 이 화면을 캡처해서 우리 반 Padlet에 업로드해 주세요!
  </div>
</div>

<script>
const CFG = {config_json};

// ==========================================
// 1. 팀 코드 기반 결정론적 난수 (2태블릿 완벽 동기화)
// ==========================================
function hashSeed(str) {{
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {{
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }}
  return h >>> 0;
}}
function makeRng(seedStr) {{
  let s = hashSeed(seedStr);
  return function() {{
    s += 0x6D2B79F5;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }};
}}
function shuffleWithRng(arr, rng) {{
  const copy = arr.slice();
  for (let i = copy.length - 1; i > 0; i--) {{
    const j = Math.floor(rng() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }}
  return copy;
}}

// ==========================================
// 2. 미션 및 맵 데이터 (0~1000 좌표계)
// ==========================================
const MISSIONS = {{
  "Kitchen": {{
    roomKo: "주방 (Kitchen)",
    icon: "🔥",
    cardCrop: [0, 0], // 좌상단
    silhouette: "네모난 조리 기구 그림자",
    baseWord: "stove",
    prefix: "There is a",
    suffix: ".",
    targetWord: "stove",
    question: "What's in the kitchen?",
    options: ["There is a stove.", "There are a stove.", "There is two stoves."],
    answer: "There is a stove.",
    tip: "가스레인지가 1개(단수)이므로 'There is a stove.'예요!"
  }},
  "Bedroom": {{
    roomKo: "침실 (Bedroom)",
    icon: "🛏️🛏️",
    cardCrop: [1, 0], // 우상단
    silhouette: "푹신한 침대 그림자",
    baseWord: "bed",
    prefix: "There are two",
    suffix: ".",
    targetWord: "beds",
    question: "What's in the bedroom?",
    options: ["There is two beds.", "There are two beds.", "There are a bed."],
    answer: "There are two beds.",
    tip: "침대가 2개(복수)이므로 뒤에 '-s'를 붙여 'beds'를 써요!"
  }},
  "Living Room": {{
    roomKo: "거실 (Living Room)",
    icon: "📺",
    cardCrop: [0, 1], // 좌하단
    silhouette: "네모난 화면 가전 그림자",
    baseWord: "TV",
    prefix: "There is a",
    suffix: ".",
    targetWord: "tv",
    question: "What's in the living room?",
    options: ["There are a TV.", "There is two TVs.", "There is a TV."],
    answer: "There is a TV.",
    tip: "TV가 1개(단수)이므로 'There is a TV.'예요!"
  }},
  "Garden": {{
    roomKo: "정원 (Garden)",
    icon: "🌲🌲🌲",
    cardCrop: [1, 1], // 우하단
    silhouette: "눈 덮인 초록 나무 그림자",
    baseWord: "tree",
    prefix: "There are three",
    suffix: ".",
    targetWord: "trees",
    question: "What's in the garden?",
    options: ["There is three trees.", "There are three trees.", "There are a tree."],
    answer: "There are three trees.",
    tip: "나무가 3그루(복수)이므로 뒤에 '-s'를 붙여 'trees'를 써요!"
  }}
}};

const ROOM_SPOTS = {{
  "Kitchen": [
    {{ x: 185, y: 250 }}, {{ x: 390, y: 250 }},
    {{ x: 185, y: 405 }}, {{ x: 395, y: 405 }}
  ],
  "Bedroom": [
    {{ x: 600, y: 250 }}, {{ x: 745, y: 250 }},
    {{ x: 600, y: 405 }}, {{ x: 745, y: 405 }}
  ],
  "Living Room": [
    {{ x: 185, y: 600 }}, {{ x: 400, y: 600 }},
    {{ x: 185, y: 810 }}, {{ x: 400, y: 810 }}
  ],
  "Garden": [
    {{ x: 600, y: 600 }}, {{ x: 735, y: 625 }},
    {{ x: 600, y: 740 }}, {{ x: 745, y: 760 }}
  ]
}};

const DECOYS = [
  {{ emoji: "🐱", msg: "야옹~ 낮잠 자는 고양이(Cat)네요! 찾는 물건이 아니에요." }},
  {{ emoji: "🧦", msg: "구멍 난 산타 양말(Sock)이에요! 다른 반짝이(✨)를 찾아보세요." }},
  {{ emoji: "🧸", msg: "낡은 곰인형(Teddy Bear)이에요! 방 구석구석을 더 살펴보세요." }}
];

// house_map.png 벽 및 가구 충돌 박스 (0~1000 좌표)
const HOUSE_WALLS = [
  // 외벽
  [0, 0, 1000, 58], [0, 942, 1000, 58], [0, 0, 58, 1000], [942, 0, 58, 1000],
  // 중앙 세로벽 (상단 주방<->침실 통로 y:235~345 개방, 하단은 막힘)
  [455, 0, 90, 235], [455, 345, 90, 655],
  // 중앙 가로벽 (좌측 주방<->거실 통로 x:205~295 개방)
  [0, 455, 205, 90], [295, 455, 160, 90],
  // 중앙 가로벽 (우측 침실<->정원 통로 x:705~795 개방)
  [545, 455, 160, 90], [795, 455, 160, 90],
  // 주방 조리대 & 왼쪽 카운터
  [58, 58, 385, 145], [58, 203, 75, 220],
  // 침실 옷장 & 침대 2개
  [555, 58, 210, 140], [800, 120, 142, 110], [880, 245, 62, 85], [800, 340, 142, 110],
  // 거실 TV & 소파
  [58, 555, 82, 125], [58, 710, 68, 160], [135, 870, 185, 72],
  // 정원 소나무 3그루
  [790, 555, 152, 165], [560, 785, 135, 157], [810, 785, 132, 157]
];

// 본부 관제실(Role A) 벽 및 오브젝트
const HQ_WALLS = [
  [0, 0, 1000, 80], [0, 920, 1000, 80], [0, 0, 70, 1000], [930, 0, 70, 1000],
  [360, 170, 280, 110], // 산타 지령 데스크
  [140, 640, 170, 110], // 단말기 1
  [415, 640, 170, 110], // 단말기 2
  [690, 640, 170, 110]  // 단말기 3
];

// 팀 계획 생성
function buildTeamPlan(teamCode) {{
  const rng = makeRng(teamCode);
  const rooms = shuffleWithRng(Object.keys(MISSIONS), rng);
  return rooms.map(room => {{
    const spots = shuffleWithRng(ROOM_SPOTS[room], rng);
    return {{
      room,
      targetSpot: spots[0],
      decoys: [
        {{ ...spots[1], ...DECOYS[0] }},
        {{ ...spots[2], ...DECOYS[1] }},
        {{ ...spots[3], ...DECOYS[2] }}
      ]
    }};
  }});
}}

const TEAM_PLAN = buildTeamPlan(CFG.teamCode);

// ==========================================
// 3. 게임 상태 변수
// ==========================================
let roundIdx = 0;
let player = {{ x: 250, y: 295, dir: "down", walkFrame: 0 }};
let checkedSpots = new Set();
let wordSolved = false;
let hqBriefed = false;
let nearObj = null;
let keys = {{}};
let lastTime = 0;

// 이미지 로드
const houseImg = new Image();
if (CFG.imgMap) houseImg.src = "data:image/png;base64," + CFG.imgMap;

const cardsImg = new Image();
if (CFG.imgCards) cardsImg.src = "data:image/png;base64," + CFG.imgCards;

if (CFG.imgComplete) {{
  document.getElementById("completeImgEl").src = "data:image/png;base64," + CFG.imgComplete;
}}

function getActiveRole() {{
  if (roundIdx < 2) return CFG.initialRole;
  return CFG.initialRole === "A" ? "B" : "A";
}}

function resetPositionForRole() {{
  const role = getActiveRole();
  if (role === "B") {{
    player = {{ x: 250, y: 295, dir: "down", walkFrame: 0 }}; // 주방 중앙
  }} else {{
    player = {{ x: 500, y: 450, dir: "up", walkFrame: 0 }};   // 본부 관제실 중앙
  }}
  checkedSpots = new Set();
  wordSolved = false;
  hqBriefed = false;
  updateHudAndPrompt();
}}

// ==========================================
// 4. UI & 대화창 업데이트
// ==========================================
function setDialogue(speaker, text, interactiveHtml = "") {{
  document.getElementById("dlgSpeaker").innerHTML = speaker;
  document.getElementById("dlgText").innerHTML = text;
  document.getElementById("dlgInteractive").innerHTML = interactiveHtml;
}}

function updateInventoryUI() {{
  for (let i = 0; i < 4; i++) {{
    const el = document.getElementById("slot" + i);
    const m = MISSIONS[TEAM_PLAN[i].room];
    if (i < roundIdx) {{
      el.className = "inv-slot done";
      el.innerHTML = `✅ ${{m.icon}} ${{m.answer}}`;
    }} else if (i === roundIdx) {{
      el.className = "inv-slot";
      el.innerHTML = `🔍 ${{i + 1}}단계 조사 중...`;
    }} else {{
      el.className = "inv-slot";
      el.innerHTML = `🔒 ${{i + 1}}단계 잠김`;
    }}
  }}
}}

function updateHudAndPrompt() {{
  updateInventoryUI();
  if (roundIdx >= 4) {{
    showCompleteScreen();
    return;
  }}
  const role = getActiveRole();
  const step = TEAM_PLAN[roundIdx];
  const m = MISSIONS

