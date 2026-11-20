import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import json

st.set_page_config(
    page_title="Santa's Dream House RPG",
    page_icon="🎅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.4rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    .stApp { background-color: #141722; }
</style>
""", unsafe_allow_html=True)

def load_img_b64(candidates):
    if isinstance(candidates, str):
        candidates = [candidates]
    for base_name in candidates:
        for ext in ["", ".png", ".jpg", ".jpeg", ".webp"]:
            fname = base_name if base_name.endswith((".png", ".jpg", ".jpeg", ".webp")) else base_name + ext
            if os.path.exists(fname):
                mime = "image/jpeg" if fname.lower().endswith((".jpg", ".jpeg")) else "image/png"
                with open(fname, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{data}"
    return ""

ASSETS = {
    "map": load_img_b64(["house_map.png", "house_map.jpg"]),
    "cards": load_img_b64(["cards.png", "cards.jpg"]),
    "extra_cards": load_img_b64(["extra_cards.jpg", "extra_cards.png"]),
    "complete": load_img_b64(["complete.png", "complete.jpg"]),
    "title_banner": load_img_b64(["title_banner.png", "title_banner.jpg"]),
    "unlock_cutin": load_img_b64(["unlock_cutin.png", "unlock_cutin.jpg"]),
    "portrait_p1": load_img_b64(["portrait_p1.png", "portraits_p1.png"]),
    "portrait_p2": load_img_b64(["portrait_p2.png", "portraits_p2.png"]),
    "santa_panic": load_img_b64(["portrait_santa_panic.png", "portraits_santa_panic.png"]),
    "santa_happy": load_img_b64(["portrait_santa_happy.png", "portraits_santa_happy.png"]),
    "magic_lock": load_img_b64(["obj_magic_lock.png", "obj_magic_lock.jpg"]),
    "treasure_chest": load_img_b64(["obj_treasure_chest.png", "obj_treasure_chest.jpg"]),
    "decoy_kitchen": load_img_b64(["decoy_kitchen.png", "decoy_kitchen.jpg"]),
    "decoy_bedroom": load_img_b64(["decoy_bedroom.png", "decoy_bedroom.jpg"]),
    "decoy_living": load_img_b64(["decoy_living.png", "decoy_living.jpg"]),
    "decoy_garden": load_img_b64(["decoy_garden.png", "decoy_garden.jpg"]),
}

assets_json = json.dumps(ASSETS)

html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<style>
  * {{
    box-sizing: border-box;
    user-select: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
  }}
  body {{
    margin: 0;
    padding: 0;
    background: #141722;
    color: #f8fafc;
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    overflow-x: hidden;
  }}

  /* 로비 화면 */
  #lobby-screen {{
    max-width: 980px;
    margin: 8px auto;
    background: linear-gradient(180deg, #1e2436 0%, #161b29 100%);
    border: 3px solid #f59e0b;
    border-radius: 20px;
    padding: 18px 22px 24px 22px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.65);
    text-align: center;
  }}
  .banner-wrap {{
    width: 100%;
    max-height: 270px;
    overflow: hidden;
    border-radius: 14px;
    border: 2px solid #fbbf24;
    margin-bottom: 12px;
  }}
  .banner-wrap img {{
    width: 100%;
    height: 270px;
    object-fit: cover;
    display: block;
  }}
  .lobby-title {{
    font-size: 26px;
    font-weight: 900;
    color: #fde047;
    margin: 4px 0 6px 0;
  }}
  .lobby-sub {{
    font-size: 14.5px;
    color: #cbd5e1;
    margin-bottom: 16px;
    line-height: 1.5;
  }}
  .role-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }}
  .role-card {{
    background: #252d44;
    border: 3px solid #475569;
    border-radius: 16px;
    padding: 16px;
    cursor: pointer;
    transition: transform 0.16s ease, border-color 0.16s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .role-card.p1:hover, .role-card.p1:active {{ border-color: #f87171; transform: translateY(-2px); }}
  .role-card.p2:hover, .role-card.p2:active {{ border-color: #4ade80; transform: translateY(-2px); }}
  .role-avatar {{
    width: 82px;
    height: 82px;
    border-radius: 14px;
    border: 3px solid #fbbf24;
    object-fit: cover;
    margin-bottom: 10px;
  }}
  .role-name {{
    font-size: 19px;
    font-weight: 800;
    margin-bottom: 6px;
  }}
  .role-desc {{
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.45;
  }}

  /* 메인 게임 레이아웃 */
  #game-screen {{
    display: none;
    max-width: 1360px;
    margin: 0 auto;
  }}
  .top-hud {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    background: #1e2436;
    border: 2px solid #334155;
    border-radius: 12px;
    padding: 8px 14px;
    margin-bottom: 10px;
  }}
  .hud-badge {{
    font-weight: 800;
    font-size: 14.5px;
    padding: 5px 12px;
    border-radius: 999px;
  }}
  .badge-p1 {{ background: #7f1d1d; color: #fecaca; border: 1px solid #f87171; }}
  .badge-p2 {{ background: #14532d; color: #bbf7d0; border: 1px solid #4ade80; }}
  .key-slots {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .key-slot {{
    background: #0f172a;
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12.5px;
    font-weight: 700;
    color: #64748b;
  }}
  .key-slot.unlocked {{
    border-color: #facc15;
    color: #fef08a;
    background: #422006;
  }}

  .main-arena {{
    display: grid;
    grid-template-columns: 1.32fr 1fr;
    gap: 14px;
    align-items: start;
  }}

  /* 왼쪽 맵 캔버스 영역 */
  .map-panel {{
    background: #0f172a;
    border: 3px solid #475569;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.5);
  }}
  canvas#rpgCanvas {{
    width: 100%;
    height: auto;
    border-radius: 10px;
    display: block;
    background: #1e293b;
    touch-action: none;
  }}
  .controls-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
    padding: 4px 6px;
    touch-action: none;
  }}
  .dpad {{
    display: grid;
    grid-template-columns: repeat(3, 54px);
    grid-template-rows: repeat(2, 48px);
    gap: 6px;
    touch-action: none;
  }}
  .dpad button {{
    background: #334155;
    color: #f8fafc;
    border: 2px solid #64748b;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 900;
    cursor: pointer;
    touch-action: none;
  }}
  .dpad button.active-dir, .dpad button:active {{
    background: #f59e0b;
    color: #0f172a;
    border-color: #fde047;
  }}
  .action-btn {{
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #fff;
    border: none;
    border-radius: 14px;
    padding: 15px 22px;
    font-size: 17px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.45);
    touch-action: manipulation;
    min-height: 56px;
  }}
  .action-btn:active {{ transform: scale(0.97); }}

  /* 오른쪽 패널 */
  .right-panel {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .dialogue-box {{
    display: flex;
    gap: 12px;
    background: linear-gradient(180deg, #2b2118 0%, #1f1710 100%);
    border: 4px solid #d97706;
    border-radius: 16px;
    padding: 12px 14px;
    align-items: center;
  }}
  .portrait-frame {{
    width: 88px;
    height: 88px;
    flex-shrink: 0;
    border-radius: 12px;
    border: 3px solid #fbbf24;
    overflow: hidden;
    background: #0f172a;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }}
  .portrait-frame.speaking {{
    box-shadow: 0 0 18px #facc15;
    transform: scale(1.04);
  }}
  .portrait-frame img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .speaker-tag {{
    display: inline-block;
    background: #b45309;
    color: #fef3c7;
    font-size: 12px;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 6px;
    margin-bottom: 5px;
  }}
  .dialogue-text {{
    font-size: 14.5px;
    line-height: 1.48;
    color: #fef9c3;
    font-weight: 600;
  }}

  .mission-box {{
    background: #1e2436;
    border: 3px solid #3b82f6;
    border-radius: 16px;
    padding: 15px;
    min-height: 360px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .card-preview {{
    text-align: center;
    margin: 6px 0 10px 0;
  }}
  .card-canvas-wrap {{
    display: inline-block;
    border-radius: 14px;
    overflow: hidden;
    border: 3px solid #fbbf24;
    background: #0f172a;
  }}
  .step-box {{
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 11px 12px;
    margin-top: 8px;
  }}
  .step-title {{
    font-size: 13.5px;
    font-weight: 800;
    color: #38bdf8;
    margin-bottom: 6px;
  }}
  .btn-tts {{
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    margin-right: 6px;
    touch-action: manipulation;
  }}
  .btn-tts:hover {{ background: #1d4ed8; }}
  .btn-tts.unlocked-answer {{
    background: #059669;
  }}
  .btn-tts.unlocked-answer:hover {{
    background: #047857;
  }}
  .btn-mic {{
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    touch-action: manipulation;
  }}
  .btn-mic.listening {{
    background: #16a34a;
    animation: pulse 1s infinite;
  }}
  @keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }}
    70% {{ box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }}
  }}
  .eng-input {{
    width: 100%;
    padding: 11px 12px;
    font-size: 16px;
    font-weight: 700;
    border-radius: 8px;
    border: 2px solid #64748b;
    background: #1e293b;
    color: #f8fafc;
    margin-top: 4px;
  }}
  .eng-input:focus {{
    outline: none;
    border-color: #facc15;
  }}
  .btn-submit {{
    width: 100%;
    margin-top: 8px;
    padding: 11px;
    background: #10b981;
    color: #064e3b;
    font-size: 15px;
    font-weight: 900;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    touch-action: manipulation;
  }}
  .btn-submit:hover {{ background: #34d399; }}

  /* 태블릿/모바일 반응형 */
  @media (max-width: 960px) {{
    .main-arena {{
      grid-template-columns: 1fr;
    }}
    .role-grid {{
      grid-template-columns: 1fr;
    }}
    .banner-wrap, .banner-wrap img {{
      height: 190px;
      max-height: 190px;
    }}
  }}

  /* 컷인 & 엔딩 오버레이 */
  #cutin-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.78);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }}
  #cutin-overlay img {{
    max-width: 720px;
    width: 88%;
    border-radius: 20px;
    border: 4px solid #facc15;
  }}
  .cutin-caption {{
    margin-top: 14px;
    font-size: 22px;
    font-weight: 900;
    color: #fde047;
    text-align: center;
    padding: 0 12px;
  }}
  #ending-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.92);
    z-index: 10000;
    align-items: center;
    justify-content: center;
    padding: 16px;
  }}
  .ending-card {{
    max-width: 680px;
    width: 100%;
    background: #1e293b;
    border: 4px solid #facc15;
    border-radius: 22px;
    padding: 22px;
    text-align: center;
  }}
  .ending-badges {{
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 12px 0;
  }}
  .ending-badges img {{
    width: 80px;
    height: 80px;
    border-radius: 14px;
    border: 3px solid #fbbf24;
  }}
</style>
</head>
<body>

<div id="lobby-screen">
  <div class="banner-wrap" id="banner-container"></div>
  <div class="lobby-title">🎅 Santa's Secret Mission RPG 🎄</div>
  <div class="lobby-sub">
    산타 할아버지가 커피를 쏟는 바람에 집 안의 보물 목록이 뒤섞였어요!<br>
    짝꿍과 서로 다른 방을 탐험하고, <b>영어로 질문하고 답하며</b> 마법 자물쇠를 열어주세요!
  </div>
  <div class="role-grid">
    <div class="role-card p1" onclick="startGame(1)">
      <img id="lobby-p1-img" class="role-avatar" alt="1번 산타 요원" />
      <div class="role-name" style="color:#f87171;">🔴 1번 산타 요원 (짝꿍 A)</div>
      <div class="role-desc">
        • 시작 구역: <b>주방(Kitchen) &amp; 거실(Living Room)</b><br>
        • 먼저 우리 구역의 보물 단서를 찾아 영어 문장을 완성하세요!
      </div>
    </div>
    <div class="role-card p2" onclick="startGame(2)">
      <img id="lobby-p2-img" class="role-avatar" alt="2번 엘프 요원" />
      <div class="role-name" style="color:#4ade80;">🟢 2번 엘프 요원 (짝꿍 B)</div>
      <div class="role-desc">
        • 시작 구역: <b>침실(Bedroom) &amp; 정원(Garden)</b><br>
        • 먼저 우리 구역의 보물 단서를 찾아 영어 문장을 완성하세요!
      </div>
    </div>
  </div>
</div>

<div id="game-screen">
  <div class="top-hud">
    <div id="player-badge" class="hud-badge badge-p1">🔴 1번 산타 요원</div>
    <div style="font-size:13px; color:#cbd5e1; font-weight:700;">
      터치 패드 / 방향키 이동 · <b>[🔍 조사]</b>로 탐색
    </div>
    <div class="key-slots">
      <div id="slot-0" class="key-slot">🍳 Kitchen</div>
      <div id="slot-1" class="key-slot">🛏️ Bedroom</div>
      <div id="slot-2" class="key-slot">🛋️ Living</div>
      <div id="slot-3" class="key-slot">🌲 Garden</div>
    </div>
  </div>

  <div class="main-arena">
    <div class="map-panel">
      <canvas id="rpgCanvas" width="760" height="540"></canvas>
      <div class="controls-bar">
        <div class="dpad">
          <div></div>
          <button id="btn-up"
            onpointerdown="holdDir('up', this)" onpointerup="releaseDir('up', this)" onpointerleave="releaseDir('up', this)" onpointercancel="releaseDir('up', this)">▲</button>
          <div></div>
          <button id="btn-left"
            onpointerdown="holdDir('left', this)" onpointerup="releaseDir('left', this)" onpointerleave="releaseDir('left', this)" onpointercancel="releaseDir('left', this)">◀</button>
          <button id="btn-down"
            onpointerdown="holdDir('down', this)" onpointerup="releaseDir('down', this)" onpointerleave="releaseDir('down', this)" onpointercancel="releaseDir('down', this)">▼</button>
          <button id="btn-right"
            onpointerdown="holdDir('right', this)" onpointerup="releaseDir('right', this)" onpointerleave="releaseDir('right', this)" onpointercancel="releaseDir('right', this)">▶</button>
        </div>
        <div style="font-size:12.5px; color:#94a3b8; text-align:center; line-height:1.4;">
          통로와 벽은 막혀 있어요!<br><b>보물 상자</b>나 <b>자물쇠</b> 앞에서 조사!
        </div>
        <button class="action-btn" onclick="interact()">🔍 조사 / 대화</button>
      </div>
    </div>

    <div class="right-panel">
      <div class="dialogue-box">
        <div id="portrait-frame" class="portrait-frame">
          <img id="portrait-img" alt="캐릭터 초상화" />
        </div>
        <div style="flex:1;">
          <div id="speaker-tag" class="speaker-tag">🎅 산타 본부 무전</div>
          <div id="dialogue-text" class="dialogue-text">
            요원, 출동 준비 완료! 우리 구역 방 안의 반짝이는 보물 상자를 찾아가 조사해 보자!
          </div>
        </div>
      </div>

      <div class="mission-box" id="mission-panel">
        <div style="text-align:center; padding:40px 10px; color:#94a3b8;">
          <div style="font-size:42px; margin-bottom:10px;">🎁</div>
          <div style="font-size:17px; font-weight:800; color:#e2e8f0; margin-bottom:6px;">
            탐험 대기 중
          </div>
          <div style="font-size:14px; line-height:1.6;">
            맵 위에서 빛나는 <b>보물 상자</b>에 다가가<br>
            <b>[🔍 조사 / 대화]</b> 버튼을 누르면 미션이 열립니다!
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="cutin-overlay">
  <img id="cutin-img" alt="협동 자물쇠 해제!" />
  <div class="cutin-caption">✨ 짝꿍과 힘을 합쳐 마법 자물쇠를 열었습니다! ✨</div>
</div>

<div id="ending-overlay">
  <div class="ending-card">
    <h2 style="color:#fde047; margin:0 0 8px 0; font-size:26px;">🎉 MISSION COMPLETE! 🎉</h2>
    <p style="color:#cbd5e1; font-size:15px; margin:0 0 12px 0;">
      짝꿍과 영어로 소통하여 산타의 드림하우스 4개 구역 보물을 모두 복구했습니다!
    </p>
    <img id="complete-img" style="max-width:340px; width:85%; border-radius:14px; border:3px solid #fbbf24;" />
    <div class="ending-badges">
      <img id="end-agent-img" alt="내 요원" />
      <img id="end-santa-img" alt="엄지척 산타" />
    </div>
    <div style="background:#0f172a; padding:10px; border-radius:10px; font-size:13.5px; color:#fde047; font-weight:700;">
      📸 지금 이 화면을 캡처해서 학급 패들렛(Padlet)에 올려주세요!
    </div>
  </div>
</div>

<script>
const ASSETS = {assets_json};
const IMGS = {{}};
for (const [k, src] of Object.entries(ASSETS)) {{
  if (src) {{
    const img = new Image();
    img.src = src;
    IMGS[k] = img;
  }}
}}

if (ASSETS.title_banner) {{
  document.getElementById("banner-container").innerHTML = `<img src="${{ASSETS.title_banner}}" alt="Santa's Secret Mission" />`;
}}
if (ASSETS.portrait_p1) document.getElementById("lobby-p1-img").src = ASSETS.portrait_p1;
if (ASSETS.portrait_p2) document.getElementById("lobby-p2-img").src = ASSETS.portrait_p2;
if (ASSETS.unlock_cutin) document.getElementById("cutin-img").src = ASSETS.unlock_cutin;
if (ASSETS.complete) document.getElementById("complete-img").src = ASSETS.complete;
if (ASSETS.santa_happy) document.getElementById("end-santa-img").src = ASSETS.santa_happy;

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSFX(type) {{
  if (audioCtx.state === "suspended") audioCtx.resume();
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  const now = audioCtx.currentTime;

  if (type === "open") {{
    osc.type = "sine";
    osc.frequency.setValueAtTime(523, now);
    osc.frequency.setValueAtTime(659, now + 0.08);
    osc.frequency.setValueAtTime(784, now + 0.16);
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);
    osc.start(now); osc.stop(now + 0.32);
  }} else if (type === "decoy") {{
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(300, now);
    osc.frequency.linearRampToValueAtTime(160, now + 0.25);
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
    osc.start(now); osc.stop(now + 0.28);
  }} else if (type === "success") {{
    osc.type = "square";
    [523, 659, 784, 1046].forEach((f, i) => osc.frequency.setValueAtTime(f, now + i * 0.09));
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
    osc.start(now); osc.stop(now + 0.45);
  }} else if (type === "error") {{
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(170, now);
    osc.frequency.setValueAtTime(135, now + 0.12);
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
    osc.start(now); osc.stop(now + 0.28);
  }}
}}

// 원어민 음성 듣기 (태블릿·모바일 TTS 안정화)
let availableVoices = [];
function loadVoices() {{
  if ("speechSynthesis" in window) {{
    availableVoices = window.speechSynthesis.getVoices() || [];
  }}
}}
loadVoices();
if ("speechSynthesis" in window) {{
  window.speechSynthesis.onvoiceschanged = loadVoices;
}}

let speakTimer = null;
function speakEnglish(text, btnEl) {{
  if (!("speechSynthesis" in window)) return;
  loadVoices();
  try {{
    window.speechSynthesis.resume();
    window.speechSynthesis.cancel();
  }} catch (e) {{}}

  const frame = document.getElementById("portrait-frame");
  if (frame) frame.classList.add("speaking");
  if (btnEl) btnEl.style.opacity = "0.75";
  clearTimeout(speakTimer);

  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US";
  u.rate = 0.88;
  u.pitch = 1.0;
  u.volume = 1.0;

  const enVoice =
    availableVoices.find(v => v.lang && v.lang.toLowerCase().startsWith("en-us")) ||
    availableVoices.find(v => v.lang && v.lang.toLowerCase().startsWith("en"));
  if (enVoice) u.voice = enVoice;

  const cleanup = () => {{
    if (frame) frame.classList.remove("speaking");
    if (btnEl) btnEl.style.opacity = "1";
    clearTimeout(speakTimer);
  }};
  u.onend = cleanup;
  u.onerror = cleanup;

  // 모바일/태블릿에서 onend가 누락될 경우 대비 안전 해제 타이머
  speakTimer = setTimeout(cleanup, 2600);

  setTimeout(() => {{
    try {{
      window.speechSynthesis.resume();
      window.speechSynthesis.speak(u);
    }} catch (err) {{
      cleanup();
    }}
  }}, 30);
}}

// 4개 방 데이터 (760x540 캔버스 기준)
const ROOMS = [
  {{
    id: 0,
    roomName: "Kitchen",
    roomKo: "주방",
    owner: 1,
    question: "What's in the kitchen?",
    answer: "There is a stove.",
    altAnswers: ["there is a stove", "there's a stove"],
    itemLabel: "a stove (가스레인지)",
    crop: [0, 0],
    chestPos: {{ x: 155, y: 135 }},
    decoyPos: {{ x: 265, y: 185 }},
    decoyImg: "decoy_kitchen",
    decoyText: "앗, 꽝! 배고픈 고양이(a hungry cat)가 생선을 훔쳐 먹고 있어요! 다른 상자를 찾아보세요."
  }},
  {{
    id: 1,
    roomName: "Bedroom",
    roomKo: "침실",
    owner: 2,
    question: "What's in the bedroom?",
    answer: "There is a bed.",
    altAnswers: ["there is a bed", "there's a bed"],
    itemLabel: "a bed (침대)",
    crop: [1, 0],
    chestPos: {{ x: 605, y: 135 }},
    decoyPos: {{ x: 495, y: 185 }},
    decoyImg: "decoy_bedroom",
    decoyText: "앗, 꽝! 강아지(a sleeping dog)가 산타 양말을 물고 자고 있어요! 다른 상자를 찾아보세요."
  }},
  {{
    id: 2,
    roomName: "Living Room",
    roomKo: "거실",
    owner: 1,
    question: "What's in the living room?",
    answer: "There is a sofa.",
    altAnswers: ["there is a sofa", "there's a sofa"],
    itemLabel: "a sofa (소파)",
    crop: [0, 1],
    chestPos: {{ x: 155, y: 405 }},
    decoyPos: {{ x: 265, y: 355 }},
    decoyImg: "decoy_living",
    decoyText: "앗, 꽝! 장난감 로봇(a toy robot)이 거실 러그 위에서 춤추고 있어요! 다른 상자를 찾아보세요."
  }},
  {{
    id: 3,
    roomName: "Garden",
    roomKo: "정원",
    owner: 2,
    question: "What's in the garden?",
    answer: "There are two trees.",
    altAnswers: ["there are two trees", "there are 2 trees"],
    itemLabel: "two trees (나무 두 그루)",
    crop: [1, 1],
    chestPos: {{ x: 605, y: 405 }},
    decoyPos: {{ x: 495, y: 355 }},
    decoyImg: "decoy_garden",
    decoyText: "앗, 꽝! 귀여운 눈사람(a cute snowman)이 인사하고 있어요! 다른 상자를 찾아보세요."
  }}
];

const GATES = [
  {{ id: "top_gate", x: 380, y: 145, unlocked: false, targetRoomForP1: 1, targetRoomForP2: 0 }},
  {{ id: "bot_gate", x: 380, y: 405, unlocked: false, targetRoomForP1: 3, targetRoomForP2: 2 }}
];

const WALL_RECTS = [
  {{ x: 0, y: 0, w: 760, h: 36 }},
  {{ x: 0, y: 504, w: 760, h: 36 }},
  {{ x: 0, y: 0, w: 36, h: 540 }},
  {{ x: 724, y: 0, w: 36, h: 540 }},
  {{ x: 36, y: 256, w: 310, h: 28 }},
  {{ x: 414, y: 256, w: 310, h: 28 }},
  {{ x: 364, y: 36, w: 32, h: 78 }},
  {{ x: 364, y: 176, w: 32, h: 198 }},
  {{ x: 364, y: 436, w: 32, h: 68 }}
];

let playerRole = 1;
let player = {{ x: 190, y: 210, radius: 18, speed: 4.2 }};
let keysPressed = {{}};
let touchDirs = {{ up: false, down: false, left: false, right: false }};
let unlockedRooms = [false, false, false, false];
let openedDecoys = [false, false, false, false];
let solvedWriteRooms = [false, false, false, false];

function holdDir(dir, el) {{
  loadVoices();
  touchDirs[dir] = true;
  if (el) el.classList.add("active-dir");
}}
function releaseDir(dir, el) {{
  touchDirs[dir] = false;
  if (el) el.classList.remove("active-dir");
}}

function setDialogue(portraitKey, speaker, text) {{
  const pImg = document.getElementById("portrait-img");
  if (ASSETS[portraitKey]) pImg.src = ASSETS[portraitKey];
  document.getElementById("speaker-tag").innerText = speaker;
  document.getElementById("dialogue-text").innerHTML = text;
}}

function startGame(role) {{
  loadVoices();
  playerRole = role;
  document.getElementById("lobby-screen").style.display = "none";
  document.getElementById("game-screen").style.display = "block";

  const badge = document.getElementById("player-badge");
  if (role === 1) {{
    badge.className = "hud-badge badge-p1";
    badge.innerText = "🔴 1번 산타 요원 (주방 · 거실 담당)";
    player.x = 190; player.y = 205;
    document.getElementById("end-agent-img").src = ASSETS.portrait_p1 || "";
    setDialogue("portrait_p1", "🔴 1번 산타 요원", "출동 완료! 왼쪽 <b>주방(위)</b>과 <b>거실(아래)</b> 보물 상자를 조사하자! 옆 방 통로는 자물쇠로 막혀 있어요.");
  }} else {{
    badge.className = "hud-badge badge-p2";
    badge.innerText = "🟢 2번 엘프 요원 (침실 · 정원 담당)";
    player.x = 570; player.y = 205;
    document.getElementById("end-agent-img").src = ASSETS.portrait_p2 || "";
    setDialogue("portrait_p2", "🟢 2번 엘프 요원", "출동 완료! 오른쪽 <b>침실(위)</b>과 <b>정원(아래)</b> 보물 상자를 조사하자! 옆 방 통로는 자물쇠로 막혀 있어요.");
  }}
  requestAnimationFrame(gameLoop);
}}

window.addEventListener("keydown", e => {{
  if (document.activeElement.tagName === "INPUT") return;
  keysPressed[e.key.toLowerCase()] = true;
  if (e.code === "Space") {{
    e.preventDefault();
    interact();
  }}
}});
window.addEventListener("keyup", e => {{
  keysPressed[e.key.toLowerCase()] = false;
}});

function circleIntersectsRect(cx, cy, r, rect) {{
  const closestX = Math.max(rect.x, Math.min(cx, rect.x + rect.w));
  const closestY = Math.max(rect.y, Math.min(cy, rect.y + rect.h));
  const dx = cx - closestX;
  const dy = cy - closestY;
  return (dx * dx + dy * dy) < (r * r);
}}

function canOccupy(nx, ny) {{
  for (const w of WALL_RECTS) {{
    if (circleIntersectsRect(nx, ny, player.radius, w)) return false;
  }}
  for (const g of GATES) {{
    if (!g.unlocked) {{
      const gateWall = {{ x: g.x - 26, y: g.y - 32, w: 52, h: 64 }};
      if (circleIntersectsRect(nx, ny, player.radius, gateWall)) return false;
    }}
  }}
  return true;
}}

function tryMove(dx, dy) {{
  const nextX = player.x + dx;
  const nextY = player.y + dy;
  if (canOccupy(nextX, player.y)) player.x = nextX;
  if (canOccupy(player.x, nextY)) player.y = nextY;
}}

function interact() {{
  loadVoices();
  for (const g of GATES) {{
    if (!g.unlocked && Math.hypot(player.x - g.x, player.y - g.y) < 82) {{
      openGateChallenge(g);
      return;
    }}
  }}

  for (const r of ROOMS) {{
    if (Math.hypot(player.x - r.chestPos.x, player.y - r.chestPos.y) < 62) {{
      if (r.owner !== playerRole && !unlockedRooms[r.id]) {{
        setDialogue("santa_panic", "🎅 산타 본부", "통로가 마법 자물쇠로 막혀 있어요! 먼저 중앙 자물쇠 앞에서 짝꿍에게 영어로 질문해 보세요!");
        playSFX("error");
        return;
      }}
      openTreasureMission(r);
      return;
    }}
    if (Math.hypot(player.x - r.decoyPos.x, player.y - r.decoyPos.y) < 58) {{
      openedDecoys[r.id] = true;
      playSFX("decoy");
      setDialogue("santa_panic", "🎅 앗, 함정 상자!", r.decoyText);
      renderDecoyCard(r);
      return;
    }}
  }}

  setDialogue(playerRole === 1 ? "portrait_p1" : "portrait_p2", "🔍 주변 탐색", "근처에 조사할 상자나 자물쇠가 없어요. 반짝이는 <b>보물 상자</b>나 <b>황금 자물쇠</b> 가까이 다가가 보세요!");
}}

function renderDecoyCard(room) {{
  const panel = document.getElementById("mission-panel");
  const imgSrc = ASSETS[room.decoyImg] || "";
  panel.innerHTML = `
    <div style="text-align:center;">
      <div style="color:#fbbf24; font-weight:900; font-size:17px; margin-bottom:8px;">😜 코믹 꽝 카드 발견!</div>
      <img src="${{imgSrc}}" style="width:210px; height:210px; border-radius:14px; border:3px solid #f59e0b; object-fit:cover;" />
      <p style="color:#cbd5e1; font-size:14px; margin-top:10px; line-height:1.5;">
        ${{room.decoyText}}
      </p>
    </div>
  `;
}}

function openTreasureMission(room) {{
  playSFX("open");
  const myPortrait = playerRole === 1 ? "portrait_p1" : "portrait_p2";
  const isSolved = solvedWriteRooms[room.id];

  setDialogue(myPortrait, `📦 ${{room.roomKo}}(${{room.roomName}}) 보물 발견!`,
    `<b>${{room.itemLabel}}</b> 단서를 찾았어요!<br>먼저 <b>[🔊 질문 듣기]</b>로 질문을 듣고, 직접 영어 문장을 써서 정답을 맞혀 보세요!`);

  const panel = document.getElementById("mission-panel");
  panel.innerHTML = `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:900; color:#fde047; font-size:16px;">✨ ${{room.roomName}} 보물 단서</span>
        <span style="font-size:12px; background:#1e3a8a; padding:3px 8px; border-radius:6px;">질문 듣기 → 쓰기 → 정답 발음</span>
      </div>
      <div class="card-preview">
        <div class="card-canvas-wrap">
          <canvas id="cardCropCanvas" width="150" height="150"></canvas>
        </div>
        <div style="font-size:13.5px; color:#93c5fd; margin-top:5px; font-weight:700;">
          질문: "${{room.question}}"
        </div>
      </div>

      <div class="step-box">
        <div class="step-title">1단계: 원어민 질문 듣기 (정답 확인 후 정답 문장 듣기 해금)</div>
        <button class="btn-tts" onclick="speakEnglish('${{room.question.replace(/'/g, "\\\\'")}}', this)">🔊 질문 듣기</button>
        <button id="btn-answer-tts" class="btn-tts unlocked-answer"
          style="display:${{isSolved ? 'inline-block' : 'none'}};"
          onclick="speakEnglish('${{room.answer.replace(/'/g, "\\\\'")}}', this)">🔊 정답 문장 듣기</button>
      </div>

      <div class="step-box">
        <div class="step-title">2단계: 정답 문장 직접 쓰기</div>
        <input id="mission-write-input" class="eng-input" type="text"
          value="${{isSolved ? room.answer : ''}}"
          placeholder="예: There is a ..." autocomplete="off" />
        <button class="btn-submit" onclick="checkMissionWrite(${{room.id}})">✅ 문장 확인하기</button>
      </div>

      <div class="step-box" id="speak-step-box" style="opacity:${{isSolved ? '1' : '0.45'}}; pointer-events:${{isSolved ? 'auto' : 'none'}};">
        <div class="step-title">3단계: 마이크 눌러 따라 읽기 (발음 인증)</div>
        <button id="mic-btn" class="btn-mic" onclick="startSpeechCheck(${{room.id}})">🎤 말하기 시작</button>
        <span id="speech-result" style="font-size:13px; margin-left:8px; color:#cbd5e1;">
          ${{isSolved ? '정답 문장을 듣고 따라 읽어보세요!' : '2단계를 먼저 통과하세요'}}
        </span>
      </div>
    </div>
  `;

  const c = document.getElementById("cardCropCanvas");
  const ctx = c.getContext("2d");
  if (IMGS.cards && IMGS.cards.complete) {{
    const sw = IMGS.cards.width / 2;
    const sh = IMGS.cards.height / 2;
    ctx.drawImage(IMGS.cards, room.crop[0] * sw, room.crop[1] * sh, sw, sh, 0, 0, 150, 150);
  }}
}}

function normalizeSentence(s) {{
  return s.toLowerCase().replace(/[.!?,'"]/g, "").replace(/\s+/g, " ").trim();
}}

function checkMissionWrite(roomId) {{
  const room = ROOMS[roomId];
  const val = normalizeSentence(document.getElementById("mission-write-input").value);
  const target = normalizeSentence(room.answer);

  if (val === target || room.altAnswers.includes(val)) {{
    solvedWriteRooms[roomId] = true;
    playSFX("success");
    const ansBtn = document.getElementById("btn-answer-tts");
    if (ansBtn) ansBtn.style.display = "inline-block";

    setDialogue("santa_happy", "😎 산타 교관",
      `정답이에요! <b>"${{room.answer}}"</b><br>이제 <b>[🔊 정답 문장 듣기]</b>로 원어민 발음을 확인한 뒤 <b>3단계 마이크</b>로 따라 읽어보세요!`);

    const speakBox = document.getElementById("speak-step-box");
    speakBox.style.opacity = "1";
    speakBox.style.pointerEvents = "auto";
    document.getElementById("speech-result").innerText = "정답 문장을 듣고 말해보세요!";
    speakEnglish(room.answer, ansBtn);
  }} else {{
    playSFX("error");
    setDialogue("santa_panic", "🎅 산타 교관",
      `아직 맞지 않아요! 먼저 <b>[🔊 질문 듣기]</b>를 누르고, <b>There is / There are</b>와 단어 철자를 다시 확인해 보세요.`);
  }}
}}

function startSpeechCheck(roomId) {{
  const room = ROOMS[roomId];
  const resSpan = document.getElementById("speech-result");
  const micBtn = document.getElementById("mic-btn");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {{
    completeRoomMission(roomId, "(음성인식 미지원 기기 자동 통과)");
    return;
  }}

  const recog = new SpeechRecognition();
  recog.lang = "en-US";
  recog.interimResults = false;
  micBtn.classList.add("listening");
  micBtn.innerText = "🎙️ 듣는 중...";
  resSpan.innerText = `"${{room.answer}}" 라고 말해보세요!`;

  recog.onresult = (e) => {{
    micBtn.classList.remove("listening");
    micBtn.innerText = "🎤 다시 말하기";
    const spoken = normalizeSentence(e.results[0][0].transcript);
    const keyWord = room.id === 0 ? "stove" : room.id === 1 ? "bed" : room.id === 2 ? "sofa" : "tree";
    if (spoken.includes(keyWord) || spoken.includes("there")) {{
      completeRoomMission(roomId, spoken);
    }} else {{
      playSFX("error");
      resSpan.innerText = `인식된 말: "${{spoken}}" — "${{room.answer}}"를 또박또박 말해 보세요!`;
    }}
  }};
  recog.onerror = () => {{
    micBtn.classList.remove("listening");
    micBtn.innerText = "🎤 말하기 시작";
    resSpan.innerHTML = `마이크 인식이 어렵다면 <button class="btn-tts" style="padding:3px 8px;font-size:12px;" onclick="completeRoomMission(${{roomId}}, '발음 연습 완료')">발음 연습 완료 처리</button>`;
  }};
  recog.start();
}}

function completeRoomMission(roomId, spokenText) {{
  const room = ROOMS[roomId];
  unlockedRooms[roomId] = true;
  document.getElementById(`slot-${{roomId}}`).classList.add("unlocked");
  playSFX("success");
  setDialogue("santa_happy", "😎 산타 교관",
    `멋져요! (${{spokenText}})<br>짝꿍이 <b>"${{room.question}}"</b>라고 물어보면 <b>"${{room.answer}}"</b>라고 대답해 주세요!`);

  document.getElementById("mission-panel").innerHTML = `
    <div style="text-align:center; padding:24px 10px;">
      <div style="font-size:44px; margin-bottom:8px;">🔑</div>
      <div style="font-size:19px; font-weight:900; color:#fde047; margin-bottom:8px;">
        ${{room.roomName}} 열쇠 문장 획득 완료!
      </div>
      <div style="background:#0f172a; border:2px solid #facc15; border-radius:12px; padding:12px; font-size:18px; font-weight:900; color:#fff; margin-bottom:12px;">
        "${{room.answer}}"
      </div>
      <button class="btn-tts unlocked-answer" onclick="speakEnglish('${{room.answer.replace(/'/g, "\\\\'")}}', this)">🔊 정답 문장 다시 듣기</button>
      <p style="font-size:13.5px; color:#cbd5e1; line-height:1.5; margin-top:12px;">
        이제 중앙 통로의 <b>황금 마법 자물쇠</b> 앞으로 가서 짝꿍 방의 단서를 영어로 물어보세요!
      </p>
    </div>
  `;
  checkAllClear();
}}

function openGateChallenge(gate) {{
  const targetRoomId = playerRole === 1 ? gate.targetRoomForP1 : gate.targetRoomForP2;
  const targetRoom = ROOMS[targetRoomId];
  const partnerPortrait = playerRole === 1 ? "portrait_p2" : "portrait_p1";
  const partnerName = playerRole === 1 ? "🟢 2번 엘프 짝꿍에게 질문하기!" : "🔴 1번 산타 짝꿍에게 질문하기!";

  playSFX("open");
  setDialogue(partnerPortrait, partnerName,
    `옆자리 짝꿍을 보고 영어로 질문해 보세요!<br>👉 <b style="color:#fde047; font-size:17px;">"${{targetRoom.question}}"</b>`);

  const panel = document.getElementById("mission-panel");
  panel.innerHTML = `
    <div>
      <div style="text-align:center; margin-bottom:8px;">
        <img src="${{ASSETS.magic_lock || ''}}" style="width:84px; height:84px; object-fit:contain;" />
        <div style="font-size:17px; font-weight:900; color:#fbbf24;">🔒 마법 자물쇠 해제 작전</div>
      </div>

      <div class="step-box">
        <div class="step-title">1단계: 짝꿍에게 영어로 질문하기</div>
        <div style="font-size:16px; font-weight:900; color:#fde047; margin-bottom:6px;">
          "${{targetRoom.question}}"
        </div>
        <button class="btn-tts" onclick="speakEnglish('${{targetRoom.question.replace(/'/g, "\\\\'")}}', this)">🔊 질문 발음 들어보기</button>
      </div>

      <div class="step-box">
        <div class="step-title">2단계: 짝꿍이 대답해 준 영어 문장 입력</div>
        <input id="gate-answer-input" class="eng-input" type="text" placeholder="짝꿍이 알려준 문장을 입력하세요" autocomplete="off" />
        <button class="btn-submit" onclick="verifyGateAnswer('${{gate.id}}', ${{targetRoomId}})">🔓 자물쇠 열기!</button>
      </div>
    </div>
  `;
}}

function verifyGateAnswer(gateId, targetRoomId) {{
  const targetRoom = ROOMS[targetRoomId];
  const val = normalizeSentence(document.getElementById("gate-answer-input").value);
  const target = normalizeSentence(targetRoom.answer);

  if (val === target || targetRoom.altAnswers.includes(val)) {{
    const gate = GATES.find(g => g.id === gateId);
    gate.unlocked = true;
    unlockedRooms[targetRoomId] = true;
    document.getElementById(`slot-${{targetRoomId}}`).classList.add("unlocked");
    playSFX("success");

    const cutin = document.getElementById("cutin-overlay");
    cutin.style.display = "flex";
    setTimeout(() => {{
      cutin.style.display = "none";
      checkAllClear();
    }}, 2500);

    setDialogue("santa_happy", "😎 자물쇠 해제 성공!",
      `짝꿍과 힘을 합쳐 <b>${{targetRoom.roomName}}</b> 통로를 열었어요! 이제 열린 통로를 지나갈 수 있습니다!`);
    document.getElementById("mission-panel").innerHTML = `
      <div style="text-align:center; padding:30px 10px;">
        <div style="font-size:44px; margin-bottom:8px;">🔓</div>
        <div style="font-size:18px; font-weight:900; color:#4ade80;">마법 자물쇠가 열렸습니다!</div>
        <p style="font-size:14px; color:#cbd5e1; margin-top:8px;">이제 열린 통로를 지나 반대편 구역으로 이동해 보세요!</p>
      </div>
    `;
  }} else {{
    playSFX("error");
    setDialogue("santa_panic", "🎅 암호 불일치!",
      `자물쇠가 열리지 않아요! 짝꿍에게 <b>"${{targetRoom.question}}"</b>라고 다시 한 번 정확히 물어보세요!`);
  }}
}}

function checkAllClear() {{
  if (unlockedRooms.every(v => v === true)) {{
    setTimeout(() => {{
      playSFX("success");
      document.getElementById("ending-overlay").style.display = "flex";
    }}, 600);
  }}
}}

const canvas = document.getElementById("rpgCanvas");
const ctx = canvas.getContext("2d");

function updateMovement() {{
  let dx = 0, dy = 0;
  if (keysPressed["arrowup"] || keysPressed["w"] || touchDirs.up) dy -= player.speed;
  if (keysPressed["arrowdown"] || keysPressed["s"] || touchDirs.down) dy += player.speed;
  if (keysPressed["arrowleft"] || keysPressed["a"] || touchDirs.left) dx -= player.speed;
  if (keysPressed["arrowright"] || keysPressed["d"] || touchDirs.right) dx += player.speed;
  if (dx !== 0 || dy !== 0) tryMove(dx, dy);
}}

function drawGame() {{
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (IMGS.map && IMGS.map.complete) {{
    ctx.drawImage(IMGS.map, 0, 0, canvas.width, canvas.height);
  }} else {{
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }}

  ctx.save();
  ctx.fillStyle = "rgba(15, 23, 42, 0.42)";
  for (const w of WALL_RECTS) {{
    ctx.fillRect(w.x, w.y, w.w, w.h);
  }}
  ctx.restore();

  const tick = Date.now() / 300;
  for (const r of ROOMS) {{
    if (r.owner === playerRole || unlockedRooms[r.id]) {{
      drawChest(r.chestPos.x, r.chestPos.y, unlockedRooms[r.id], tick);
    }}
    if (r.owner === playerRole && !openedDecoys[r.id]) {{
      drawChest(r.decoyPos.x, r.decoyPos.y, false, tick + 1.5);
    }}
  }}

  for (const g of GATES) {{
    if (!g.unlocked) {{
      if (IMGS.magic_lock && IMGS.magic_lock.complete) {{
        ctx.drawImage(IMGS.magic_lock, g.x - 32, g.y - 32, 64, 64);
      }} else {{
        ctx.font = "34px serif";
        ctx.fillText("🔒", g.x - 17, g.y + 12);
      }}
    }}
  }}

  ctx.save();
  ctx.beginPath();
  ctx.arc(player.x, player.y, player.radius + 4, 0, Math.PI * 2);
  ctx.fillStyle = playerRole === 1 ? "#ef4444" : "#22c55e";
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#fde047";
  ctx.stroke();

  const avatarImg = playerRole === 1 ? IMGS.portrait_p1 : IMGS.portrait_p2;
  if (avatarImg && avatarImg.complete) {{
    ctx.clip();
    ctx.drawImage(avatarImg, player.x - 20, player.y - 20, 40, 40);
  }}
  ctx.restore();
}}

function drawChest(x, y, opened, tick) {{
  const bounce = opened ? 0 : Math.sin(tick) * 3;
  ctx.save();
  if (opened) ctx.globalAlpha = 0.45;
  if (IMGS.treasure_chest && IMGS.treasure_chest.complete) {{
    ctx.drawImage(IMGS.treasure_chest, x - 24, y - 24 + bounce, 48, 48);
  }} else {{
    ctx.font = "28px serif";
    ctx.fillText("✨", x - 14, y + 10 + bounce);
  }}
  ctx.restore();
}}

function gameLoop() {{
  updateMovement();
  drawGame();
  requestAnimationFrame(gameLoop);
}}
</script>
</body>
</html>
"""

components.html(html_code, height=780, scrolling=False)
