import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import json

# 1. 페이지 설정
st.set_page_config(
    page_title="Santa's Dream House RPG",
    page_icon="🎅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Streamlit 기본 여백 제거 & 다크 RPG 테마 적용
st.markdown("""
<style>
    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none; }
    .stApp { background-color: #141722; }
</style>
""", unsafe_allow_html=True)

# 3. 보유 이미지 파일 유연한 로딩 (파일명 오타/확장자 자동 대응)
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

# 4. 실시간 2D RPG 짝꿍 협동 자물쇠 엔진 (HTML5 Canvas + JS)
html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  * {{ box-sizing: border-box; user-select: none; }}
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
    margin: 10px auto;
    background: linear-gradient(180deg, #1e2436 0%, #161b29 100%);
    border: 3px solid #f59e0b;
    border-radius: 20px;
    padding: 20px 26px 26px 26px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.65);
    text-align: center;
  }}
  .banner-wrap {{
    width: 100%;
    max-height: 290px;
    overflow: hidden;
    border-radius: 14px;
    border: 2px solid #fbbf24;
    margin-bottom: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45);
  }}
  .banner-wrap img {{
    width: 100%;
    height: 290px;
    object-fit: cover;
    display: block;
  }}
  .lobby-title {{
    font-size: 28px;
    font-weight: 900;
    color: #fde047;
    margin: 4px 0 6px 0;
    text-shadow: 0 2px 10px rgba(250, 204, 21, 0.35);
  }}
  .lobby-sub {{
    font-size: 15px;
    color: #cbd5e1;
    margin-bottom: 18px;
    line-height: 1.5;
  }}
  .role-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }}
  .role-card {{
    background: #252d44;
    border: 3px solid #475569;
    border-radius: 16px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.18s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .role-card:hover {{
    transform: translateY(-4px);
    border-color: #facc15;
    box-shadow: 0 10px 25px rgba(250, 204, 21, 0.25);
  }}
  .role-card.p1:hover {{ border-color: #f87171; }}
  .role-card.p2:hover {{ border-color: #4ade80; }}
  .role-avatar {{
    width: 84px;
    height: 84px;
    border-radius: 14px;
    border: 3px solid #fbbf24;
    object-fit: cover;
    margin-bottom: 10px;
  }}
  .role-name {{
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 6px;
  }}
  .role-desc {{
    font-size: 13.5px;
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
    justify-content: space-between;
    align-items: center;
    background: #1e2436;
    border: 2px solid #334155;
    border-radius: 12px;
    padding: 8px 16px;
    margin-bottom: 10px;
  }}
  .hud-badge {{
    font-weight: 800;
    font-size: 15px;
    padding: 5px 12px;
    border-radius: 999px;
  }}
  .badge-p1 {{ background: #7f1d1d; color: #fecaca; border: 1px solid #f87171; }}
  .badge-p2 {{ background: #14532d; color: #bbf7d0; border: 1px solid #4ade80; }}
  .key-slots {{
    display: flex;
    gap: 8px;
  }}
  .key-slot {{
    background: #0f172a;
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 13px;
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
    grid-template-columns: 1.38fr 1fr;
    gap: 14px;
    align-items: start;
  }}

  /* 왼쪽 맵 캔버스 영역 */
  .map-panel {{
    position: relative;
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
  }}
  .controls-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
    padding: 4px 6px;
  }}
  .dpad {{
    display: grid;
    grid-template-columns: repeat(3, 44px);
    grid-template-rows: repeat(2, 40px);
    gap: 4px;
  }}
  .dpad button {{
    background: #334155;
    color: #f8fafc;
    border: 2px solid #64748b;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 800;
    cursor: pointer;
  }}
  .dpad button:active {{ background: #f59e0b; color: #0f172a; }}
  .action-btn {{
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.45);
  }}
  .action-btn:active {{ transform: scale(0.97); }}

  /* 오른쪽 RPG 무전 대화창 & 학습 미션 패널 */
  .right-panel {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* 스타듀 밸리풍 무전 대화창 */
  .dialogue-box {{
    display: flex;
    gap: 14px;
    background: linear-gradient(180deg, #2b2118 0%, #1f1710 100%);
    border: 4px solid #d97706;
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    align-items: center;
  }}
  .portrait-frame {{
    width: 96px;
    height: 96px;
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
  .dialogue-content {{
    flex: 1;
  }}
  .speaker-tag {{
    display: inline-block;
    background: #b45309;
    color: #fef3c7;
    font-size: 12px;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 6px;
    margin-bottom: 6px;
  }}
  .dialogue-text {{
    font-size: 15px;
    line-height: 1.5;
    color: #fef9c3;
    font-weight: 600;
  }}

  /* 미션 카드 & 학습 인터랙션 박스 */
  .mission-box {{
    background: #1e2436;
    border: 3px solid #3b82f6;
    border-radius: 16px;
    padding: 16px;
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
    box-shadow: 0 6px 18px rgba(0,0,0,0.45);
  }}
  .step-box {{
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px;
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
    padding: 8px 14px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    margin-right: 6px;
  }}
  .btn-tts:hover {{ background: #1d4ed8; }}
  .btn-mic {{
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
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
    padding: 10px 12px;
    font-size: 16px;
    font-weight: 700;
    border-radius: 8px;
    border: 2px solid #64748b;
    background: #1e293b;
    color: #f8fafc;
    margin-top: 6px;
  }}
  .eng-input:focus {{
    outline: none;
    border-color: #facc15;
  }}
  .btn-submit {{
    width: 100%;
    margin-top: 8px;
    padding: 10px;
    background: #10b981;
    color: #064e3b;
    font-size: 15px;
    font-weight: 900;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }}
  .btn-submit:hover {{ background: #34d399; }}

  /* 중앙 자물쇠 해제 컷인 오버레이 */
  #cutin-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.78);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    animation: fadeIn 0.25s ease;
  }}
  #cutin-overlay img {{
    max-width: 720px;
    width: 88%;
    border-radius: 20px;
    border: 4px solid #facc15;
    box-shadow: 0 0 50px rgba(250, 204, 21, 0.75);
  }}
  .cutin-caption {{
    margin-top: 14px;
    font-size: 26px;
    font-weight: 900;
    color: #fde047;
    text-shadow: 0 3px 12px rgba(0,0,0,0.9);
  }}

  /* 최종 클리어 모달 */
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
    box-shadow: 0 20px 60px rgba(0,0,0,0.8);
  }}
  .ending-badges {{
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 12px 0;
  }}
  .ending-badges img {{
    width: 82px;
    height: 82px;
    border-radius: 14px;
    border: 3px solid #fbbf24;
  }}
</style>
</head>
<body>

<!-- 1. 로비 화면 -->
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

<!-- 2. 메인 게임 화면 -->
<div id="game-screen">
  <div class="top-hud">
    <div id="player-badge" class="hud-badge badge-p1">🔴 1번 산타 요원</div>
    <div style="font-size:14px; color:#cbd5e1; font-weight:700;">
      방향키(WASD / ↑↓←→) 이동 · <b>Space</b> 또는 <b>[조사 / 대화]</b>
    </div>
    <div class="key-slots">
      <div id="slot-0" class="key-slot">🍳 Kitchen</div>
      <div id="slot-1" class="key-slot">🛏️ Bedroom</div>
      <div id="slot-2" class="key-slot">🛋️ Living</div>
      <div id="slot-3" class="key-slot">🌲 Garden</div>
    </div>
  </div>

  <div class="main-arena">
    <!-- 왼쪽: 2D RPG 맵 -->
    <div class="map-panel">
      <canvas id="rpgCanvas" width="760" height="540"></canvas>
      <div class="controls-bar">
        <div class="dpad">
          <div></div>
          <button onpointerdown="moveStep(0,-24)">▲</button>
          <div></div>
          <button onpointerdown="moveStep(-24,0)">◀</button>
          <button onpointerdown="moveStep(0,24)">▼</button>
          <button onpointerdown="moveStep(24,0)">▶</button>
        </div>
        <div style="font-size:13px; color:#94a3b8; text-align:center;">
          빛나는 <b>보물 상자</b> 가까이 가서<br>조사 버튼을 눌러보세요!
        </div>
        <button class="action-btn" onclick="interact()">🔍 조사 / 대화 (Space)</button>
      </div>
    </div>

    <!-- 오른쪽: 무전 대화창 & 3단 학습 미션 -->
    <div class="right-panel">
      <!-- 스타듀 밸리풍 대화창 -->
      <div class="dialogue-box">
        <div id="portrait-frame" class="portrait-frame">
          <img id="portrait-img" alt="캐릭터 초상화" />
        </div>
        <div class="dialogue-content">
          <div id="speaker-tag" class="speaker-tag">🎅 산타 본부 무전</div>
          <div id="dialogue-text" class="dialogue-text">
            요원, 출동 준비 완료! 우리 구역 방 안의 반짝이는 보물 상자를 찾아가 조사해 보자!
          </div>
        </div>
      </div>
      <!-- 미션 수행 박스 -->
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

<!-- 3. 중앙 자물쇠 해제 컷인 오버레이 -->
<div id="cutin-overlay">
  <img id="cutin-img" alt="협동 자물쇠 해제!" />
  <div class="cutin-caption">✨ 짝꿍과 힘을 합쳐 마법 자물쇠를 열었습니다! ✨</div>
</div>

<!-- 4. 최종 클리어 모달 -->
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

// 이미지 객체 프리로드
const IMGS = {{}};
for (const [k, src] of Object.entries(ASSETS)) {{
  if (src) {{
    const img = new Image();
    img.src = src;
    IMGS[k] = img;
  }}
}}

// 초기 로비 이미지 바인딩
if (ASSETS.title_banner) {{
  document.getElementById("banner-container").innerHTML = `<img src="${{ASSETS.title_banner}}" alt="Santa's Secret Mission" />`;
}}
if (ASSETS.portrait_p1) document.getElementById("lobby-p1-img").src = ASSETS.portrait_p1;
if (ASSETS.portrait_p2) document.getElementById("lobby-p2-img").src = ASSETS.portrait_p2;
if (ASSETS.unlock_cutin) document.getElementById("cutin-img").src = ASSETS.unlock_cutin;
if (ASSETS.complete) document.getElementById("complete-img").src = ASSETS.complete;
if (ASSETS.santa_happy) document.getElementById("end-santa-img").src = ASSETS.santa_happy;

// Web Audio 레트로 효과음
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSFX(type) {{
  if (audioCtx.state === "suspended") audioCtx.resume();
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  const now = audioCtx.currentTime;

  if (type === "step") {{
    osc.type = "triangle";
    osc.frequency.setValueAtTime(190, now);
    gain.gain.setValueAtTime(0.03, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
    osc.start(now); osc.stop(now + 0.05);
  }} else if (type === "open") {{
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

// 원어민 음성 듣기 (TTS)
function speakEnglish(text) {{
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US";
  u.rate = 0.88;
  const frame = document.getElementById("portrait-frame");
  frame.classList.add("speaking");
  u.onend = () => frame.classList.remove("speaking");
  window.speechSynthesis.speak(u);
}}

// 4개 방 핵심 미션 데이터 (cards.png 2x2 그리드 연동)
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
    crop: [0, 0], // cards.png 좌상단
    chestPos: {{ x: 175, y: 145 }},
    decoyPos: {{ x: 285, y: 195 }},
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
    crop: [1, 0], // cards.png 우상단
    chestPos: {{ x: 585, y: 145 }},
    decoyPos: {{ x: 475, y: 200 }},
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
    crop: [0, 1], // cards.png 좌하단
    chestPos: {{ x: 165, y: 395 }},
    decoyPos: {{ x: 280, y: 345 }},
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
    crop: [1, 1], // cards.png 우하단
    chestPos: {{ x: 595, y: 395 }},
    decoyPos: {{ x: 485, y: 350 }},
    decoyImg: "decoy_garden",
    decoyText: "앗, 꽝! 귀여운 눈사람(a cute snowman)이 인사하고 있어요! 다른 상자를 찾아보세요."
  }}
];

// 중앙 통로 마법 자물쇠 2개 (좌우 통로를 가로막아 짝꿍 질문 유도)
const GATES = [
  {{ id: "top_gate", x: 380, y: 155, unlocked: false, targetRoomForP1: 1, targetRoomForP2: 0 }},
  {{ id: "bot_gate", x: 380, y: 395, unlocked: false, targetRoomForP1: 3, targetRoomForP2: 2 }}
];

let playerRole = 1;
let player = {{ x: 210, y: 240, speed: 5 }};
let keysPressed = {{}};
let unlockedRooms = [false, false, false, false];
let openedDecoys = [false, false, false, false];
let currentMissionState = null;

// 대화창 초상화 업데이트
function setDialogue(portraitKey, speaker, text) {{
  const pImg = document.getElementById("portrait-img");
  if (ASSETS[portraitKey]) pImg.src = ASSETS[portraitKey];
  document.getElementById("speaker-tag").innerText = speaker;
  document.getElementById("dialogue-text").innerHTML = text;
}}

function startGame(role) {{
  playerRole = role;
  document.getElementById("lobby-screen").style.display = "none";
  document.getElementById("game-screen").style.display = "block";

  const badge = document.getElementById("player-badge");
  if (role === 1) {{
    badge.className = "hud-badge badge-p1";
    badge.innerText = "🔴 1번 산타 요원 (주방 · 거실 담당)";
    player.x = 220; player.y = 220;
    document.getElementById("end-agent-img").src = ASSETS.portrait_p1 || "";
    setDialogue("portrait_p1", "🔴 1번 산타 요원", "출동 완료! 먼저 왼쪽 <b>주방(위)</b>과 <b>거실(아래)</b>에 숨겨진 보물 상자를 조사하자!");
  }} else {{
    badge.className = "hud-badge badge-p2";
    badge.innerText = "🟢 2번 엘프 요원 (침실 · 정원 담당)";
    player.x = 540; player.y = 220;
    document.getElementById("end-agent-img").src = ASSETS.portrait_p2 || "";
    setDialogue("portrait_p2", "🟢 2번 엘프 요원", "출동 완료! 먼저 오른쪽 <b>침실(위)</b>과 <b>정원(아래)</b>에 숨겨진 보물 상자를 조사하자!");
  }}
  requestAnimationFrame(gameLoop);
}}

// 키보드 이동
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

function moveStep(dx, dy) {{
  tryMove(dx, dy);
  playSFX("step");
}}

function tryMove(dx, dy) {{
  let nx = Math.max(45, Math.min(715, player.x + dx));
  let ny = Math.max(55, Math.min(485, player.y + dy));

  // 잠긴 중앙 자물쇠 게이트 통과 차단
  for (const g of GATES) {{
    if (!g.unlocked) {{
      const dist = Math.hypot(nx - g.x, ny - g.y);
      if (dist < 48) return;
    }}
  }}
  player.x = nx;
  player.y = ny;
}}

// 근접 오브젝트 조사 & 짝꿍 자물쇠 상호작용
function interact() {{
  // 1. 중앙 마법 자물쇠(🔒) 확인
  for (const g of GATES) {{
    if (!g.unlocked && Math.hypot(player.x - g.x, player.y - g.y) < 78) {{
      openGateChallenge(g);
      return;
    }}
  }}

  // 2. 보물 상자(진짜 / 꽝) 확인
  for (const r of ROOMS) {{
    // 진짜 보물 상자
    if (Math.hypot(player.x - r.chestPos.x, player.y - r.chestPos.y) < 62) {{
      if (r.owner !== playerRole && !unlockedRooms[r.id]) {{
        setDialogue("santa_panic", "🎅 산타 본부", "그 방은 짝꿍 요원의 담당 구역이에요! 먼저 중앙 마법 자물쇠를 열어 짝꿍에게 물어보세요!");
        playSFX("error");
        return;
      }}
      openTreasureMission(r);
      return;
    }}
    // 꽝 보물 상자
    if (Math.hypot(player.x - r.decoyPos.x, player.y - r.decoyPos.y) < 58) {{
      openedDecoys[r.id] = true;
      playSFX("decoy");
      setDialogue("santa_panic", "🎅 앗, 함정 상자!", r.decoyText);
      renderDecoyCard(r);
      return;
    }}
  }}

  setDialogue(playerRole === 1 ? "portrait_p1" : "portrait_p2", "🔍 주변 탐색", "근처에 조사할 상자가 없어요. 반짝이는 <b>보물 상자</b>나 <b>황금 자물쇠</b> 가까이 다가가 보세요!");
}}

// 꽝 카드 출력
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

// 진짜 보물 상자 3단 학습 미션 (1. 듣기 -> 2. 쓰기 -> 3. 음성인식 말하기)
function openTreasureMission(room) {{
  playSFX("open");
  const myPortrait = playerRole === 1 ? "portrait_p1" : "portrait_p2";
  setDialogue(myPortrait, `📦 ${{room.roomKo}}(${{room.roomName}}) 보물 발견!`,
    `우와! <b>${{room.itemLabel}}</b> 단서를 찾았어요!<br>원어민 발음을 듣고 영어 문장을 완성한 뒤, 짝꿍에게 알려줄 수 있게 저장하세요!`);

  const panel = document.getElementById("mission-panel");
  panel.innerHTML = `
    <div>
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:900; color:#fde047; font-size:16px;">✨ ${{room.roomName}} 보물 단서</span>
        <span style="font-size:12px; background:#1e3a8a; padding:3px 8px; border-radius:6px;">Step 1 → 2 → 3</span>
      </div>
      <div class="card-preview">
        <div class="card-canvas-wrap">
          <canvas id="cardCropCanvas" width="160" height="160"></canvas>
        </div>
        <div style="font-size:13px; color:#93c5fd; margin-top:4px; font-weight:700;">질문: "${{room.question}}"</div>
      </div>

      <div class="step-box">
        <div class="step-title">1단계: 원어민 음성 듣기</div>
        <button class="btn-tts" onclick="speakEnglish('${{room.question}}')">🔊 질문 듣기</button>
        <button class="btn-tts" onclick="speakEnglish('${{room.answer}}')">🔊 정답 문장 듣기</button>
      </div>

      <div class="step-box">
        <div class="step-title">2단계: 정답 문장 직접 쓰기</div>
        <input id="mission-write-input" class="eng-input" type="text" placeholder="예: There is a ..." autocomplete="off" />
        <button class="btn-submit" onclick="checkMissionWrite(${{room.id}})">✅ 문장 확인하기</button>
      </div>

      <div class="step-box" id="speak-step-box" style="opacity:0.45; pointer-events:none;">
        <div class="step-title">3단계: 마이크 눌러 따라 읽기 (발음 인증)</div>
        <button id="mic-btn" class="btn-mic" onclick="startSpeechCheck(${{room.id}})">🎤 말하기 시작</button>
        <span id="speech-result" style="font-size:13px; margin-left:8px; color:#cbd5e1;">2단계를 먼저 통과하세요</span>
      </div>
    </div>
  `;

  // cards.png 2x2 크롭 렌더링
  const c = document.getElementById("cardCropCanvas");
  const ctx = c.getContext("2d");
  if (IMGS.cards && IMGS.cards.complete) {{
    const sw = IMGS.cards.width / 2;
    const sh = IMGS.cards.height / 2;
    ctx.drawImage(IMGS.cards, room.crop[0] * sw, room.crop[1] * sh, sw, sh, 0, 0, 160, 160);
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
    playSFX("success");
    setDialogue("santa_happy", "😎 산타 교관", `완벽해요! <b>"${{room.answer}}"</b> 정확한 문장이에요!<br>이제 아래 <b>3단계 마이크 버튼</b>을 눌러 큰 소리로 따라 읽어보세요!`);
    const speakBox = document.getElementById("speak-step-box");
    speakBox.style.opacity = "1";
    speakBox.style.pointerEvents = "auto";
    document.getElementById("speech-result").innerText = "버튼을 누르고 문장을 말해보세요!";
    speakEnglish(room.answer);
  }} else {{
    playSFX("error");
    setDialogue("santa_panic", "🎅 산타 교관", `앗, 철자나 단·복수(<b>There is / There are</b>)를 다시 확인해 볼까요?<br>힌트: <b>${{room.answer}}</b>`);
  }}
}}

// 음성 인식 (Web Speech API) + 폴백 지원
function startSpeechCheck(roomId) {{
  const room = ROOMS[roomId];
  const resSpan = document.getElementById("speech-result");
  const micBtn = document.getElementById("mic-btn");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {{
    completeRoomMission(roomId, "(음성인식 미지원 브라우저 자동 통과)");
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
      resSpan.innerText = `인식된 말: "${{spoken}}" — 핵심 단어(${{keyWord}})를 또박또박 다시 말해보세요!`;
    }}
  }};
  recog.onerror = () => {{
    micBtn.classList.remove("listening");
    micBtn.innerText = "🎤 말하기 시작";
    resSpan.innerHTML = `마이크 인식이 어렵다면 <button class="btn-tts" style="padding:3px 8px;font-size:12px;" onclick="completeRoomMission(${{roomId}}, '직접 발음 확인 완료')">발음 연습 완료 처리</button>`;
  }};
  recog.start();
}}

function completeRoomMission(roomId, spokenText) {{
  const room = ROOMS[roomId];
  unlockedRooms[roomId] = true;
  document.getElementById(`slot-${{roomId}}`).classList.add("unlocked");
  playSFX("success");
  setDialogue("santa_happy", "😎 산타 교관",
    `멋진 발음이에요! (${{spokenText}})<br>이제 짝꿍이 <b>"${{room.question}}"</b>라고 물어보면 <b>"${{room.answer}}"</b>라고 대답해 주세요!`);

  document.getElementById("mission-panel").innerHTML = `
    <div style="text-align:center; padding:24px 10px;">
      <div style="font-size:44px; margin-bottom:8px;">🔑</div>
      <div style="font-size:19px; font-weight:900; color:#fde047; margin-bottom:8px;">
        ${{room.roomName}} 열쇠 문장 획득 완료!
      </div>
      <div style="background:#0f172a; border:2px solid #facc15; border-radius:12px; padding:12px; font-size:18px; font-weight:900; color:#fff; margin-bottom:12px;">
        "${{room.answer}}"
      </div>
      <p style="font-size:13.5px; color:#cbd5e1; line-height:1.5;">
        짝꿍에게 이 문장을 영어로 알려주고,<br>
        이제 중앙 통로의 <b>황금 마법 자물쇠</b> 앞으로 가서 짝꿍 방의 단서를 물어보세요!
      </p>
    </div>
  `;
  checkAllClear();
}}

// 중앙 마법 자물쇠(🔒) 짝꿍 질문 챌린지 (상대방 초상화로 전환!)
function openGateChallenge(gate) {{
  const targetRoomId = playerRole === 1 ? gate.targetRoomForP1 : gate.targetRoomForP2;
  const targetRoom = ROOMS[targetRoomId];
  const partnerPortrait = playerRole === 1 ? "portrait_p2" : "portrait_p1";
  const partnerName = playerRole === 1 ? "🟢 2번 엘프 짝꿍에게 질문하기!" : "🔴 1번 산타 짝꿍에게 질문하기!";

  playSFX("open");
  // 핵심 연출: 대화창 얼굴을 짝꿍 초상화로 변경하여 '짝꿍에게 물어볼 타이밍'임을 직관적 안내!
  setDialogue(partnerPortrait, partnerName,
    `옆자리 짝꿍을 보고 영어로 크게 질문해 보세요!<br>👉 <b style="color:#fde047; font-size:17px;">"${{targetRoom.question}}"</b>`);

  const panel = document.getElementById("mission-panel");
  panel.innerHTML = `
    <div>
      <div style="text-align:center; margin-bottom:8px;">
        <img src="${{ASSETS.magic_lock || ''}}" style="width:86px; height:86px; object-fit:contain;" />
        <div style="font-size:17px; font-weight:900; color:#fbbf24;">🔒 마법 자물쇠 해제 작전</div>
      </div>

      <div class="step-box">
        <div class="step-title">1단계: 짝꿍에게 영어로 질문하기</div>
        <div style="font-size:16px; font-weight:900; color:#fde047; margin-bottom:6px;">
          "${{targetRoom.question}}"
        </div>
        <button class="btn-tts" onclick="speakEnglish('${{targetRoom.question}}')">🔊 질문 발음 들어보기</button>
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

    // 2.5초간 협동 자물쇠 해제 컷인(unlock_cutin.png) 출력!
    const cutin = document.getElementById("cutin-overlay");
    cutin.style.display = "flex";
    setTimeout(() => {{
      cutin.style.display = "none";
      checkAllClear();
    }}, 2500);

    setDialogue("santa_happy", "😎 자물쇠 해제 성공!",
      `대단해요! 짝꿍과 힘을 합쳐 <b>${{targetRoom.roomName}}</b> 통로를 열었어요!<br>다음 구역 자물쇠도 마저 열어 4개의 열쇠를 모두 모아보세요!`);
    document.getElementById("mission-panel").innerHTML = `
      <div style="text-align:center; padding:30px 10px;">
        <div style="font-size:44px; margin-bottom:8px;">🔓</div>
        <div style="font-size:18px; font-weight:900; color:#4ade80;">마법 자물쇠가 열렸습니다!</div>
        <p style="font-size:14px; color:#cbd5e1; margin-top:8px;">이제 열린 통로를 지나 반대편 구역도 자유롭게 이동할 수 있어요!</p>
      </div>
    `;
  }} else {{
    playSFX("error");
    setDialogue("santa_panic", "🎅 암호 불일치!",
      `앗, 자물쇠가 열리지 않아요! 짝꿍에게 <b>"${{targetRoom.question}}"</b>라고 다시 한 번 정확히 물어보고 철자를 확인해 보세요!`);
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

// 캔버스 렌더링 루프
const canvas = document.getElementById("rpgCanvas");
const ctx = canvas.getContext("2d");

function updateMovement() {{
  let dx = 0, dy = 0;
  if (keysPressed["arrowup"] || keysPressed["w"]) dy -= player.speed;
  if (keysPressed["arrowdown"] || keysPressed["s"]) dy += player.speed;
  if (keysPressed["arrowleft"] || keysPressed["a"]) dx -= player.speed;
  if (keysPressed["arrowright"] || keysPressed["d"]) dx += player.speed;
  if (dx !== 0 || dy !== 0) tryMove(dx, dy);
}}

function drawGame() {{
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 1. 배경 맵
  if (IMGS.map && IMGS.map.complete) {{
    ctx.drawImage(IMGS.map, 0, 0, canvas.width, canvas.height);
  }} else {{
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }}

  // 2. 보물 상자 (진짜 + 꽝)
  const tick = Date.now() / 300;
  for (const r of ROOMS) {{
    // 내 구역이거나 이미 열린 방의 진짜 상자 표시
    if (r.owner === playerRole || unlockedRooms[r.id]) {{
      drawChest(r.chestPos.x, r.chestPos.y, unlockedRooms[r.id], tick);
    }}
    // 내 구역의 코믹 꽝 상자 표시
    if (r.owner === playerRole && !openedDecoys[r.id]) {{
      drawChest(r.decoyPos.x, r.decoyPos.y, false, tick + 1.5);
    }}
  }}

  // 3. 중앙 통로 마법 자물쇠 (obj_magic_lock.png)
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

  // 4. 플레이어 캐릭터 (초상화 원형 배지 + 발광 링)
  ctx.save();
  ctx.beginPath();
  ctx.arc(player.x, player.y, 24, 0, Math.PI * 2);
  ctx.fillStyle = playerRole === 1 ? "#ef4444" : "#22c55e";
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#fde047";
  ctx.stroke();

  const avatarImg = playerRole === 1 ? IMGS.portrait_p1 : IMGS.portrait_p2;
  if (avatarImg && avatarImg.complete) {{
    ctx.clip();
    ctx.drawImage(avatarImg, player.x - 22, player.y - 22, 44, 44);
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

components.html(html_code, height=740, scrolling=False)
