"""
frontend/app.py — MeetingIQ Streamlit Frontend
Run with: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import time
from typing import Optional

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="MeetingIQ",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS & animated background ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #0e0f13;
    --bg2:       #13151b;
    --bg3:       #181b23;
    --surface:   #1d2029;
    --border:    #272b36;
    --border2:   #2e3340;
    --gold:      #c9a84c;
    --gold-soft: #e8c97a;
    --gold-dim:  #7a6230;
    --cream:     #f0ebe0;
    --text:      #d8d4cc;
    --text2:     #8a8880;
    --text3:     #555250;
    --green:     #4caf82;
    --red:       #c9504c;
    --amber:     #c9934c;
    --blue:      #4c82c9;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

[data-testid="stHeader"]     { background: transparent !important; display: none; }
[data-testid="stSidebar"]    { display: none !important; }
#MainMenu, footer, header    { visibility: hidden; }
.stDeployButton              { display: none; }

.main .block-container {
    max-width: 1080px !important;
    padding: 0 2rem 6rem !important;
    position: relative;
    z-index: 1;
}

/* ── Animated background canvas ── */
#bg-canvas {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}

/* ── Grain overlay ── */
body::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── Nav ── */
.miq-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.6rem 0 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
    position: relative;
}
.miq-nav::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 80px; height: 1px;
    background: var(--gold);
}
.miq-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: 0.01em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.miq-logo-mark {
    width: 28px; height: 28px;
    background: var(--gold);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; color: var(--bg);
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
}
.miq-nav-right {
    display: flex; align-items: center; gap: 16px;
}
.miq-nav-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    color: var(--gold);
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.2);
    padding: 4px 12px;
    border-radius: 2px;
}
.miq-nav-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 2.5s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.75); }
}

/* ── Hero ── */
.miq-hero {
    padding: 3.5rem 0 3rem;
    position: relative;
}
.miq-hero-kicker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 10px;
}
.miq-hero-kicker::before {
    content: '';
    display: inline-block;
    width: 24px; height: 1px;
    background: var(--gold);
}
.miq-hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 4.5vw, 3.8rem);
    font-weight: 700;
    color: var(--cream);
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-bottom: 1.4rem;
}
.miq-hero-title em {
    font-style: italic;
    color: var(--gold-soft);
}
.miq-hero-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--text2);
    line-height: 1.7;
    max-width: 420px;
    font-weight: 300;
}

/* ── Upload card ── */
.miq-upload-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2.4rem 2.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.miq-upload-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold-dim), transparent);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text3) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.4rem !important;
    text-transform: uppercase;
    border-radius: 0 !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }
.stTabs [data-baseweb="tab-panel"]     { padding: 0 !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase;
    border-radius: 2px !important;
    border: none !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: var(--gold) !important;
    color: #0a0b0e !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--gold-soft) !important;
    box-shadow: 0 0 28px rgba(201,168,76,0.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--gold-dim) !important;
    color: var(--gold-soft) !important;
}
.stDownloadButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    background: transparent !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: var(--gold) !important;
    color: var(--gold-soft) !important;
    background: rgba(201,168,76,0.05) !important;
}

/* ── Text inputs ── */
.stTextArea textarea {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.7 !important;
}
.stTextArea textarea:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.06) !important;
}
.stTextInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
}
.stTextInput input:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.06) !important;
}
.stTextInput label, .stTextArea label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text3) !important;
    text-transform: uppercase !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 2px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--gold-dim) !important; }
[data-testid="stFileUploader"] section { background: transparent !important; }
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text3) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* ── Progress ── */
.stProgress > div > div {
    background: var(--gold) !important;
    border-radius: 0 !important;
}
.stProgress > div {
    background: var(--border) !important;
    border-radius: 0 !important;
    height: 2px !important;
}

/* ── Stat cards ── */
.miq-stats {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.miq-stat {
    background: var(--bg2);
    padding: 1.4rem 1.2rem;
    text-align: center;
    transition: background 0.2s;
}
.miq-stat:hover { background: var(--bg3); }
.miq-stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--gold-soft);
    line-height: 1;
    margin-bottom: 6px;
}
.miq-stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    color: var(--text3);
    text-transform: uppercase;
}

/* ── Section heading ── */
.miq-section {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 2rem 0 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.miq-section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--cream);
    letter-spacing: -0.01em;
}
.miq-section-count {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--gold);
    letter-spacing: 0.1em;
    margin-left: auto;
}

/* ── Cards ── */
.miq-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 6px;
    transition: border-color 0.2s, background 0.2s;
    position: relative;
}
.miq-card:hover {
    border-color: var(--border2);
    background: var(--bg3);
}
.miq-card-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    color: var(--text);
    line-height: 1.5;
    margin-bottom: 8px;
}
.miq-card-meta {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
}
.miq-card-person {
    color: var(--gold-soft);
    font-size: 0.68rem;
}
.miq-card-date {
    color: var(--text2);
}

/* ── Badges ── */
.miq-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    padding: 2px 7px;
    border-radius: 1px;
    text-transform: uppercase;
    font-weight: 500;
}
.miq-badge-high     { background: rgba(201,80,76,0.12);  color: #e07070; border: 1px solid rgba(201,80,76,0.2); }
.miq-badge-medium   { background: rgba(201,147,76,0.12); color: #dda060; border: 1px solid rgba(201,147,76,0.2); }
.miq-badge-low      { background: rgba(76,175,130,0.12); color: #6dcca0; border: 1px solid rgba(76,175,130,0.2); }
.miq-badge-decided  { background: rgba(76,175,130,0.12); color: #6dcca0; border: 1px solid rgba(76,175,130,0.2); }
.miq-badge-deferred { background: rgba(201,147,76,0.12); color: #dda060; border: 1px solid rgba(201,147,76,0.2); }
.miq-badge-pending  { background: rgba(201,80,76,0.12);  color: #e07070; border: 1px solid rgba(201,80,76,0.2); }

/* ── Report header ── */
.miq-report-header {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.miq-report-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--gold), transparent 60%);
}
.miq-report-kicker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.miq-report-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: -0.02em;
    line-height: 1.25;
}

/* ── Risk alert ── */
.miq-risk-alert {
    background: rgba(201,80,76,0.06);
    border: 1px solid rgba(201,80,76,0.2);
    border-left: 2px solid var(--red);
    border-radius: 2px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #e07070;
    letter-spacing: 0.04em;
}

/* ── Step list ── */
.miq-step {
    display: flex;
    gap: 14px;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--border);
    align-items: flex-start;
}
.miq-step:last-child { border-bottom: none; }
.miq-step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--gold);
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.15);
    width: 20px; height: 20px;
    border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.miq-step-text {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.5;
    font-weight: 300;
}

/* ── Person chip ── */
.miq-people-row {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-bottom: 1.5rem;
}
.miq-person-chip {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--bg3);
    border: 1px solid var(--border2);
    border-radius: 2px;
    padding: 5px 12px 5px 6px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.78rem;
    color: var(--text);
}
.miq-avatar {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, var(--gold-dim), var(--gold));
    border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--bg);
    font-weight: 500;
    flex-shrink: 0;
}

/* ── Financial amount ── */
.miq-amount {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--gold-soft);
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}

/* ── Question card ── */
.miq-question {
    border-left: 2px solid var(--gold-dim);
    padding-left: 1rem;
    margin-bottom: 10px;
}

/* ── Date display ── */
.miq-date-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}

/* ── Divider line ── */
.miq-divider {
    height: 1px;
    background: var(--border);
    margin: 1.8rem 0;
}

/* ── Email preview ── */
.miq-email-preview {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.4rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--text3);
    line-height: 1.9;
    white-space: pre-wrap;
    margin-top: 1.5rem;
}

/* ── How it works row ── */
.miq-how {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
    margin-top: 3rem;
}
.miq-how-item {
    background: var(--bg2);
    padding: 1.6rem 1.4rem;
}
.miq-how-num {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--border2);
    line-height: 1;
    margin-bottom: 0.8rem;
}
.miq-how-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.miq-how-body {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: var(--text3);
    line-height: 1.6;
    font-weight: 300;
}

/* ── Alert overrides ── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* ── Animations ── */
@keyframes fade-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.miq-animate { animation: fade-up 0.5s ease both; }
.miq-animate-2 { animation: fade-up 0.5s 0.1s ease both; }
.miq-animate-3 { animation: fade-up 0.5s 0.2s ease both; }

</style>

<!-- Animated canvas background -->
<canvas id="bg-canvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('bg-canvas');
    const ctx    = canvas.getContext('2d');

    function resize() {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Floating dust particles
    const PARTICLE_COUNT = 55;
    const particles = Array.from({length: PARTICLE_COUNT}, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        r: Math.random() * 1.2 + 0.2,
        vx: (Math.random() - 0.5) * 0.18,
        vy: (Math.random() - 0.5) * 0.12,
        o: Math.random() * 0.4 + 0.05,
    }));

    // Slow-breathing mesh gradient orbs
    let t = 0;
    function draw() {
        t += 0.004;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Orb 1 — warm amber, top-left
        const g1 = ctx.createRadialGradient(
            canvas.width * 0.15 + Math.sin(t * 0.7) * 60,
            canvas.height * 0.2 + Math.cos(t * 0.5) * 40,
            0,
            canvas.width * 0.15, canvas.height * 0.2, canvas.width * 0.38
        );
        g1.addColorStop(0, 'rgba(180,130,40,0.055)');
        g1.addColorStop(1, 'rgba(180,130,40,0)');
        ctx.fillStyle = g1;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Orb 2 — cool slate, bottom-right
        const g2 = ctx.createRadialGradient(
            canvas.width * 0.82 + Math.sin(t * 0.4 + 1) * 50,
            canvas.height * 0.75 + Math.cos(t * 0.6 + 2) * 35,
            0,
            canvas.width * 0.82, canvas.height * 0.75, canvas.width * 0.42
        );
        g2.addColorStop(0, 'rgba(60,80,140,0.045)');
        g2.addColorStop(1, 'rgba(60,80,140,0)');
        ctx.fillStyle = g2;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Orb 3 — subtle centre
        const g3 = ctx.createRadialGradient(
            canvas.width * 0.5 + Math.sin(t * 0.3) * 30,
            canvas.height * 0.45 + Math.cos(t * 0.4) * 20,
            0,
            canvas.width * 0.5, canvas.height * 0.45, canvas.width * 0.28
        );
        g3.addColorStop(0, 'rgba(140,110,50,0.025)');
        g3.addColorStop(1, 'rgba(140,110,50,0)');
        ctx.fillStyle = g3;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Particles
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(201,168,76,${p.o})`;
            ctx.fill();
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < -5)  p.x = canvas.width + 5;
            if (p.x > canvas.width + 5)  p.x = -5;
            if (p.y < -5)  p.y = canvas.height + 5;
            if (p.y > canvas.height + 5) p.y = -5;
        });

        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def nav():
    st.markdown("""
    <div class="miq-nav miq-animate">
        <div class="miq-logo">
            <div class="miq-logo-mark">M</div>
            MeetingIQ
        </div>
        <div class="miq-nav-right">
            <div class="miq-nav-pill">AI Intelligence</div>
            <div class="miq-nav-dot" title="API online"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def badge(value: str, kind: str = "priority") -> str:
    v = (value or "").upper()
    if kind == "priority":
        cls = {"HIGH": "miq-badge-high", "MEDIUM": "miq-badge-medium", "LOW": "miq-badge-low"}.get(v, "miq-badge-low")
    else:
        cls = {"DECIDED": "miq-badge-decided", "DEFERRED": "miq-badge-deferred", "PENDING": "miq-badge-pending"}.get(v, "miq-badge-pending")
    return f'<span class="miq-badge {cls}">{v}</span>'


def section(icon: str, title: str, count: int = None):
    count_html = f'<span class="miq-section-count">{count} items</span>' if count is not None else ""
    st.markdown(f"""
    <div class="miq-section">
        <span style="font-size:0.9rem">{icon}</span>
        <span class="miq-section-title">{title}</span>
        {count_html}
    </div>
    """, unsafe_allow_html=True)


def stat_row(report: dict):
    n_a = len(report.get("action_items", []))
    n_r = len(report.get("risks", []))
    n_f = len(report.get("financial_items", []))
    n_p = len(report.get("people", []))
    n_q = len(report.get("unresolved_questions", []))
    st.markdown(f"""
    <div class="miq-stats">
        <div class="miq-stat"><div class="miq-stat-num">{n_a}</div><div class="miq-stat-label">Actions</div></div>
        <div class="miq-stat"><div class="miq-stat-num">{n_r}</div><div class="miq-stat-label">Risks</div></div>
        <div class="miq-stat"><div class="miq-stat-num">{n_f}</div><div class="miq-stat-label">Financials</div></div>
        <div class="miq-stat"><div class="miq-stat-num">{n_p}</div><div class="miq-stat-label">People</div></div>
        <div class="miq-stat"><div class="miq-stat-num">{n_q}</div><div class="miq-stat-label">Questions</div></div>
    </div>
    """, unsafe_allow_html=True)


def call_api(endpoint: str, **kwargs) -> Optional[dict]:
    try:
        r = requests.request(url=f"{API_BASE}{endpoint}", **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to MeetingIQ API — is `uvicorn main:app` running on port 8000?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.status_code} — {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def empty_state(msg: str):
    st.markdown(f"""
    <div style="padding:2rem 0;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
                color:var(--text3);letter-spacing:0.06em">— {msg} —</div>
    """, unsafe_allow_html=True)


# ── Upload page ───────────────────────────────────────────────────────────────

def page_upload():
    nav()

    st.markdown("""
    <div class="miq-hero miq-animate">
        <div class="miq-hero-kicker">AI Meeting Intelligence</div>
        <div class="miq-hero-title">Every meeting,<br><em>perfectly distilled.</em></div>
        <div class="miq-hero-sub">Upload a recording or paste a transcript — the AI extracts every decision, action, risk, and commitment in seconds.</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  Upload File  ", "  Paste Transcript  "])

    with tab1:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Drop your file",
            type=["mp3", "mp4", "wav", "m4a", "ogg", "webm", "pdf", "docx", "txt"],
            label_visibility="collapsed",
        )
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;
                    color:var(--text3);text-align:center;margin-top:6px;text-transform:uppercase">
            MP3 · MP4 · WAV · M4A · PDF · DOCX · TXT
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("◈  Analyse Meeting", key="btn_file", type="primary", use_container_width=True):
                if not uploaded:
                    st.warning("Please upload a file first.")
                else:
                    _run_analysis(file=uploaded)

    with tab2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        transcript = st.text_area(
            "Transcript",
            placeholder="Sarah: Let's kick off with the Q3 roadmap...\nMarcus: Agreed. Our primary target is...",
            height=270,
            label_visibility="collapsed",
        )
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("◈  Analyse Meeting", key="btn_text", type="primary", use_container_width=True):
                if not transcript or not transcript.strip():
                    st.warning("Please paste a transcript first.")
                else:
                    _run_analysis(text=transcript)

    st.markdown("""
    <div class="miq-how miq-animate-3">
        <div class="miq-how-item">
            <div class="miq-how-num">01</div>
            <div class="miq-how-title">Upload</div>
            <div class="miq-how-body">Any format — audio, PDF, Word, or plain text. Whisper handles transcription automatically.</div>
        </div>
        <div class="miq-how-item">
            <div class="miq-how-num">02</div>
            <div class="miq-how-title">Analyse</div>
            <div class="miq-how-body">Nine AI tools run sequentially, extracting actions, decisions, financials, risks, and more.</div>
        </div>
        <div class="miq-how-item">
            <div class="miq-how-num">03</div>
            <div class="miq-how-title">Distribute</div>
            <div class="miq-how-body">Download a branded PDF or PowerPoint. Send to all attendees in one click.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _run_analysis(file=None, text=None):
    tools = [
        "Core Summary & Decisions",
        "Action Items",
        "Financial Items",
        "Priorities",
        "Targets & Commitments",
        "Unresolved Questions",
        "People & Roles",
        "Dates & Deadlines",
        "Risks & Blockers",
    ]

    pb     = st.progress(0)
    status = st.empty()
    result = None

    for i, tool in enumerate(tools):
        pb.progress(i / len(tools))
        status.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                    color:var(--gold);letter-spacing:0.08em;text-align:center;
                    padding:4px 0">
            {i+1} / {len(tools)} &nbsp;·&nbsp; {tool}
        </div>
        """, unsafe_allow_html=True)

        if i == 0:
            if file is not None:
                result = call_api("/analyse", method="POST",
                                  files={"file": (file.name, file.getvalue(), file.type)},
                                  timeout=120)
            else:
                result = call_api("/analyse", method="POST",
                                  data={"text": text},
                                  timeout=120)
            if result is None:
                pb.empty(); status.empty(); return

        time.sleep(0.16)

    pb.progress(1.0)
    time.sleep(0.3)
    pb.empty(); status.empty()

    if result:
        st.session_state["report"]    = result["report"]
        st.session_state["report_id"] = result["report_id"]
        st.session_state["page"]      = "dashboard"
        st.rerun()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def page_dashboard():
    nav()

    report    = st.session_state["report"]
    report_id = st.session_state["report_id"]
    summary   = report["summary"]

    # Risk alert
    high_risks = sum(1 for r in report.get("risks", []) if r.get("severity") == "HIGH")
    if high_risks:
        st.markdown(f"""
        <div class="miq-risk-alert">
            ▲ &nbsp;{high_risks} high-severity risk(s) identified — review before proceeding
        </div>
        """, unsafe_allow_html=True)

    # Report header
    st.markdown(f"""
    <div class="miq-report-header miq-animate">
        <div class="miq-report-kicker">{summary.get('meeting_type','Meeting').upper()} &nbsp;·&nbsp; Report Ready</div>
        <div class="miq-report-title">{summary.get('one_line','Meeting Report')}</div>
    </div>
    """, unsafe_allow_html=True)

    stat_row(report)

    # Action row
    col_pdf, col_ppt, col_new = st.columns([1.4, 1.4, 1])
    with col_pdf:
        pdf_bytes = _fetch_bytes(f"/download/pdf/{report_id}")
        if pdf_bytes:
            st.download_button("⬇  Download PDF", pdf_bytes,
                               file_name="MeetingIQ_Report.pdf",
                               mime="application/pdf",
                               use_container_width=True)
    with col_ppt:
        ppt_bytes = _fetch_bytes(f"/download/ppt/{report_id}")
        if ppt_bytes:
            st.download_button("⬇  Download PPT", ppt_bytes,
                               file_name="MeetingIQ_Report.pptx",
                               mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               use_container_width=True)
    with col_new:
        if st.button("↩  New Meeting", type="secondary", use_container_width=True):
            for k in ["report", "report_id"]:
                st.session_state.pop(k, None)
            st.session_state["page"] = "upload"
            st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    tabs = st.tabs([
        "Summary", "Actions", "Financials", "Priorities",
        "Commitments", "Questions", "People", "Dates", "Risks", "Send"
    ])
    with tabs[0]: _tab_summary(report)
    with tabs[1]: _tab_actions(report)
    with tabs[2]: _tab_financials(report)
    with tabs[3]: _tab_priorities(report)
    with tabs[4]: _tab_commitments(report)
    with tabs[5]: _tab_questions(report)
    with tabs[6]: _tab_people(report)
    with tabs[7]: _tab_dates(report)
    with tabs[8]: _tab_risks(report)
    with tabs[9]: _tab_send(report, report_id)


def _fetch_bytes(path: str) -> Optional[bytes]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=30)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


# ── Tabs ──────────────────────────────────────────────────────────────────────

def _tab_summary(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    summary   = report["summary"]
    decisions = summary.get("decisions_made", [])

    if decisions:
        section("◈", "Decisions Made", len(decisions))
        for d in decisions:
            owner = f'<span class="miq-card-person">↳ {d.get("owner")}</span>' if d.get("owner") else ""
            st.markdown(f"""
            <div class="miq-card">
                <div class="miq-card-title">{d.get('decision','')}</div>
                <div class="miq-card-meta">{badge(d.get('status','PENDING'),'status')}{owner}</div>
            </div>
            """, unsafe_allow_html=True)

    next_steps = summary.get("next_steps", [])
    if next_steps:
        section("→", "Next Steps", len(next_steps))
        for i, step in enumerate(next_steps, 1):
            st.markdown(f"""
            <div class="miq-step">
                <div class="miq-step-num">{i:02d}</div>
                <div class="miq-step-text">{step}</div>
            </div>
            """, unsafe_allow_html=True)


def _tab_actions(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("action_items", [])
    if not items:
        empty_state("No action items extracted"); return
    section("✓", "Action Items", len(items))
    for item in items:
        deadline = f'<span class="miq-card-date">due {item.get("deadline")}</span>' if item.get("deadline") else ""
        st.markdown(f"""
        <div class="miq-card">
            <div class="miq-card-title">{item.get('task','')}</div>
            <div class="miq-card-meta">
                {badge(item.get('priority','LOW'))}
                <span class="miq-card-person">{item.get('owner','—')}</span>
                {deadline}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _tab_financials(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("financial_items", [])
    if not items:
        empty_state("No financial items extracted"); return
    section("$", "Financial Items", len(items))
    for item in items:
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        st.markdown(f"""
        <div class="miq-card">
            <div class="miq-amount">{item.get('amount','')}</div>
            <div class="miq-card-title">{item.get('context','')}</div>
            <div class="miq-card-meta">{badge(item.get('status','PENDING'),'status')}{owner}</div>
        </div>
        """, unsafe_allow_html=True)


def _tab_priorities(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("priorities", [])
    if not items:
        empty_state("No priority items extracted"); return
    section("▲", "Priorities", len(items))
    for level in ["HIGH", "MEDIUM", "LOW"]:
        group = [i for i in items if i.get("priority","").upper() == level]
        if not group: continue
        st.markdown(f"<div style='margin:1rem 0 6px'>{badge(level)}</div>", unsafe_allow_html=True)
        for item in group:
            owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
            st.markdown(f"""
            <div class="miq-card">
                <div class="miq-card-title">{item.get('item','')}</div>
                <div class="miq-card-meta">{owner}</div>
            </div>
            """, unsafe_allow_html=True)


def _tab_commitments(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("commitments", [])
    if not items:
        empty_state("No commitments extracted"); return
    section("◉", "Targets & Commitments", len(items))
    for item in items:
        target   = f'<span>Target: {item.get("target")}</span>'   if item.get("target")   else ""
        deadline = f'<span class="miq-card-date">by {item.get("deadline")}</span>' if item.get("deadline") else ""
        st.markdown(f"""
        <div class="miq-card">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                        color:var(--gold);letter-spacing:0.08em;margin-bottom:6px">
                {item.get('person','')}
            </div>
            <div class="miq-card-title">{item.get('committed_to','')}</div>
            <div class="miq-card-meta">{target}{deadline}</div>
        </div>
        """, unsafe_allow_html=True)


def _tab_questions(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("unresolved_questions", [])
    if not items:
        empty_state("No unresolved questions"); return
    section("?", "Unresolved Questions", len(items))
    for item in items:
        raised = f'<span class="miq-card-person">raised by {item.get("raised_by")}</span>' if item.get("raised_by") else ""
        st.markdown(f"""
        <div class="miq-card miq-question">
            <div class="miq-card-title">{item.get('question','')}</div>
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.78rem;
                        color:var(--text3);margin:6px 0;font-weight:300">{item.get('context','')}</div>
            <div class="miq-card-meta">{raised}</div>
        </div>
        """, unsafe_allow_html=True)


def _tab_people(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    people = report.get("people", [])
    if not people:
        empty_state("No people extracted"); return
    section("◎", "People & Roles", len(people))

    chips = ""
    for p in people:
        initials = "".join(w[0].upper() for w in (p.get("name") or "?").split()[:2])
        chips += f"""
        <span class="miq-person-chip">
            <span class="miq-avatar">{initials}</span>
            {p.get('name','?')}
        </span>"""
    st.markdown(f'<div class="miq-people-row">{chips}</div>', unsafe_allow_html=True)

    for p in people:
        role  = f'<span>{p.get("role")}</span>'              if p.get("role")  else ""
        email = f'<span class="miq-card-person">{p.get("email")}</span>' if p.get("email") else ""
        st.markdown(f"""
        <div class="miq-card">
            <div class="miq-card-title">{p.get('name','')}</div>
            <div class="miq-card-meta">{role}{email}</div>
        </div>
        """, unsafe_allow_html=True)


def _tab_dates(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("dates_deadlines", [])
    if not items:
        empty_state("No dates extracted"); return
    section("◷", "Dates & Deadlines", len(items))
    for item in items:
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        st.markdown(f"""
        <div class="miq-card">
            <div class="miq-date-label">{item.get('date','')}</div>
            <div class="miq-card-title">{item.get('event','')}</div>
            <div class="miq-card-meta">{badge(item.get('priority','LOW'))}{owner}</div>
        </div>
        """, unsafe_allow_html=True)


def _tab_risks(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("risks", [])
    if not items:
        empty_state("No risks extracted"); return
    section("▲", "Risks & Blockers", len(items))
    border = {"HIGH": "var(--red)", "MEDIUM": "var(--amber)", "LOW": "var(--green)"}
    sorted_items = sorted(items, key=lambda r: {"HIGH":0,"MEDIUM":1,"LOW":2}.get(r.get("severity","LOW"),3))
    for item in sorted_items:
        col   = border.get(item.get("severity","LOW"), "var(--border2)")
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        mit   = f"""<div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.78rem;
                       color:var(--green);margin-top:8px;font-weight:300">
                       ↳ Mitigation: {item.get('mitigation')}</div>""" if item.get("mitigation") else ""
        st.markdown(f"""
        <div class="miq-card" style="border-left:2px solid {col}">
            <div class="miq-card-title">{item.get('description','')}</div>
            <div class="miq-card-meta" style="margin-top:6px">{badge(item.get('severity','LOW'))}{owner}</div>
            {mit}
        </div>
        """, unsafe_allow_html=True)


def _tab_send(report: dict, report_id: str):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    section("◈", "Send to Attendees")

    ai_emails = [p.get("email") for p in report.get("people", []) if p.get("email")]
    default   = "\n".join(ai_emails)

    email_input = st.text_area(
        "Recipient email addresses (one per line)",
        value=default,
        height=110,
        placeholder="alice@company.com\nbob@company.com",
    )

    subject_default = f"Meeting Report — {report['summary'].get('one_line','')[:60]}"
    subject = st.text_input("Email subject", value=subject_default)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    with c1:
        send_clicked = st.button("◈  Send", type="primary", use_container_width=True)

    if send_clicked:
        emails = [e.strip() for e in email_input.strip().splitlines() if e.strip()]
        if not emails:
            st.warning("Add at least one email address.")
        else:
            with st.spinner("Sending…"):
                result = call_api("/send-email", method="POST",
                                  json={"report_id": report_id, "emails": emails,
                                        "attendees": report.get("people", [])},
                                  timeout=30)
            if result and result.get("status") == "success":
                st.success(f"Report sent to {len(emails)} recipient(s).")
            elif result:
                st.error(f"Send failed: {result.get('message','Unknown error')}")

    # Email preview
    section("◎", "Preview")
    summary = report["summary"]
    actions = report.get("action_items", [])
    decisions = summary.get("decisions_made", [])
    action_lines = "".join(
        f"  [{i.get('priority','?')}]  {i.get('owner','?')} → {i.get('task','')}"
        + (f"  (by {i.get('deadline')})" if i.get("deadline") else "") + "\n"
        for i in actions[:5]
    )
    decision_lines = "".join(
        f"  [{d.get('status','?')}]  {d.get('decision','')}\n"
        for d in decisions[:3]
    )
    st.markdown(f"""
    <div class="miq-email-preview">
<span style="color:var(--gold)">To:</span>      {', '.join(ai_emails[:3]) or 'recipients'}
<span style="color:var(--gold)">Subject:</span> {subject}

─────────────────────────────────────
{summary.get('one_line','')}
Type: {summary.get('meeting_type','')}

Action Items:
{action_lines}
Decisions:
{decision_lines}
─────────────────────────────────────
Full report attached as PDF.
Generated by MeetingIQ
    </div>
    """, unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "upload"

    if st.session_state["page"] == "dashboard" and "report" not in st.session_state:
        st.session_state["page"] = "upload"

    if st.session_state["page"] == "upload":
        page_upload()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()