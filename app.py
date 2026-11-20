import base64
import json
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Santa's Dream House RPG",
    page_icon="🎅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; max-width: 980px; }
        header[data-testid="stHeader"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

def load_b64_any(candidates: list[str]) -> str:
    for path in candidates:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

IMG_MAP = load_b64_any(["house_map.png", "house_map.jpg"])
IMG_CARDS = load_b64_any(["cards.png", "cards.jpg"])
IMG_EXTRA = load_b64_any(["extra_cards.jpg", "extra_cards.png"])
IMG_COMPLETE = load_b64_any(["complete.png", "complete.jpg"])

if "started" not in st.session_state:
    st.session_state.started = False

# ==========================================
# 1. 초간편 1인 1태블릿 입장 화면
# ==========================================
if not st.session_state.started:
    st.markdown("## 🎅 Santa's Dream House : 2D English RPG")
    st.markdown("커피가 쏟아져 지워진 **산타의 선물 리스트 8가지**를 찾아 영어로 듣고, 쓰고, 말해보세요!")
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        player_name = st.text_input(
            "✏️ 내 번호와 이름을 입력하세요 (예: 5-1 김민수)",
            placeholder="이름을 입력하고 시작 버튼을 누르세요!"
        )
    with col2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        start_btn = st.button("🚀 산타 하우스 입장!", type="primary", use_container_width=True)

    if start_btn:
        st.session_state.player_name = player_name.strip() if player_name.strip() else "산타 요원"
        st.session_state.started = True
        st.rerun()

    st.info("💡 **게임 방법:** 방향키(또는 화면 터치)로 이동 ➔ 반짝이(`✨`) 조사 ➔ **① 원어민 듣기 ➔ ② 문장 쓰기 ➔ ③ 따라 읽기**로 8개 보물을 모두 모으세요!")
    st.stop()

top1, top2 = st.columns([4.5, 1])
with top1:
    st.markdown(f"🎄 **플레이어:** `{st.session_state.player_name}` | 🎯 **목표:** 4개 방의 8가지 물건 리스트 복원하기")
with top2:
    if st.button("🔄 처음부터", use_container_width=True):
        st.session_state.started = False
        st.rerun()

config_json = json.dumps({
    "playerName": st.session_state.player_name,
    "imgMap": IMG_MAP,
    "imgCards": IMG_CARDS,
    "imgExtra": IMG_EXTRA,
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

  .game-shell {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    background: radial-gradient(circle at top left, #241b4b 0%, #121629 100%);
    border: 3px solid #ffd166;
    border-radius: 16px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.45);
  }

  /* 왼쪽 맵 영역 */
  .map-column {
    flex: 1 1 420px;
    max-width: 470px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .top-hud {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.92);
    border: 2px solid #4cc9f0;
    border-radius: 10px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: bold;
  }
  .progress-wrap {
    width: 100%;
    height: 10px;
    background: #1e293b;
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid #475569;
  }
  .progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #06d6a0, #ffd166);
    transition: width 0.4s ease;
  }
  canvas#rpgCanvas {
    width: 100%;
    aspect-ratio: 1 / 1;
    display: block;
    border-radius: 12px;
    border: 3px solid #ffd166;
    background: #1e293b;
    box-shadow: 0 8px 22px rgba(0,0,0,0.55);
    cursor: pointer;
  }

  /* 오른쪽 학습 & 컨트롤 영역 */
  .ui-column {
    flex: 1 1 340px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
  }

  /* 8칸 도감 인벤토리 */
  .dex-box {
    background: rgba(15, 23, 42, 0.92);
    border: 2px solid #ffd166;
    border-radius: 12px;
    padding: 8px 10px;
  }
  .dex-header {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: bold;
    color: #ffd166;
    margin-bottom: 6px;
  }
  .dex-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
  }
  .dex-slot {
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 7px;
    padding: 4px;
    text-align: center;
    font-size: 10.5px;
    color: #94a3b8;
  }
  .dex-slot.active {
    border: 2px solid #4cc9f0;
    background: #172554;
    color: #e0f2fe;
    animation: glowBorder 1.4s infinite;
  }
  .dex-slot.done {
    background: #14532d;
    border-color: #4ade80;
    color: #dcfce7;
    font-weight: bold;
  }
  @keyframes glowBorder {
    0%, 100% { box-shadow: 0 0 4px #4cc9f0; }
    50% { box-shadow: 0 0 12px #4cc9f0; }
  }

  /* RPG 대화 및 3단 영어 미션 창 */
  .quest-panel {
    flex: 1;
    background: #0b1120;
    border: 3px solid #f8fafc;
    box-shadow: inset 0 0 0 2px #3b82f6;
    border-radius: 12px;
    padding: 12px;
    min-height: 255px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .q-title {
    font-size: 13.5px;
    font-weight: bold;
    color: #ffd166;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 5px;
    margin-bottom: 7px;
    display: flex;
    justify-content: space-between;
  }
  .q-body {
    font-size: 13.5px;
    line-height: 1.5;
    color: #f1f5f9;
  }

  .card-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #172033;
    border: 1px solid #334155;
    padding: 7px;
    border-radius: 9px;
    margin-bottom: 8px;
  }
  canvas#cardPreview {
    width: 78px;
    height: 78px;
    border-radius: 8px;
    border: 2px solid #ffd166;
    background: #fff;
    flex-shrink: 0;
  }

  .step-badge {
    display: inline-block;
    background: #3b82f6;
    color: #fff;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 7px;
    border-radius: 5px;
    margin-bottom: 5px;
  }
  .audio-btns {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 6px;
  }
  .btn-game {
    background: #06d6a0;
    color: #052e16;
    border: none;
    border-radius: 7px;
    padding: 7px 11px;
    font-size: 12.5px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 3px 0 #047857;
    transition: transform 0.08s;
  }
  .btn-game:active { transform: translateY(2px); box-shadow: 0 1px 0 #047857; }
  .btn-game.sky { background: #38bdf8; color: #082f49; box-shadow: 0 3px 0 #0369a1; }
  .btn-game.amber { background: #fbbf24; color: #451a03; box-shadow: 0 3px 0 #b45309; }
  .btn-game.rose { background: #fb7185; color: #4c0519; box-shadow: 0 3px 0 #be123c; }
  .btn-game.ghost { background: #334155; color: #e2e8f0; box-shadow: 0 3px 0 #1e293b; font-size: 11.5px; }

  .chip-area {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 6px 0;
  }
  .word-chip {
    background: #1e3a8a;
    color: #dbeafe;
    border: 1px solid #60a5fa;
    border-radius: 6px;
    padding: 4px 9px;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
  }
  .word-chip:active { background: #ffd166; color: #111; }

  .write-box {
    display: flex;
    gap: 6px;
    margin-top: 5px;
  }
  .sentence-input {
    flex: 1;
    padding: 7px 10px;
    font-size: 14px;
    font-weight: bold;
    border-radius: 7px;
    border: 2px solid #ffd166;
    background: #fff;
    color: #0f172a;
    user-select: text;
    -webkit-user-select: text;
  }

  .mic-status {
    background: #1e293b;
    border: 1px dashed #64748b;
    border-radius: 7px;
    padding: 6px 9px;
    font-size: 12px;
    margin-top: 6px;
    color: #cbd5e1;
  }
  .fb-line {
    font-size: 12px;
    font-weight: bold;
    margin-top: 5px;
  }

  /* 하단 방향키 & 조사 버튼 */
  .pad-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.95);
    border: 2px solid #475569;
    border-radius: 12px;
    padding: 8px 14px;
  }
  .dpad {
    display: grid;
    grid-template-columns: 46px 46px 46px;
    grid-template-rows: 40px 40px 40px;
    gap: 3px;
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

  .act-btn {
    width: 124px;
    height: 86px;
    border-radius: 14px;
    border: 3px solid #ffd166;
    background: #e11d48;
    color: #fff;
    font-size: 14.5px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 5px 0 #881337;
    touch-action: manipulation;
  }
  .act-btn.near {
    background: #10b981;
    color: #022c22;
    box-shadow: 0 5px 0 #065f46;
    animation: bounceBtn 0.9s infinite;
  }
  @keyframes bounceBtn {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }

  /* 모바일 & 태블릿 세로 최적화 */
  @media (max-width: 768px) {
    .game-shell { padding: 8px; gap: 8px; }
    .map-column { flex: 1 1 100%; max-width: 100%; }
    canvas#rpgCanvas { max-width: 275px; margin: 0 auto; }
    .ui-column { flex: 1 1 100%; gap: 8px; }
    .quest-panel { order: 1; min-height: 195px; padding: 9px; }
    .pad-bar { order: 2; padding: 6px 12px; }
    .dex-box { order: 3; }
  }

  /* 엔딩 인증서 오버레이 */
  .ending-screen {
    position: fixed;
    inset: 0;
    background: rgba(9, 13, 28, 0.96);
    z-index: 100;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16px;
    text-align: center;
    overflow-y: auto;
  }
  .ending-screen.hidden { display: none; }
  .cert-img {
    max-width: 360px;
    width: 86%;
    border-radius: 12px;
    border: 3px solid #ffd166;
    margin-bottom: 10px;
  }
  .cert-board {
    background: #1e293b;
    border: 2px solid #38bdf8;
    border-radius: 12px;
    padding: 10px 16px;
    max-width: 520px;
    width: 95%;
    text-align: left;
    font-size: 12.5px;
    line-height: 1.65;
    margin-bottom: 10px;
  }
</style>
</head>
<body>

<div class="game-shell">
  <!-- 왼쪽: 2D RPG 맵 -->
  <div class="map-column">
    <div class="top-hud">
      <span id="hudRoom">📍 Kitchen</span>
      <span id="hudQuest">보물: 0 / 8</span>
      <span id="hudScore" style="color:#ffd166;">⭐ 0 PTS</span>
    </div>
    <div class="progress-wrap"><div class="progress-fill" id="progressFill"></div></div>
    <canvas id="rpgCanvas" width="520" height="520"></canvas>
  </div>

  <!-- 오른쪽: 도감 + 3단 영어 미션창 + 방향키 -->
  <div class="ui-column">
    <div class="dex-box">
      <div class="dex-header">
        <span>📜 산타의 선물 리스트 도감 (8종)</span>
        <span id="hudStars">획득 별: 0⭐</span>
      </div>
      <div class="dex-grid" id="dexGrid"></div>
    </div>

    <div class="quest-panel">
      <div>
        <div class="q-title">
          <span id="qSpeaker">🎅 산타 클로스</span>
          <span id="qBadge" style="color:#38bdf8;">탐험 중</span>
        </div>
        <div class="q-body" id="qBody"></div>
      </div>
      <div id="qFooter" style="font-size:11px; color:#94a3b8; margin-top:6px;">
        💡 화면의 맵을 직접 터치하거나 방향키로 움직여 보세요!
      </div>
    </div>

    <div class="pad-bar">
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
      <button id="btnAction" type="button" class="act-btn">🔍 조사하기<br><span style="font-size:11px;font-weight:normal;">(Space)</span></button>
    </div>
  </div>
</div>

<!-- 클리어 인증 화면 (Padlet 업로드용) -->
<div id="endingScreen" class="ending-screen hidden">
  <img id="certImgEl" class="cert-img" alt="Mission Complete" />
  <h3 id="certTitle" style="color:#ffd166; margin:4px 0 8px 0;"></h3>
  <div class="cert-board" id="certBoard"></div>
  <div style="color:#38bdf8; font-weight:bold; font-size:14px;">
    📸 이 화면을 캡처해서 우리 반 Padlet에 올려주세요!
  </div>
</div>

<script>
const CFG = __CONFIG_JSON__;

// ==========================================
// 1. Web Audio API 레트로 RPG 효과음 합성기 (외부 파일 불필요)
// ==========================================
let audioCtx = null;
function playSfx(type) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    const now = audioCtx.currentTime;

    const playTone = (freq, start, dur, wave = "triangle", vol = 0.14) => {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = wave;
      osc.frequency.setValueAtTime(freq, now + start);
      gain.gain.setValueAtTime(vol, now + start);
      gain.gain.exponentialRampToValueAtTime(0.001, now + start + dur);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(now + start);
      osc.stop(now + start + dur);
    };

    if (type === "coin") {
      playTone(987.77, 0, 0.08, "sine", 0.15);
      playTone(1318.51, 0.07, 0.18, "sine", 0.15);
    } else if (type === "discover") {
      playTone(523.25, 0, 0.1, "triangle");
      playTone(659.25, 0.09, 0.1, "triangle");
      playTone(783.99, 0.18, 0.22, "triangle");
    } else if (type === "success") {
      playTone(523.25, 0, 0.1, "square", 0.09);
      playTone(659.25, 0.09, 0.1, "square", 0.09);
      playTone(783.99, 0.18, 0.1, "square", 0.09);
      playTone(1046.50, 0.27, 0.3, "square", 0.11);
    } else if (type === "error") {
      playTone(220, 0, 0.15, "sawtooth", 0.09);
      playTone(185, 0.12, 0.2, "sawtooth", 0.09);
    }
  } catch (e) {}
}

// ==========================================
// 2. 원어민 발음 TTS 엔진 (일반 속도 & 0.75배속)
// ==========================================
function speakEnglish(text, rate = 0.95) {
  try {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    utter.rate = rate;
    utter.pitch = 1.05;
    const voices = window.speechSynthesis.getVoices();
    const enVoice = voices.find(v => v.lang.includes("en-US") && (v.name.includes("Google") || v.name.includes("Samantha") || v.name.includes("Jenny")))
                 || voices.find(v => v.lang.includes("en"));
    if (enVoice) utter.voice = enVoice;
    window.speechSynthesis.speak(utter);
  } catch (e) {}
}
if (typeof window !== "undefined" && window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// ==========================================
// 3. 8개 순차 영어 퀘스트 데이터 (4개 방 × 2개 사물)
// ==========================================
const QUESTS = [
  {
    id: 0, room: "Kitchen", roomKo: "주방", label: "stove", icon: "🔥",
    sheet: "main", crop: [0, 0], x: 335, y: 245,
    question: "What's in the kitchen?",
    answer: "There is a stove.",
    chips: ["stove.", "There is", "a"],
    isPlural: false, noun: "stove",
    tip: "가스레인지가 1개(단수)이므로 'There is a stove.'로 써요!"
  },
  {
    id: 1, room: "Kitchen", roomKo: "주방", label: "sink", icon: "🚰",
    sheet: "extra", crop: [0, 0], x: 185, y: 245,
    question: "What's in the kitchen?",
    answer: "There is a sink.",
    chips: ["a", "sink.", "There is"],
    isPlural: false, noun: "sink",
    tip: "싱크대가 1개(단수)이므로 'There is a sink.'로 써요!"
  },
  {
    id: 2, room: "Bedroom", roomKo: "침실", label: "two beds", icon: "🛏️",
    sheet: "main", crop: [1, 0], x: 755, y: 285,
    question: "What's in the bedroom?",
    answer: "There are two beds.",
    chips: ["two", "There are", "beds."],
    isPlural: true, noun: "beds",
    tip: "침대가 2개(복수)이므로 'There are two beds.'로 써요!"
  },
  {
    id: 3, room: "Bedroom", roomKo: "침실", label: "closet", icon: "🚪",
    sheet: "extra", crop: [1, 0], x: 605, y: 245,
    question: "What's in the bedroom?",
    answer: "There is a closet.",
    chips: ["closet.", "There is", "a"],
    isPlural: false, noun: "closet",
    tip: "옷장이 1개(단수)이므로 'There is a closet.'로 써요!"
  },
  {
    id: 4, room: "Living Room", roomKo: "거실", label: "TV", icon: "📺",
    sheet: "main", crop: [0, 1], x: 190, y: 615,
    question: "What's in the living room?",
    answer: "There is a TV.",
    chips: ["TV.", "a", "There is"],
    isPlural: false, noun: "TV",
    tip: "TV가 1개(단수)이므로 'There is a TV.'로 써요!"
  },
  {
    id: 5, room: "Living Room", roomKo: "거실", label: "two sofas", icon: "🛋️",
    sheet: "extra", crop: [0, 1], x: 230, y: 815,
    question: "What's in the living room?",
    answer: "There are two sofas.",
    chips: ["sofas.", "There are", "two"],
    isPlural: true, noun: "sofas",
    tip: "소파가 2개(복수)이므로 'There are two sofas.'로 써요!"
  },
  {
    id: 6, room: "Garden", roomKo: "정원", label: "three trees", icon: "🌲",
    sheet: "main", crop: [1, 1], x: 735, y: 635,
    question: "What's in the garden?",
    answer: "There are three trees.",
    chips: ["trees.", "three", "There are"],
    isPlural: true, noun: "trees",
    tip: "나무가 3그루(복수)이므로 'There are three trees.'로 써요!"
  },
  {
    id: 7, room: "Garden", roomKo: "정원", label: "three gifts", icon: "🎁",
    sheet: "extra", crop: [1, 1], x: 655, y: 745,
    question: "What's in the garden?",
    answer: "There are three gifts.",
    chips: ["three", "gifts.", "There are"],
    isPlural: true, noun: "gifts",
    tip: "선물이 3개(복수)이므로 'There are three gifts.'로 써요!"
  }
];

// 맵 곳곳에 흩어진 보너스 아이템 12개 (수집 재미 + 점수)
let bonusItems = [
  { x: 260, y: 380, emoji: "🍬", collected: false },
  { x: 405, y: 310, emoji: "🔔", collected: false },
  { x: 680, y: 390, emoji: "🍬", collected: false },
  { x: 750, y: 495, emoji: "🔔", collected: false },
  { x: 250, y: 495, emoji: "🍬", collected: false },
  { x: 380, y: 620, emoji: "🔔", collected: false },
  { x: 390, y: 780, emoji: "🍬", collected: false },
  { x: 165, y: 720, emoji: "⭐", collected: false },
  { x: 610, y: 590, emoji: "🍬", collected: false },
  { x: 745, y: 745, emoji: "🔔", collected: false },
  { x: 500, y: 290, emoji: "⭐", collected: false },
  { x: 750, y: 850, emoji: "⭐", collected: false }
];

// 벽 및 가구 충돌 영역
const WALLS = [
  [0, 0, 1000, 58], [0, 942, 1000, 58], [0, 0, 58, 1000], [942, 0, 58, 1000],
  [455, 0, 90, 235], [455, 345, 90, 655],
  [0, 455, 205, 90], [295, 455, 160, 90],
  [545, 455, 160, 90], [795, 455, 160, 90],
  [58, 58, 385, 145], [58, 203, 75, 220],
  [555, 58, 210, 140], [800, 120, 142, 110], [880, 245, 62, 85], [800, 340, 142, 110],
  [58, 555, 82, 125], [58, 710, 68, 160], [135, 870, 185, 72],
  [790, 555, 152, 165], [560, 785, 135, 157], [810, 785, 132, 157]
];

// ==========================================
// 4. 게임 상태 & 파티클 효과 배열
// ==========================================
let currentIdx = 0;
let missionStage = "explore"; // explore | modal_write | modal_speak
let score = 0;
let totalStars = 0;
let speakAttempts = 0;
let earnedStarsList = [];

let player = { x: 260, y: 310, targetX: null, targetY: null, walkAnim: 0 };
const santaNpc = { x: 395, y: 375 };

let particles = [];
let floatingTexts = [];
let snowflakes = Array.from({ length: 38 }, () => ({
  x: Math.random() * 520,
  y: Math.random() * 520,
  r: 1.5 + Math.random() * 2.5,
  sp: 18 + Math.random() * 25,
  drift: Math.random() * Math.PI * 2
}));

let keys = {};
let nearTarget = false;
let nearSanta = false;
let lastTime = 0;

// 이미지 로드
const mapImg = new Image();
if (CFG.imgMap) mapImg.src = "data:image/png;base64," + CFG.imgMap;

const mainCardsImg = new Image();
if (CFG.imgCards) mainCardsImg.src = "data:image/png;base64," + CFG.imgCards;

const extraCardsImg = new Image();
if (CFG.imgExtra) extraCardsImg.src = "data:image/png;base64," + CFG.imgExtra;

if (CFG.imgComplete) {
  document.getElementById("certImgEl").src = "data:image/png;base64," + CFG.imgComplete;
}

function spawnBurst(x, y, colors, count = 22) {
  const px = (x / 1000) * 520;
  const py = (y / 1000) * 520;
  for (let i = 0; i < count; i++) {
    const ang = (Math.PI * 2 * i) / count + Math.random() * 0.3;
    const spd = 45 + Math.random() * 110;
    particles.push({
      x: px, y: py,
      vx: Math.cos(ang) * spd,
      vy: Math.sin(ang) * spd - 30,
      life: 0.7 + Math.random() * 0.4,
      maxLife: 1.1,
      size: 3 + Math.random() * 3.5,
      color: colors[i % colors.length]
    });
  }
}

function spawnFloatText(x, y, text, color = "#ffd166") {
  floatingTexts.push({
    x: (x / 1000) * 520,
    y: (y / 1000) * 520 - 18,
    text,
    color,
    life: 1.1
  });
}

// ==========================================
// 5. 도감 및 HUD UI 렌더링
// ==========================================
function renderDex() {
  const grid = document.getElementById("dexGrid");
  grid.innerHTML = "";
  QUESTS.forEach((q, idx) => {
    const div = document.createElement("div");
    if (idx < currentIdx) {
      div.className = "dex-slot done";
      div.innerHTML = `${q.icon} ${q.label}<br>✅ ${earnedStarsList[idx] || 3}⭐`;
    } else if (idx === currentIdx) {
      div.className = "dex-slot active";
      div.innerHTML = `✨ <b>${q.roomKo}</b><br>탐색 중!`;
    } else {
      div.className = "dex-slot";
      div.innerHTML = `🔒 #${idx + 1}<br>${q.roomKo}`;
    }
    grid.appendChild(div);
  });

  document.getElementById("hudQuest").innerText = `보물: ${currentIdx} / 8`;
  document.getElementById("hudScore").innerText = `⭐ ${score} PTS`;
  document.getElementById("hudStars").innerText = `획득 별: ${totalStars}⭐`;
  document.getElementById("progressFill").style.width = `${(currentIdx / 8) * 100}%`;
}

function setExplorePrompt() {
  missionStage = "explore";
  renderDex();
  if (currentIdx >= QUESTS.length) {
    showEnding();
    return;
  }
  const q = QUESTS[currentIdx];
  document.getElementById("qSpeaker").innerText = `🎅 퀘스트 #${currentIdx + 1} (${q.roomKo})`;
  document.getElementById("qBadge").innerText = "🗺️ 탐색 모드";
  document.getElementById("qBody").innerHTML = `
    <div style="margin-bottom:8px;">
      <b>${q.roomKo} (${q.room})</b> 구역에서 반짝이는 선물 단서(<b>✨</b>)를 찾아 <b>[조사하기]</b>를 누르세요!
    </div>
    <button class="btn-game sky" onclick="speakEnglish('${q.question.replace(/'/g, "\\'")}', 0.95)">
      🔊 산타의 질문 듣기: "${q.question}"
    </button>
  `;
}

// ==========================================
// 6. 사물 발견 시 [① 듣기 ➔ ② 쓰기 ➔ ③ 따라 읽기] 진행
// ==========================================
function openItemMission() {
  const q = QUESTS[currentIdx];
  missionStage = "modal_write";
  speakAttempts = 0;
  playSfx("discover");
  spawnBurst(q.x, q.y, ["#ffd166", "#06d6a0", "#38bdf8", "#fb7185"], 28);

  // 자동으로 질문과 정답 원어민 발음 1회 재생
  speakEnglish(`${q.question} ... ${q.answer}`, 0.92);

  document.getElementById("qSpeaker").innerText = `🎁 발견! ${q.roomKo} 보물 #${currentIdx + 1}`;
  document.getElementById("qBadge").innerText = "✍️ 1단계: 듣고 쓰기";

  const chipsHtml = q.chips
    .map(ch => `<button type="button" class="word-chip" onclick="appendChip('${ch.replace(/'/g, "\\'")}')">${ch}</button>`)
    .join("");

  document.getElementById("qBody").innerHTML = `
    <div class="card-row">
      <canvas id="cardPreview" width="160" height="160"></canvas>
      <div style="font-size:12px;">
        <div class="step-badge">STEP 1. 원어민 발음 듣기</div>
        <div class="audio-btns">
          <button type="button" class="btn-game sky" onclick="speakEnglish('${q.answer.replace(/'/g, "\\'")}', 0.95)">🔊 정답 듣기</button>
          <button type="button" class="btn-game ghost" onclick="speakEnglish('${q.answer.replace(/'/g, "\\'")}', 0.7)">🐢 천천히</button>
        </div>
        <div style="color:#94a3b8;">질문: <i>"${q.question}"</i></div>
      </div>
    </div>

    <div class="step-badge" style="background:#f59e0b; color:#111;">STEP 2. 문장 직접 쓰기 (단어 터치 또는 키보드 입력)</div>
    <div class="chip-area">${chipsHtml}</div>
    <div class="write-box">
      <input id="sentenceInput" class="sentence-input" type="text" placeholder="예: ${q.answer}" autocomplete="off" />
      <button type="button" class="btn-game" onclick="verifySentence()">확인</button>
      <button type="button" class="btn-game ghost" onclick="clearSentence()">지우기</button>
    </div>
    <div id="writeFb" class="fb-line"></div>
  `;

  drawCardThumbnail(q);
}

function drawCardThumbnail(q) {
  setTimeout(() => {
    const c = document.getElementById("cardPreview");
    if (!c) return;
    const ctx = c.getContext("2d");
    const imgObj = q.sheet === "main" ? mainCardsImg : extraCardsImg;
    if (imgObj.complete && imgObj.naturalWidth > 0) {
      const sw = imgObj.naturalWidth / 2;
      const sh = imgObj.naturalHeight / 2;
      ctx.drawImage(imgObj, q.crop[0] * sw, q.crop[1] * sh, sw, sh, 0, 0, 160, 160);
    } else {
      ctx.fillStyle = "#1e3a8a";
      ctx.fillRect(0, 0, 160, 160);
      ctx.font = "54px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(q.icon, 80, 68);
      ctx.fillStyle = "#ffd166";
      ctx.font = "bold 20px sans-serif";
      ctx.fillText(q.label, 80, 128);
    }
  }, 30);
}

window.appendChip = function(word) {
  const inp = document.getElementById("sentenceInput");
  if (!inp) return;
  const cur = inp.value.trim();
  inp.value = cur ? `${cur} ${word}` : word;
  playSfx("coin");
};

window.clearSentence = function() {
  const inp = document.getElementById("sentenceInput");
  if (inp) inp.value = "";
};

window.verifySentence = function() {
  const q = QUESTS[currentIdx];
  const inp = document.getElementById("sentenceInput");
  const fb = document.getElementById("writeFb");
  if (!inp || !fb) return;

  const normalize = s => s.trim().toLowerCase().replace(/[.!?]+$/g, "").replace(/\s+/g, " ");
  const userNorm = normalize(inp.value);
  const ansNorm = normalize(q.answer);

  if (userNorm === ansNorm) {
    playSfx("success");
    score += 100;
    spawnFloatText(player.x, player.y, "+100 WRITE!", "#06d6a0");
    renderDex();
    openSpeakStep();
  } else {
    playSfx("error");
    fb.style.color = "#fb7185";
    if (q.isPlural && userNorm.startsWith("there is")) {
      fb.innerText = "💡 물건이 2개 이상(복수)이에요! 'There are'로 시작해 볼까요?";
    } else if (!q.isPlural && userNorm.startsWith("there are")) {
      fb.innerText = "💡 물건이 1개(단수)예요! 'There is a'로 시작해 볼까요?";
    } else {
      fb.innerText = `❌ 다시 확인해 보세요! 힌트: ${q.tip}`;
    }
  }
};
// ==========================================
// 7. STEP 3: 원어민 발음 따라 읽기 (음성 인식 + 안전 통과)
// ==========================================
function openSpeakStep() {
  const q = QUESTS[currentIdx];
  missionStage = "modal_speak";
  speakEnglish(q.answer, 0.9);

  document.getElementById("qBadge").innerText = "🎤 2단계: 따라 읽기";
  document.getElementById("qBody").innerHTML = `
    <div style="background:#14532d; border:1px solid #4ade80; border-radius:8px; padding:7px 10px; margin-bottom:8px;">
      <div style="font-size:11px; color:#bbf7d0;">✅ 문장 쓰기 성공! 이제 원어민처럼 소리 내어 읽어보세요.</div>
      <div style="font-size:17px; font-weight:bold; color:#fff; margin-top:2px;">"${q.answer}"</div>
    </div>

    <div class="audio-btns">
      <button type="button" class="btn-game sky" onclick="speakEnglish('${q.answer.replace(/'/g, "\\'")}', 0.92)">🔊 원어민 발음 다시 듣기</button>
      <button type="button" class="btn-game rose" id="btnMic" onclick="startSpeechCheck()">🎤 마이크 누르고 따라 읽기</button>
    </div>

    <div class="mic-status" id="micStatus">
      🎙️ 위 빨간 버튼을 누른 뒤 <b>"${q.answer}"</b>라고 또렷하게 읽어주세요!
    </div>
    <div id="speakNextArea" style="margin-top:8px;"></div>
  `;
}

window.startSpeechCheck = function() {
  const q = QUESTS[currentIdx];
  const statusEl = document.getElementById("micStatus");
  const nextEl = document.getElementById("speakNextArea");
  speakAttempts++;

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    statusEl.innerHTML = "⚠️ 이 브라우저는 음성 인식을 지원하지 않아요. 큰 소리로 2번 따라 읽은 뒤 아래 버튼을 누르세요!";
    nextEl.innerHTML = `<button type="button" class="btn-game" onclick="completeCurrentQuest(3)">⭐ 소리 내어 읽기 완료! 다음 보물로</button>`;
    return;
  }

  try {
    const rec = new SpeechRec();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 3;

    statusEl.innerHTML = "🔴 <b>듣고 있어요!</b> 지금 영어로 말해보세요...";
    rec.start();

    rec.onresult = (event) => {
      const transcripts = [];
      for (let i = 0; i < event.results[0].length; i++) {
        transcripts.push(event.results[0][i].transcript.toLowerCase());
      }
      const heard = transcripts[0] || "";
      const targetNoun = q.noun.toLowerCase().replace(/s$/, "");
      const matched = transcripts.some(t => t.includes(targetNoun) || t.includes("there"));

      if (matched) {
        statusEl.innerHTML = `🎉 <b>인식된 발음:</b> "${heard}" — <span style="color:#4ade80;">발음 최고예요! ⭐⭐⭐</span>`;
        nextEl.innerHTML = `<button type="button" class="btn-game" onclick="completeCurrentQuest(3)">✨ 별 3개 획득! 다음 퀘스트로</button>`;
        playSfx("success");
      } else {
        statusEl.innerHTML = `🤔 <b>인식된 발음:</b> "${heard}" — 한 번 더 또렷하게 읽어볼까요?`;
        if (speakAttempts >= 2) {
          nextEl.innerHTML = `<button type="button" class="btn-game amber" onclick="completeCurrentQuest(2)">⭐ 도전에 박수! 별 2개로 다음 단계 가기</button>`;
        }
      }
    };

    rec.onerror = () => {
      statusEl.innerHTML = "🎙️ 마이크 권한이 꺼져 있거나 주변이 시끄러워요. 큰 소리로 따라 읽은 뒤 아래 버튼을 눌러 통과하세요!";
      nextEl.innerHTML = `<button type="button" class="btn-game" onclick="completeCurrentQuest(3)">⭐ 따라 읽기 완료! 다음 퀘스트로</button>`;
    };
  } catch (e) {
    statusEl.innerHTML = "🎙️ 큰 소리로 따라 읽은 뒤 아래 버튼을 눌러 진행하세요!";
    nextEl.innerHTML = `<button type="button" class="btn-game" onclick="completeCurrentQuest(3)">⭐ 따라 읽기 완료! 다음 퀘스트로</button>`;
  }
};

window.completeCurrentQuest = function(stars) {
  const q = QUESTS[currentIdx];
  playSfx("success");
  score += stars * 50;
  totalStars += stars;
  earnedStarsList.push(stars);
  spawnBurst(player.x, player.y, ["#ffd166", "#4ade80", "#38bdf8", "#f472b6"], 36);
  spawnFloatText(player.x, player.y, `+${stars * 50} PTS! (${stars}⭐)`, "#ffd166");

  currentIdx++;
  setExplorePrompt();
};

function showEnding() {
  playSfx("success");
  document.getElementById("certTitle").innerText =
    `🎉 [${CFG.playerName}] 산타의 선물 리스트 8종 완벽 복원! (총점: ${score}점 / ${totalStars}⭐)`;
  let rows = "";
  QUESTS.forEach((q, idx) => {
    rows += `<div><b>${idx + 1}. ${q.roomKo}</b> : <span style="color:#ffd166;">${q.answer}</span> (${earnedStarsList[idx] || 3}⭐)</div>`;
  });
  document.getElementById("certBoard").innerHTML = rows;
  document.getElementById("endingScreen").classList.remove("hidden");
}

// ==========================================
// 8. 이동 물리 · 터치 투 무브 · 충돌 판정
// ==========================================
function collides(nx, ny) {
  const r = 21;
  for (const [wx, wy, ww, wh] of WALLS) {
    if (nx + r > wx && nx - r < wx + ww && ny + r > wy && ny - r < wy + wh) return true;
  }
  return false;
}

function getRoomName(x, y) {
  if (x < 500 && y < 500) return "🍳 Kitchen (주방)";
  if (x >= 500 && y < 500) return "🛏️ Bedroom (침실)";
  if (x < 500 && y >= 500) return "🛋️ Living Room (거실)";
  return "🌳 Garden (정원)";
}

function triggerInteract() {
  if (missionStage !== "explore" || currentIdx >= QUESTS.length) return;
  if (nearTarget) {
    openItemMission();
  } else if (nearSanta) {
    const q = QUESTS[currentIdx];
    playSfx("coin");
    speakEnglish(q.question, 0.95);
    spawnFloatText(santaNpc.x, santaNpc.y, "HO HO HO!", "#fb7185");
  }
}

function update(dt) {
  // 눈송이 업데이트
  for (const s of snowflakes) {
    s.y += s.sp * dt;
    s.drift += dt * 1.5;
    s.x += Math.sin(s.drift) * 12 * dt;
    if (s.y > 520) { s.y = -5; s.x = Math.random() * 520; }
  }

  // 파티클 업데이트
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.vy += 180 * dt;
    p.life -= dt;
    if (p.life <= 0) particles.splice(i, 1);
  }

  // 떠오르는 텍스트 업데이트
  for (let i = floatingTexts.length - 1; i >= 0; i--) {
    const ft = floatingTexts[i];
    ft.y -= 28 * dt;
    ft.life -= dt;
    if (ft.life <= 0) floatingTexts.splice(i, 1);
  }

  if (missionStage !== "explore" || currentIdx >= QUESTS.length) return;
  if (document.activeElement && document.activeElement.tagName === "INPUT") return;

  let dx = 0, dy = 0;
  if (keys["ArrowUp"] || keys["w"] || keys["W"]) dy -= 1;
  if (keys["ArrowDown"] || keys["s"] || keys["S"]) dy += 1;
  if (keys["ArrowLeft"] || keys["a"] || keys["A"]) dx -= 1;
  if (keys["ArrowRight"] || keys["d"] || keys["D"]) dx += 1;

  if (dx !== 0 || dy !== 0) {
    player.targetX = null;
    player.targetY = null;
  } else if (player.targetX !== null && player.targetY !== null) {
    const tdx = player.targetX - player.x;
    const tdy = player.targetY - player.y;
    if (Math.hypot(tdx, tdy) < 12) {
      player.targetX = null;
      player.targetY = null;
    } else {
      dx = tdx;
      dy = tdy;
    }
  }

  if (dx !== 0 || dy !== 0) {
    const len = Math.hypot(dx, dy);
    const speed = 285 * dt;
    const vx = (dx / len) * speed;
    const vy = (dy / len) * speed;
    if (!collides(player.x + vx, player.y)) player.x += vx;
    if (!collides(player.x, player.y + vy)) player.y += vy;
    player.walkAnim += dt * 11;
  } else {
    player.walkAnim = 0;
  }

  document.getElementById("hudRoom").innerText = "📍 " + getRoomName(player.x, player.y);

  // 보너스 사탕/종 수집 체크
  for (const b of bonusItems) {
    if (!b.collected && Math.hypot(player.x - b.x, player.y - b.y) < 42) {
      b.collected = true;
      score += 30;
      playSfx("coin");
      spawnBurst(b.x, b.y, ["#ffd166", "#ffffff"], 12);
      spawnFloatText(b.x, b.y, "+30!", "#ffd166");
      renderDex();
    }
  }

  // 현재 목표 사물 및 산타 NPC 근접 체크
  const q = QUESTS[currentIdx];
  nearTarget = Math.hypot(player.x - q.x, player.y - q.y) < 68;
  nearSanta = Math.hypot(player.x - santaNpc.x, player.y - santaNpc.y) < 68;

  const actBtn = document.getElementById("btnAction");
  if (nearTarget || nearSanta) actBtn.classList.add("near");
  else actBtn.classList.remove("near");
}

// ==========================================
// 9. 화려한 2D 캔버스 렌더링
// ==========================================
const canvas = document.getElementById("rpgCanvas");
const ctx = canvas.getContext("2d");

function drawGuideArrow(px, py, tx, ty, now) {
  const ang = Math.atan2(ty - py, tx - px);
  const dist = Math.hypot(tx - px, ty - py);
  if (dist < 45) return;

  const pulse = Math.sin(now / 160) * 4;
  const ax = px + Math.cos(ang) * (28 + pulse);
  const ay = py + Math.sin(ang) * (28 + pulse);

  ctx.save();
  ctx.translate(ax, ay);
  ctx.rotate(ang);
  ctx.fillStyle = "#ffd166";
  ctx.strokeStyle = "#0f172a";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(10, 0);
  ctx.lineTo(-5, -6);
  ctx.lineTo(-2, 0);
  ctx.lineTo(-5, 6);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

function drawHero(x, y, now) {
  const px = (x / 1000) * 520;
  const py = (y / 1000) * 520;
  const bob = Math.sin(player.walkAnim) * 3;

  // 발밑 황금 오라
  const auraR = 16 + Math.sin(now / 250) * 2.5;
  ctx.strokeStyle = "rgba(255, 209, 102, 0.55)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.ellipse(px, py + 12, auraR, auraR * 0.45, 0, 0, Math.PI * 2);
  ctx.stroke();

  // 몸통 (꼬마 산타 요원)
  ctx.fillStyle = "#e11d48";
  ctx.fillRect(px - 9, py - 4 + bob, 18, 14);
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(px - 9, py + 4 + bob, 18, 3);
  ctx.fillStyle = "#ffd166";
  ctx.fillRect(px - 2.5, py + 3.5 + bob, 5, 4);

  // 머리
  ctx.fillStyle = "#fed7aa";
  ctx.beginPath();
  ctx.arc(px, py - 10 + bob, 9.5, 0, Math.PI * 2);
  ctx.fill();

  // 눈
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(px - 4.5, py - 11 + bob, 2.5, 2.5);
  ctx.fillRect(px + 2, py - 11 + bob, 2.5, 2.5);

  // 산타 모자
  ctx.fillStyle = "#be123c";
  ctx.beginPath();
  ctx.moveTo(px - 10, py - 15 + bob);
  ctx.lineTo(px + 10, py - 15 + bob);
  ctx.lineTo(px + 5, py - 27 + bob);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.fillRect(px - 10, py - 17 + bob, 20, 3.5);
  ctx.beginPath();
  ctx.arc(px + 6, py - 27 + bob, 3.5, 0, Math.PI * 2);
  ctx.fill();

  if (nearTarget || nearSanta) {
    ctx.fillStyle = "#10b981";
    ctx.beginPath();
    ctx.roundRect(px - 22, py - 44 + bob, 44, 16, 6);
    ctx.fill();
    ctx.fillStyle = "#022c22";
    ctx.font = "bold 10px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("조사!", px, py - 36 + bob);
  }
}

function render(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  update(dt);

  ctx.clearRect(0, 0, 520, 520);

  // 1. 배경 맵
  if (mapImg.complete && mapImg.naturalWidth > 0) {
    ctx.drawImage(mapImg, 0, 0, 520, 520);
  } else {
    ctx.fillStyle = "#fef3c7";
    ctx.fillRect(0, 0, 520, 520);
  }

  // 2. 완료된 보물 체크 마크 표시
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let i = 0; i < currentIdx; i++) {
    const doneQ = QUESTS[i];
    const dx = (doneQ.x / 1000) * 520;
    const dy = (doneQ.y / 1000) * 520;
    ctx.font = "18px sans-serif";
    ctx.fillText("✅", dx, dy);
  }

  // 3. 보너스 캔디/종 렌더링
  const bobBonus = Math.sin(now / 260) * 2.5;
  for (const b of bonusItems) {
    if (!b.collected) {
      const bx = (b.x / 1000) * 520;
      const by = (b.y / 1000) * 520 + bobBonus;
      ctx.font = "15px sans-serif";
      ctx.fillText(b.emoji, bx, by);
    }
  }

  // 4. 산타 NPC 렌더링
  const sx = (santaNpc.x / 1000) * 520;
  const sy = (santaNpc.y / 1000) * 520;
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.beginPath();
  ctx.ellipse(sx, sy + 12, 12, 5, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.font = "25px sans-serif";
  ctx.fillText("🎅", sx, sy);

  // 5. 현재 목표 반짝이(✨) + 마법진
  if (currentIdx < QUESTS.length) {
    const q = QUESTS[currentIdx];
    const qx = (q.x / 1000) * 520;
    const qy = (q.y / 1000) * 520;
    const ringR = 14 + Math.sin(now / 180) * 4;

    ctx.strokeStyle = "#ffd166";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(qx, qy, ringR, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = "rgba(255, 209, 102, 0.28)";
    ctx.fill();

    ctx.font = "22px sans-serif";
    ctx.fillText("✨", qx, qy + Math.sin(now / 200) * 3);

    // 플레이어 주변 길안내 황금 화살표
    const px = (player.x / 1000) * 520;
    const py = (player.y / 1000) * 520;
    drawGuideArrow(px, py, qx, qy, now);
  }

  // 6. 플레이어 캐릭터
  drawHero(player.x, player.y, now);

  // 7. 파티클 & 떠오르는 텍스트
  for (const p of particles) {
    ctx.globalAlpha = Math.max(0, p.life / p.maxLife);
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;

  for (const ft of floatingTexts) {
    ctx.globalAlpha = Math.min(1, ft.life);
    ctx.font = "bold 13px sans-serif";
    ctx.fillStyle = "#0f172a";
    ctx.fillText(ft.text, ft.x + 1, ft.y + 1);
    ctx.fillStyle = ft.color;
    ctx.fillText(ft.text, ft.x, ft.y);
  }
  ctx.globalAlpha = 1;

  // 8. 크리스마스 눈송이 오버레이
  ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
  for (const s of snowflakes) {
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fill();
  }

  requestAnimationFrame(render);
}

// ==========================================
// 10. 입력 바인딩 (키보드 + D-Pad + 맵 직접 터치 이동)
// ==========================================
window.addEventListener("keydown", (e) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(e.key)) {
    if (document.activeElement?.tagName !== "INPUT") e.preventDefault();
  }
  keys[e.key] = true;
  if (e.key === " " && document.activeElement?.tagName !== "INPUT") triggerInteract();
});
window.addEventListener("keyup", (e) => { keys[e.key] = false; });

function bindPad(id, k) {
  const el = document.getElementById(id);
  const down = (e) => { if (e.cancelable) e.preventDefault(); keys[k] = true; el.classList.add("pressed"); };
  const up = (e) => { if (e.cancelable) e.preventDefault(); keys[k] = false; el.classList.remove("pressed"); };
  el.addEventListener("pointerdown", down);
  el.addEventListener("pointerup", up);
  el.addEventListener("pointerleave", up);
  el.addEventListener("touchstart", down, { passive: false });
  el.addEventListener("touchend", up, { passive: false });
}
bindPad("btnUp", "ArrowUp");
bindPad("btnDown", "ArrowDown");
bindPad("btnLeft", "ArrowLeft");
bindPad("btnRight", "ArrowRight");

document.getElementById("btnAction").addEventListener("click", triggerInteract);

// 맵 캔버스 터치/클릭 시 해당 좌표로 이동
canvas.addEventListener("pointerdown", (e) => {
  if (missionStage !== "explore") return;
  const rect = canvas.getBoundingClientRect();
  const tx = ((e.clientX - rect.left) / rect.width) * 1000;
  const ty = ((e.clientY - rect.top) / rect.height) * 1000;
  player.targetX = tx;
  player.targetY = ty;
  spawnBurst(tx, ty, ["#38bdf8", "#ffd166"], 8);
});

setExplorePrompt();
requestAnimationFrame(render);
</script>
</body>
</html>
"""

html_code = html_template.replace("__CONFIG_JSON__", config_json)
components.html(html_code, height=840, scrolling=True)
