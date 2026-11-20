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

st.markdown(
    """
    <style>
        .block-container { padding-top: 0.6rem; padding-bottom: 0.6rem; max-width: 960px; }
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
    st.caption("2인 1조로 접속해 같은 작전 코드를 고르고, 역할을 나누어 산타의 선물 리스트를 복원하세요!")
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

top_col1, top_col2 = st.columns([4, 1])
with top_col1:
    st.markdown(
        f"**🎄 {st.session_state.team_code}** | 요원: **{st.session_state.player_name}** "
        f"(시작 역할: **{st.session_state.initial_role}**)"
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

html_template = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<style>
  * { box-sizing: border-box; user-select: none; -webkit-user-select: none; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }
  body { margin: 0; padding: 0; background: transparent; color: #fff; }
  
  .game-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    background: linear-gradient(135deg, #1b1f3b 0%, #2a1b3d 100%);
    border: 3px solid #f4c430;
    border-radius: 14px;
  }

  .canvas-zone {
    position: relative;
    flex: 1 1 400px;
    max-width: 450px;
    margin: 0 auto;
  }
  canvas#rpgCanvas {
    width: 100%;
    aspect-ratio: 1 / 1;
    display: block;
    border-radius: 10px;
    border: 3px solid #ffd166;
    background: #2b2d42;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
  }
  .hud-top {
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
  }
  .badge-role {
    background: #f72585;
    padding: 3px 8px;
    border-radius: 6px;
    color: #fff;
  }
  .badge-role.hq { background: #3a86ff; }

  .side-zone {
    flex: 1 1 320px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
  }

  .inv-box {
    background: rgba(16, 22, 42, 0.92);
    border: 2px solid #ffd166;
    border-radius: 10px;
    padding: 8px 10px;
  }
  .inv-title { font-size: 12px; color: #ffd166; font-weight: bold; margin-bottom: 6px; }
  .inv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
  .inv-slot {
    background: #252d4a;
    border: 1px solid #4a5568;
    border-radius: 6px;
    padding: 5px 7px;
    font-size: 11.5px;
    color: #a0aec0;
    min-height: 34px;
    display: flex;
    align-items: center;
  }
  .inv-slot.done {
    background: #1b4332;
    border-color: #52b788;
    color: #d8f3dc;
    font-weight: bold;
  }

  .dialogue-box {
    flex: 1;
    background: #0d1321;
    border: 3px solid #f8f9fa;
    box-shadow: inset 0 0 0 2px #3a86ff;
    border-radius: 10px;
    padding: 10px 12px;
    min-height: 195px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .dlg-speaker {
    font-size: 13px;
    font-weight: bold;
    color: #ffd166;
    margin-bottom: 5px;
    border-bottom: 1px solid #2d3748;
    padding-bottom: 4px;
  }
  .dlg-text {
    font-size: 13.5px;
    line-height: 1.45;
    color: #f1faee;
    margin-bottom: 6px;
  }
  .card-preview {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #1d2d44;
    padding: 6px;
    border-radius: 8px;
    margin-bottom: 6px;
  }
  canvas#cardCanvas {
    width: 68px;
    height: 68px;
    border-radius: 6px;
    border: 2px solid #ffd166;
    background: #fff;
    flex-shrink: 0;
  }
  .word-form {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    background: #1b263b;
    padding: 7px;
    border-radius: 8px;
    border: 1px solid #4cc9f0;
  }
  .word-input {
    width: 100px;
    padding: 5px 8px;
    font-size: 14px;
    font-weight: bold;
    border-radius: 5px;
    border: 2px solid #ffd166;
    background: #fff;
    color: #111;
    user-select: text;
    -webkit-user-select: text;
  }
  .btn-rpg {
    background: #06d6a0;
    color: #073b4c;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 3px 0 #048a67;
  }
  .btn-rpg:active { transform: translateY(2px); box-shadow: 0 1px 0 #048a67; }
  .btn-rpg.blue { background: #4cc9f0; color: #03045e; box-shadow: 0 3px 0 #0077b6; }
  .feedback-msg { font-size: 12px; margin-top: 4px; font-weight: bold; }

  .controls-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 20, 40, 0.95);
    border: 2px solid #4a5568;
    border-radius: 10px;
    padding: 8px 14px;
  }
  .dpad {
    display: grid;
    grid-template-columns: 46px 46px 46px;
    grid-template-rows: 42px 42px 42px;
    gap: 4px;
  }
  .dpad button {
    background: #334155;
    color: #fff;
    border: 2px solid #64748b;
    border-radius: 8px;
    font-size: 18px;
    cursor: pointer;
    touch-action: manipulation;
  }
  .dpad button:active, .dpad button.pressed { background: #ffd166; color: #111; }
  .action-btn {
    width: 118px;
    height: 88px;
    border-radius: 14px;
    border: 3px solid #ffd166;
    background: #e63946;
    color: #fff;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 5px 0 #9b2226;
    touch-action: manipulation;
  }
  .action-btn.ready {
    background: #06d6a0;
    color: #073b4c;
    box-shadow: 0 5px 0 #048a67;
    animation: pulse 1s infinite;
  }
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.04); }
    100% { transform: scale(1); }
  }

  /* 📱 휴대폰 세로 화면 최적화: 한 화면에 맵 + 대화창 + 방향키 모두 표시 */
  @media (max-width: 768px) {
    .game-wrapper { padding: 8px; gap: 8px; }
    .canvas-zone { flex: 1 1 100%; max-width: 100%; }
    .hud-top { padding: 4px 8px; margin-bottom: 6px; font-size: 12px; }
    canvas#rpgCanvas { max-width: 265px; margin: 0 auto; }
    .side-zone { flex: 1 1 100%; gap: 8px; }
    .dialogue-box { order: 1; min-height: 125px; padding: 8px 10px; }
    .controls-bar { order: 2; padding: 6px 12px; }
    .inv-box { order: 3; padding: 6px 8px; }
    .inv-slot { min-height: 28px; font-size: 11px; padding: 3px 6px; }
    .dpad {
      grid-template-columns: 44px 44px 44px;
      grid-template-rows: 38px 38px 38px;
      gap: 3px;
    }
    .action-btn { width: 110px; height: 80px; font-size: 14px; }
    .dlg-footer-tip { display: none; }
  }

  .overlay-modal {
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 30, 0.95);
    z-index: 99;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 16px;
  }
  .overlay-modal.hidden { display: none; }
  .complete-img {
    max-width: 380px;
    width: 88%;
    border-radius: 12px;
    border: 3px solid #ffd166;
    margin-bottom: 10px;
  }
  .summary-list {
    background: #1b263b;
    border: 2px solid #4cc9f0;
    border-radius: 10px;
    padding: 8px 14px;
    text-align: left;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 10px;
  }
</style>
</head>
<body>

<div class="game-wrapper">
  <div class="canvas-zone">
    <div class="hud-top">
      <span id="hudLocation">📍 위치: Kitchen</span>
      <span id="hudStage">퀘스트: 1 / 4</span>
      <span id="hudRoleBadge" class="badge-role">현장 요원</span>
    </div>
    <canvas id="rpgCanvas" width="500" height="500"></canvas>
  </div>

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
      <div class="dlg-footer-tip" style="font-size:11.5px; color:#94a3b8;">
        💡 물건이나 NPC 가까이 다가가면 오른쪽 버튼이 초록색으로 빛납니다.
      </div>
    </div>

    <div class="controls-bar">
      <div class="dpad">
        <div></div>
        <button id="btnUp" type="button">⬆️</button>
        <div></div>
        <button id="btnLeft" type="button">⬅️</button>
        <div style="display:flex;align-items:center;justify-content:center;font-size:16px;">🧑‍🎄</div>
        <button id="btnRight" type="button">➡️</button>
        <div></div>
        <button id="btnDown" type="button">⬇️</button>
        <div></div>
      </div>
      <button id="btnAction" type="button" class="action-btn">🔍 조사 / 대화<br><span style="font-size:11px;font-weight:normal;">(Space)</span></button>
    </div>
  </div>
</div>

<div id="switchModal" class="overlay-modal hidden">
  <h2 style="color:#ffd166; margin-bottom:8px;">🔄 후반전 작전 교대! (ROLE SWITCH)</h2>
  <p style="font-size:14px; max-width:420px; line-height:1.6;">
    1·2단계 리스트 복원 성공!<br>
    3·4단계부터는 <b>본부 관제 요원</b>과 <b>현장 탐색 요원</b>의 역할이 서로 바뀝니다!
  </p>
  <button class="btn-rpg" style="font-size:15px; padding:10px 22px; margin-top:10px;" onclick="closeSwitchModal()">
    🚀 바뀐 역할로 출발하기!
  </button>
</div>

<div id="completeModal" class="overlay-modal hidden">
  <img id="completeImgEl" class="complete-img" alt="Mission Complete" />
  <h3 id="completeHeader" style="color:#ffd166; margin:4px 0 8px 0; font-size:16px;"></h3>
  <div class="summary-list" id="completeList"></div>
  <div style="color:#4cc9f0; font-weight:bold; font-size:13.5px;">
    📸 이 화면을 캡처해서 우리 반 Padlet에 업로드해 주세요!
  </div>
</div>

<script>
const CFG = __CONFIG_JSON__;

function hashSeed(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}
function makeRng(seedStr) {
  let s = hashSeed(seedStr);
  return function() {
    s += 0x6D2B79F5;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffleWithRng(arr, rng) {
  const copy = arr.slice();
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

const MISSIONS = {
  "Kitchen": {
    roomKo: "주방 (Kitchen)",
    icon: "🔥",
    cardCrop: [0, 0],
    silhouette: "네모난 조리 기구 그림자",
    baseWord: "stove",
    prefix: "There is a",
    suffix: ".",
    targetWord: "stove",
    question: "What's in the kitchen?",
    options: ["There is a stove.", "There are a stove.", "There is two stoves."],
    answer: "There is a stove.",
    tip: "가스레인지가 1개(단수)이므로 'There is a stove.'예요!"
  },
  "Bedroom": {
    roomKo: "침실 (Bedroom)",
    icon: "🛏️🛏️",
    cardCrop: [1, 0],
    silhouette: "푹신한 침대 그림자",
    baseWord: "bed",
    prefix: "There are two",
    suffix: ".",
    targetWord: "beds",
    question: "What's in the bedroom?",
    options: ["There is two beds.", "There are two beds.", "There are a bed."],
    answer: "There are two beds.",
    tip: "침대가 2개(복수)이므로 뒤에 '-s'를 붙여 'beds'를 써요!"
  },
  "Living Room": {
    roomKo: "거실 (Living Room)",
    icon: "📺",
    cardCrop: [0, 1],
    silhouette: "네모난 화면 가전 그림자",
    baseWord: "TV",
    prefix: "There is a",
    suffix: ".",
    targetWord: "tv",
    question: "What's in the living room?",
    options: ["There are a TV.", "There is two TVs.", "There is a TV."],
    answer: "There is a TV.",
    tip: "TV가 1개(단수)이므로 'There is a TV.'예요!"
  },
  "Garden": {
    roomKo: "정원 (Garden)",
    icon: "🌲🌲🌲",
    cardCrop: [1, 1],
    silhouette: "눈 덮인 초록 나무 그림자",
    baseWord: "tree",
    prefix: "There are three",
    suffix: ".",
    targetWord: "trees",
    question: "What's in the garden?",
    options: ["There is three trees.", "There are three trees.", "There are a tree."],
    answer: "There are three trees.",
    tip: "나무가 3그루(복수)이므로 뒤에 '-s'를 붙여 'trees'를 써요!"
  }
};

const ROOM_SPOTS = {
  "Kitchen": [
    { x: 185, y: 250 }, { x: 390, y: 250 },
    { x: 185, y: 405 }, { x: 395, y: 405 }
  ],
  "Bedroom": [
    { x: 600, y: 250 }, { x: 745, y: 250 },
    { x: 600, y: 405 }, { x: 745, y: 405 }
  ],
  "Living Room": [
    { x: 185, y: 600 }, { x: 400, y: 600 },
    { x: 185, y: 810 }, { x: 400, y: 810 }
  ],
  "Garden": [
    { x: 600, y: 600 }, { x: 735, y: 625 },
    { x: 600, y: 740 }, { x: 745, y: 760 }
  ]
};

const DECOYS = [
  { emoji: "🐱", msg: "야옹~ 낮잠 자는 고양이(Cat)네요! 찾는 물건이 아니에요." },
  { emoji: "🧦", msg: "구멍 난 산타 양말(Sock)이에요! 다른 반짝이(✨)를 찾아보세요." },
  { emoji: "🧸", msg: "낡은 곰인형(Teddy Bear)이에요! 방 구석구석을 더 살펴보세요." }
];

const HOUSE_WALLS = [
  [0, 0, 1000, 58], [0, 942, 1000, 58], [0, 0, 58, 1000], [942, 0, 58, 1000],
  [455, 0, 90, 235], [455, 345, 90, 655],
  [0, 455, 205, 90], [295, 455, 160, 90],
  [545, 455, 160, 90], [795, 455, 160, 90],
  [58, 58, 385, 145], [58, 203, 75, 220],
  [555, 58, 210, 140], [800, 120, 142, 110], [880, 245, 62, 85], [800, 340, 142, 110],
  [58, 555, 82, 125], [58, 710, 68, 160], [135, 870, 185, 72],
  [790, 555, 152, 165], [560, 785, 135, 157], [810, 785, 132, 157]
];

const HQ_WALLS = [
  [0, 0, 1000, 80], [0, 920, 1000, 80], [0, 0, 70, 1000], [930, 0, 70, 1000],
  [360, 170, 280, 110],
  [140, 640, 170, 110],
  [415, 640, 170, 110],
  [690, 640, 170, 110]
];

function buildTeamPlan(teamCode) {
  const rng = makeRng(teamCode);
  const rooms = shuffleWithRng(Object.keys(MISSIONS), rng);
  return rooms.map(room => {
    const spots = shuffleWithRng(ROOM_SPOTS[room], rng);
    return {
      room,
      targetSpot: spots[0],
      decoys: [
        { ...spots[1], ...DECOYS[0] },
        { ...spots[2], ...DECOYS[1] },
        { ...spots[3], ...DECOYS[2] }
      ]
    };
  });
}

const TEAM_PLAN = buildTeamPlan(CFG.teamCode);

let roundIdx = 0;
let player = { x: 250, y: 295, dir: "down", walkFrame: 0 };
let checkedSpots = new Set();
let wordSolved = false;
let hqBriefed = false;
let nearObj = null;
let keys = {};
let lastTime = 0;

const houseImg = new Image();
if (CFG.imgMap) houseImg.src = "data:image/png;base64," + CFG.imgMap;

const cardsImg = new Image();
if (CFG.imgCards) cardsImg.src = "data:image/png;base64," + CFG.imgCards;

if (CFG.imgComplete) {
  document.getElementById("completeImgEl").src = "data:image/png;base64," + CFG.imgComplete;
}

function getActiveRole() {
  if (roundIdx < 2) return CFG.initialRole;
  return CFG.initialRole === "A" ? "B" : "A";
}

function resetPositionForRole() {
  const role = getActiveRole();
  if (role === "B") {
    player = { x: 250, y: 295, dir: "down", walkFrame: 0 };
  } else {
    player = { x: 500, y: 450, dir: "up", walkFrame: 0 };
  }
  checkedSpots = new Set();
  wordSolved = false;
  hqBriefed = false;
  updateHudAndPrompt();
}

function setDialogue(speaker, text, interactiveHtml = "") {
  document.getElementById("dlgSpeaker").innerHTML = speaker;
  document.getElementById("dlgText").innerHTML = text;
  document.getElementById("dlgInteractive").innerHTML = interactiveHtml;
}

function updateInventoryUI() {
  for (let i = 0; i < 4; i++) {
    const el = document.getElementById("slot" + i);
    const m = MISSIONS[TEAM_PLAN[i].room];
    if (i < roundIdx) {
      el.className = "inv-slot done";
      el.innerHTML = `✅ ${m.icon} ${m.answer}`;
    } else if (i === roundIdx) {
      el.className = "inv-slot";
      el.innerHTML = `🔍 ${i + 1}단계 조사 중...`;
    } else {
      el.className = "inv-slot";
      el.innerHTML = `🔒 ${i + 1}단계 잠김`;
    }
  }
}

function updateHudAndPrompt() {
  updateInventoryUI();
  if (roundIdx >= 4) {
    showCompleteScreen();
    return;
  }
  const role = getActiveRole();
  document.getElementById("hudStage").innerText = `퀘스트: ${roundIdx + 1} / 4`;
  const badge = document.getElementById("hudRoleBadge");

  if (role === "B") {
    badge.innerText = "🕹️ 현장 요원";
    badge.className = "badge-role";
    setDialogue(
      "🎅 산타 본부 무전",
      `짝(본부 요원)이 알려주는 방으로 이동해 반짝이(<b>✨</b>) 앞에서 <b>[조사/대화]</b> 버튼을 누르세요!`
    );
  } else {
    badge.innerText = "🎧 본부 요원";
    badge.className = "badge-role hq";
    setDialogue(
      "📡 본부 관제실 안내",
      `위쪽 <b>산타 지령 데스크</b>로 걸어가 <b>[조사/대화]</b>를 눌러 이번 라운드 지령을 확인하세요!`
    );
  }
}

function closeSwitchModal() {
  document.getElementById("switchModal").classList.add("hidden");
  resetPositionForRole();
}

function advanceRound() {
  roundIdx++;
  if (roundIdx === 2) {
    updateInventoryUI();
    document.getElementById("switchModal").classList.remove("hidden");
  } else if (roundIdx >= 4) {
    updateInventoryUI();
    showCompleteScreen();
  } else {
    resetPositionForRole();
  }
}

function showCompleteScreen() {
  document.getElementById("completeHeader").innerText =
    `🎉 [${CFG.teamCode} - ${CFG.playerName}] 선물 리스트 복원 완료!`;
  let listHtml = "";
  TEAM_PLAN.forEach((step, idx) => {
    const m = MISSIONS[step.room];
    listHtml += `<div><b>${idx + 1}. ${m.roomKo}</b> : <span style="color:#ffd166;">${m.answer}</span> (${m.icon})</div>`;
  });
  document.getElementById("completeList").innerHTML = listHtml;
  document.getElementById("completeModal").classList.remove("hidden");
}

function triggerAction() {
  if (roundIdx >= 4 || !nearObj) return;
  const role = getActiveRole();
  const step = TEAM_PLAN[roundIdx];
  const m = MISSIONS[step.room];

  if (role === "B") {
    const key = `${nearObj.x},${nearObj.y}`;
    checkedSpots.add(key);

    if (nearObj.type === "target") {
      renderTargetDialogue(m);
    } else {
      setDialogue("🔍 조사 결과", `${nearObj.emoji} ${nearObj.msg}`);
    }
  } else {
    if (nearObj.type === "santa_desk") {
      hqBriefed = true;
      setDialogue(
        "🎅 산타 클로스 (긴급 지령)",
        `1️⃣ 이동 지시: <b style="color:#ffd166;">"Go to the ${step.room.toLowerCase()}!"</b><br>` +
        `2️⃣ 힌트: <i>${m.silhouette}</i><br>` +
        `3️⃣ 질문하기: <b style="color:#4cc9f0;">"${m.question}"</b><br>` +
        `<span style="font-size:11.5px;color:#cbd5e1;">▶ 짝의 대답을 듣고 아래 <b>1·2·3번 컴퓨터</b> 중 맞는 문장을 조사하세요!</span>`
      );
    } else if (nearObj.type === "terminal") {
      if (!hqBriefed) {
        setDialogue("⚠️ 관제 시스템", "먼저 위쪽 <b>산타 지령 데스크</b>로 가서 이번 단계 지령부터 확인하세요!");
        return;
      }
      const optText = m.options[nearObj.idx];
      const html = `
        <div style="background:#1b263b;padding:7px;border-radius:8px;border:1px solid #4cc9f0;">
          <div style="font-size:12.5px;margin-bottom:5px;">해독 문장: <b style="color:#ffd166;">"${optText}"</b></div>
          <button class="btn-rpg blue" onclick="submitTerminal(${nearObj.idx})">✨ 이 문장으로 리스트 복원하기</button>
          <div id="termFeedback" class="feedback-msg"></div>
        </div>
      `;
      setDialogue(`💻 해독 컴퓨터 #${nearObj.idx + 1}`, "짝이 말한 영어 대답과 일치하나요?", html);
    }
  }
}

function renderTargetDialogue(m) {
  if (!wordSolved) {
    const html = `
      <div class="card-preview">
        <canvas id="cardCanvas" width="160" height="160"></canvas>
        <div style="font-size:12px;">
          <b style="color:#06d6a0;">목표 물건 발견!</b><br>
          단어 힌트: <b style="color:#ffd166;">${m.baseWord}</b><br>
          개수를 세어 빈칸에 단어를 넣으세요!
        </div>
      </div>
      <div class="word-form">
        <b>${m.prefix}</b>
        <input id="wordInput" class="word-input" type="text" placeholder="단어 입력" autocomplete="off" />
        <b>${m.suffix}</b>
        <button class="btn-rpg" onclick="checkWordInput()">확인</button>
      </div>
      <div id="wordFeedback" class="feedback-msg"></div>
    `;
    setDialogue(`🎁 발견! (${m.roomKo})`, "그림 속 물건의 개수를 보고 문장을 완성하세요!", html);
    drawCroppedCard(m.cardCrop);
  } else {
    const html = `
      <div style="background:#1b4332;padding:7px 9px;border-radius:8px;border:1px solid #52b788;margin-bottom:6px;">
        <div style="font-size:11.5px;color:#b7e4c7;">완성된 문장을 짝에게 큰 소리로 말하세요!</div>
        <div style="font-size:15px;font-weight:bold;color:#fff;margin-top:2px;">🗣️ "${m.answer}"</div>
      </div>
      <button class="btn-rpg" onclick="advanceRound()">✅ 영어 보고 완료! 다음 단계로</button>
    `;
    setDialogue("🎉 문장 완성 성공!", "짝이 질문하면 위 문장으로 대답한 뒤 버튼을 누르세요!", html);
  }
}

function drawCroppedCard(cropCoords) {
  setTimeout(() => {
    const c = document.getElementById("cardCanvas");
    if (!c) return;
    const ctx = c.getContext("2d");
    if (cardsImg.complete && cardsImg.naturalWidth > 0) {
      const sw = cardsImg.naturalWidth / 2;
      const sh = cardsImg.naturalHeight / 2;
      ctx.drawImage(cardsImg, cropCoords[0] * sw, cropCoords[1] * sh, sw, sh, 0, 0, 160, 160);
    } else {
      ctx.fillStyle = "#1d3557";
      ctx.fillRect(0, 0, 160, 160);
      ctx.fillStyle = "#fff";
      ctx.font = "bold 20px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(MISSIONS[TEAM_PLAN[roundIdx].room].icon, 80, 90);
    }
  }, 30);
}

window.checkWordInput = function() {
  const m = MISSIONS[TEAM_PLAN[roundIdx].room];
  const raw = (document.getElementById("wordInput")?.value || "").trim().toLowerCase().replace(/\.$/, "");
  const fb = document.getElementById("wordFeedback");
  if (raw === m.targetWord) {
    wordSolved = true;
    renderTargetDialogue(m);
  } else if (raw === m.baseWord.toLowerCase() && m.targetWord.endsWith("s")) {
    fb.style.color = "#ffd166";
    fb.innerText = `💡 아깝다! 물건이 여러 개예요. '${m.baseWord}' 뒤에 '-s'를 붙여볼까요?`;
  } else {
    fb.style.color = "#ff6b6b";
    fb.innerText = `❌ 다시 확인해 보세요! 단어 힌트 '${m.baseWord}'를 개수에 맞게 넣어보세요.`;
  }
};

window.submitTerminal = function(idx) {
  const m = MISSIONS[TEAM_PLAN[roundIdx].room];
  const fb = document.getElementById("termFeedback");
  if (m.options[idx] === m.answer) {
    advanceRound();
  } else {
    fb.style.color = "#ff6b6b";
    fb.innerText = `❌ 짝의 대답을 다시 들어보세요! (${m.tip})`;
  }
};

function collides(nx, ny, walls) {
  const r = 22;
  for (const [wx, wy, ww, wh] of walls) {
    if (nx + r > wx && nx - r < wx + ww && ny + r > wy && ny - r < wy + wh) {
      return true;
    }
  }
  return false;
}

function getCurrentRoomLabel(x, y) {
  if (getActiveRole() === "A") return "📡 산타 관제실";
  if (x < 500 && y < 500) return "🍳 Kitchen";
  if (x >= 500 && y < 500) return "🛏️ Bedroom";
  if (x < 500 && y >= 500) return "🛋️ Living Room";
  return "🌳 Garden";
}

function updatePhysics(dt) {
  if (roundIdx >= 4 || !document.getElementById("switchModal").classList.contains("hidden")) return;
  if (document.activeElement && document.activeElement.tagName === "INPUT") return;

  let dx = 0, dy = 0;
  if (keys["ArrowUp"] || keys["w"] || keys["W"]) { dy -= 1; player.dir = "up"; }
  if (keys["ArrowDown"] || keys["s"] || keys["S"]) { dy += 1; player.dir = "down"; }
  if (keys["ArrowLeft"] || keys["a"] || keys["A"]) { dx -= 1; player.dir = "left"; }
  if (keys["ArrowRight"] || keys["d"] || keys["D"]) { dx += 1; player.dir = "right"; }

  const walls = getActiveRole() === "B" ? HOUSE_WALLS : HQ_WALLS;
  if (dx !== 0 || dy !== 0) {
    const len = Math.hypot(dx, dy);
    const speed = 260 * dt;
    const vx = (dx / len) * speed;
    const vy = (dy / len) * speed;
    if (!collides(player.x + vx, player.y, walls)) player.x += vx;
    if (!collides(player.x, player.y + vy, walls)) player.y += vy;
    player.walkFrame += dt * 10;
  } else {
    player.walkFrame = 0;
  }

  document.getElementById("hudLocation").innerText = "📍 " + getCurrentRoomLabel(player.x, player.y);

  nearObj = null;
  let minDist = 72;

  if (getActiveRole() === "B") {
    const step = TEAM_PLAN[roundIdx];
    const allSpots = [
      { ...step.targetSpot, type: "target" },
      ...step.decoys.map(d => ({ ...d, type: "decoy" }))
    ];
    for (const sp of allSpots) {
      const d = Math.hypot(player.x - sp.x, player.y - sp.y);
      if (d < minDist) { minDist = d; nearObj = sp; }
    }
  } else {
    const hqObjs = [
      { x: 500, y: 310, type: "santa_desk" },
      { x: 225, y: 615, type: "terminal", idx: 0 },
      { x: 500, y: 615, type: "terminal", idx: 1 },
      { x: 775, y: 615, type: "terminal", idx: 2 }
    ];
    for (const obj of hqObjs) {
      const d = Math.hypot(player.x - obj.x, player.y - obj.y);
      if (d < 85 && d < minDist + 15) { minDist = d; nearObj = obj; }
    }
  }

  const actBtn = document.getElementById("btnAction");
  if (nearObj) actBtn.classList.add("ready");
  else actBtn.classList.remove("ready");
}

const canvas = document.getElementById("rpgCanvas");
const ctx = canvas.getContext("2d");

function drawPixelAgent(x, y, role) {
  const px = x / 2;
  const py = y / 2;
  const bob = Math.sin(player.walkFrame) * 2.5;

  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.beginPath();
  ctx.ellipse(px, py + 12, 11, 5, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = role === "B" ? "#e63946" : "#3a86ff";
  ctx.fillRect(px - 9, py - 4 + bob, 18, 14);

  ctx.fillStyle = "#1d1e2c";
  ctx.fillRect(px - 9, py + 4 + bob, 18, 3);
  ctx.fillStyle = "#ffd166";
  ctx.fillRect(px - 2, py + 3.5 + bob, 4, 4);

  ctx.fillStyle = "#ffcdb2";
  ctx.beginPath();
  ctx.arc(px, py - 10 + bob, 9, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#111";
  ctx.fillRect(px - 4, py - 11 + bob, 2.5, 2.5);
  ctx.fillRect(px + 2, py - 11 + bob, 2.5, 2.5);

  ctx.fillStyle = role === "B" ? "#d62828" : "#0077b6";
  ctx.beginPath();
  ctx.moveTo(px - 10, py - 15 + bob);
  ctx.lineTo(px + 10, py - 15 + bob);
  ctx.lineTo(px + 4, py - 26 + bob);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#fff";
  ctx.fillRect(px - 10, py - 17 + bob, 20, 3.5);
  ctx.beginPath();
  ctx.arc(px + 5, py - 26 + bob, 3.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "rgba(0,0,0,0.7)";
  ctx.fillRect(px - 15, py - 39 + bob, 30, 11);
  ctx.fillStyle = "#ffd166";
  ctx.font = "bold 8px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("YOU", px, py - 31 + bob);
}

function drawHqMap(now) {
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(0, 0, 500, 500);
  ctx.strokeStyle = "#273549";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 500; i += 25) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, 500); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(500, i); ctx.stroke();
  }
  ctx.fillStyle = "#475569";
  ctx.fillRect(0, 0, 500, 40);
  ctx.fillRect(0, 460, 500, 40);
  ctx.fillRect(0, 0, 35, 500);
  ctx.fillRect(465, 0, 35, 500);

  ctx.fillStyle = "#8d5b4c";
  ctx.fillRect(180, 85, 140, 55);
  ctx.strokeStyle = "#ffd166";
  ctx.lineWidth = 2;
  ctx.strokeRect(180, 85, 140, 55);

  ctx.font = "28px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("🎅", 250, 78);
  ctx.font = "bold 12px sans-serif";
  ctx.fillStyle = "#ffd166";
  ctx.fillText("📡 산타 지령 데스크", 250, 117);

  const terms = [
    { x: 112, label: "💻 컴퓨터 #1" },
    { x: 250, label: "💻 컴퓨터 #2" },
    { x: 387, label: "💻 컴퓨터 #3" }
  ];
  const m = MISSIONS[TEAM_PLAN[roundIdx].room];
  terms.forEach((t, idx) => {
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(t.x - 42, 320, 84, 55);
    ctx.strokeStyle = "#4cc9f0";
    ctx.lineWidth = 2;
    ctx.strokeRect(t.x - 42, 320, 84, 55);
    ctx.fillStyle = "#4cc9f0";
    ctx.font = "bold 11px sans-serif";
    ctx.fillText(t.label, t.x, 342);
    ctx.fillStyle = "#e2e8f0";
    ctx.font = "10px sans-serif";
    ctx.fillText(m.options[idx], t.x, 360);
  });
}
function renderLoop(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  updatePhysics(dt);

  ctx.clearRect(0, 0, 500, 500);
  const role = getActiveRole();

  if (role === "B") {
    if (houseImg.complete && houseImg.naturalWidth > 0) {
      ctx.drawImage(houseImg, 0, 0, 500, 500);
    } else {
      ctx.fillStyle = "#f4e8c1";
      ctx.fillRect(0, 0, 500, 500);
    }

    if (roundIdx < 4) {
      const step = TEAM_PLAN[roundIdx];
      const allSpots = [
        { ...step.targetSpot, type: "target" },
        ...step.decoys.map(d => ({ ...d, type: "decoy" }))
      ];
      const pulse = Math.sin(now / 220) * 3;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      for (const sp of allSpots) {
        const sx = sp.x / 2;
        const sy = sp.y / 2;
        const k = `${sp.x},${sp.y}`;
        if (checkedSpots.has(k)) {
          ctx.font = "20px sans-serif";
          ctx.fillText(sp.type === "target" ? "🎁" : sp.emoji, sx, sy);
        } else {
          ctx.fillStyle = "rgba(255, 215, 0, 0.35)";
          ctx.beginPath();
          ctx.arc(sx, sy, 11 + pulse * 0.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.font = "18px sans-serif";
          ctx.fillText("✨", sx, sy + pulse * 0.4);
        }
      }
    }
  } else {
    drawHqMap(now);
  }

  drawPixelAgent(player.x, player.y, role);

  if (nearObj) {
    const bx = player.x / 2;
    const by = player.y / 2 - 28;
    ctx.fillStyle = "#06d6a0";
    ctx.beginPath();
    ctx.roundRect(bx - 22, by - 12, 44, 16, 6);
    ctx.fill();
    ctx.fillStyle = "#073b4c";
    ctx.font = "bold 10px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("조사!", bx, by - 4);
  }

  requestAnimationFrame(renderLoop);
}

window.addEventListener("keydown", (e) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(e.key)) {
    if (document.activeElement?.tagName !== "INPUT") e.preventDefault();
  }
  keys[e.key] = true;
  if (e.key === " " && document.activeElement?.tagName !== "INPUT") {
    triggerAction();
  }
});
window.addEventListener("keyup", (e) => { keys[e.key] = false; });

function bindTouchBtn(btnId, keyName) {
  const btn = document.getElementById(btnId);
  const press = (e) => {
    if (e.cancelable) e.preventDefault();
    keys[keyName] = true;
    btn.classList.add("pressed");
  };
  const release = (e) => {
    if (e.cancelable) e.preventDefault();
    keys[keyName] = false;
    btn.classList.remove("pressed");
  };
  btn.addEventListener("pointerdown", press);
  btn.addEventListener("pointerup", release);
  btn.addEventListener("pointerleave", release);
  btn.addEventListener("pointercancel", release);
  btn.addEventListener("touchstart", press, { passive: false });
  btn.addEventListener("touchend", release, { passive: false });
}
bindTouchBtn("btnUp", "ArrowUp");
bindTouchBtn("btnDown", "ArrowDown");
bindTouchBtn("btnLeft", "ArrowLeft");
bindTouchBtn("btnRight", "ArrowRight");

document.getElementById("btnAction").addEventListener("click", triggerAction);

resetPositionForRole();
requestAnimationFrame(renderLoop);
</script>
</body>
</html>
"""

html_code = html_template.replace("__CONFIG_JSON__", config_json)
components.html(html_code, height=820, scrolling=True)
