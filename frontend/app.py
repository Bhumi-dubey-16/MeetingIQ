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

# ── Global CSS + JS animations ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #0c0d10;
    --bg2:       #111318;
    --bg3:       #161820;
    --surface:   #1b1e27;
    --border:    #242830;
    --border2:   #2c3040;
    --gold:      #c9a84c;
    --gold-soft: #e8c97a;
    --gold-dim:  #7a6230;
    --gold-glow: rgba(201,168,76,0.18);
    --cream:     #f0ebe0;
    --text:      #d8d4cc;
    --text2:     #8a8880;
    --text3:     #50504e;
    --green:     #4caf82;
    --red:       #c9504c;
    --amber:     #c9934c;
    --blue:      #4c82c9;
    --ease-silk: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-out:  cubic-bezier(0.0, 0.0, 0.2, 1);
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

/* ── Canvas background ── */
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
    opacity: 0.035;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 256px 256px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }

/* ══════════════════════════════════════════════
   KEYFRAMES
══════════════════════════════════════════════ */

@keyframes fade-up {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes slide-right {
    from { opacity: 0; transform: translateX(-18px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes scale-in {
    from { opacity: 0; transform: scale(0.94); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1);    box-shadow: 0 0 6px var(--green); }
    50%       { opacity: 0.5; transform: scale(0.7); box-shadow: 0 0 14px var(--green); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes gold-breathe {
    0%, 100% { box-shadow: 0 0 0 rgba(201,168,76,0); }
    50%       { box-shadow: 0 0 22px rgba(201,168,76,0.12); }
}
@keyframes progress-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}
@keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}
@keyframes number-pop {
    0%   { transform: scale(1); }
    40%  { transform: scale(1.12); }
    100% { transform: scale(1); }
}
@keyframes border-glow {
    0%, 100% { border-color: var(--border); }
    50%       { border-color: rgba(201,168,76,0.25); }
}

/* ── Staggered card entrance ── */
.miq-card-enter {
    animation: fade-up 0.55s var(--ease-silk) both;
}
.miq-card-enter:nth-child(1)  { animation-delay: 0.04s; }
.miq-card-enter:nth-child(2)  { animation-delay: 0.09s; }
.miq-card-enter:nth-child(3)  { animation-delay: 0.14s; }
.miq-card-enter:nth-child(4)  { animation-delay: 0.19s; }
.miq-card-enter:nth-child(5)  { animation-delay: 0.24s; }
.miq-card-enter:nth-child(6)  { animation-delay: 0.29s; }
.miq-card-enter:nth-child(7)  { animation-delay: 0.34s; }
.miq-card-enter:nth-child(8)  { animation-delay: 0.39s; }
.miq-card-enter:nth-child(9)  { animation-delay: 0.44s; }
.miq-card-enter:nth-child(10) { animation-delay: 0.49s; }

.miq-animate   { animation: fade-up 0.6s var(--ease-silk) both; }
.miq-animate-2 { animation: fade-up 0.6s 0.1s var(--ease-silk) both; }
.miq-animate-3 { animation: fade-up 0.6s 0.22s var(--ease-silk) both; }
.miq-animate-4 { animation: fade-up 0.6s 0.34s var(--ease-silk) both; }

/* ══════════════════════════════════════════════
   NAV
══════════════════════════════════════════════ */
.miq-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.6rem 0 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
    position: relative;
    animation: fade-in 0.7s ease both;
}
.miq-nav::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 0px; height: 1px;
    background: var(--gold);
    animation: nav-line 1.2s 0.3s var(--ease-silk) forwards;
}
@keyframes nav-line {
    from { width: 0; }
    to   { width: 80px; }
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
    border-radius: 5px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; color: var(--bg);
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    animation: scale-in 0.5s var(--ease-silk) both;
    transition: box-shadow 0.3s ease;
}
.miq-logo:hover .miq-logo-mark {
    box-shadow: 0 0 20px rgba(201,168,76,0.4);
}
.miq-nav-right {
    display: flex; align-items: center; gap: 16px;
    animation: slide-right 0.5s 0.2s var(--ease-silk) both;
}
.miq-nav-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    color: var(--gold);
    background: rgba(201,168,76,0.07);
    border: 1px solid rgba(201,168,76,0.18);
    padding: 4px 12px;
    border-radius: 2px;
    transition: background 0.25s, border-color 0.25s;
}
.miq-nav-pill:hover {
    background: rgba(201,168,76,0.13);
    border-color: rgba(201,168,76,0.35);
}
.miq-nav-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse-dot 2.5s ease-in-out infinite;
}

/* ══════════════════════════════════════════════
   HISTORY CARDS
══════════════════════════════════════════════ */
.miq-history-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.2rem;
    transition: border-color 0.25s ease, background 0.25s ease,
                transform 0.2s var(--ease-silk), box-shadow 0.25s ease;
    position: relative;
    overflow: hidden;
    animation: fade-up 0.5s var(--ease-silk) both;
}
.miq-history-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 0;
    background: var(--gold-dim);
    opacity: 0.5;
    transition: width 0.25s var(--ease-silk);
}
.miq-history-card:hover {
    border-color: rgba(201,168,76,0.2);
    background: var(--bg3);
    transform: translateX(3px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.miq-history-card:hover::before { width: 2px; }
.miq-history-summary {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    color: var(--text);
    font-weight: 400;
    flex: 1;
    line-height: 1.5;
}
.miq-history-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: var(--text3);
    letter-spacing: 0.08em;
    white-space: nowrap;
    flex-shrink: 0;
}
.miq-history-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--gold-dim);
    letter-spacing: 0.06em;
    margin-top: 3px;
}
.miq-history-empty {
    padding: 4rem 0;
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text3);
    letter-spacing: 0.1em;
    animation: fade-in 0.4s ease both;
}

/* ══════════════════════════════════════════════
   UPLOAD CARD
══════════════════════════════════════════════ */
.miq-upload-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 2.4rem 2.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.35s ease, box-shadow 0.35s ease;
    animation: gold-breathe 4s 1s ease-in-out infinite;
}
.miq-upload-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold-dim), transparent);
}
.miq-upload-card:hover {
    border-color: rgba(201,168,76,0.22);
    box-shadow: 0 8px 40px rgba(0,0,0,0.3), 0 0 0 1px rgba(201,168,76,0.05);
}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text3) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.4rem !important;
    text-transform: uppercase;
    border-radius: 0 !important;
    transition: color 0.2s ease, border-color 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: rgba(255,255,255,0.02) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }
.stTabs [data-baseweb="tab-panel"]     { padding: 0 !important; }

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase;
    border-radius: 2px !important;
    border: none !important;
    padding: 0.72rem 2rem !important;
    transition: all 0.25s var(--ease-silk) !important;
    position: relative;
    overflow: hidden;
}
.stButton > button[kind="primary"] {
    background: var(--gold) !important;
    color: #0a0b0e !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--gold-soft) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.15), 0 8px 28px rgba(201,168,76,0.2) !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0px) !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.25) !important;
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
    background: rgba(201,168,76,0.04) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    background: transparent !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
    padding: 0.62rem 1.4rem !important;
    transition: all 0.25s var(--ease-silk) !important;
}
.stDownloadButton > button:hover {
    border-color: var(--gold) !important;
    color: var(--gold-soft) !important;
    background: rgba(201,168,76,0.05) !important;
    box-shadow: 0 0 18px rgba(201,168,76,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════ */
.stTextArea textarea, .stTextInput input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.7 !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.07), 0 0 20px rgba(201,168,76,0.04) !important;
}
.stTextInput label, .stTextArea label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.64rem !important;
    letter-spacing: 0.11em !important;
    color: var(--text3) !important;
    text-transform: uppercase !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 2px !important;
    transition: border-color 0.25s, background 0.25s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--gold-dim) !important;
    background: rgba(201,168,76,0.02) !important;
}
[data-testid="stFileUploader"] section { background: transparent !important; }
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text3) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
}

/* ══════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════ */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--gold-dim), var(--gold), var(--gold-soft)) !important;
    background-size: 200% 100% !important;
    border-radius: 0 !important;
    animation: shimmer 1.8s linear infinite, progress-pulse 2s ease-in-out infinite !important;
}
.stProgress > div {
    background: var(--border) !important;
    border-radius: 0 !important;
    height: 2px !important;
}

/* ══════════════════════════════════════════════
   STAT CARDS
══════════════════════════════════════════════ */
.miq-stats {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 2.5rem;
    animation: fade-up 0.6s 0.1s var(--ease-silk) both;
}
.miq-stat {
    background: var(--bg2);
    padding: 1.4rem 1.2rem;
    text-align: center;
    transition: background 0.25s ease, transform 0.2s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
}
.miq-stat::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(201,168,76,0.04), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.miq-stat:hover { background: var(--bg3); }
.miq-stat:hover::after { opacity: 1; }
.miq-stat:hover .miq-stat-num {
    animation: number-pop 0.35s var(--ease-silk);
    color: var(--gold-soft);
}
.miq-stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--gold-soft);
    line-height: 1;
    margin-bottom: 6px;
    transition: color 0.25s ease;
}
.miq-stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    color: var(--text3);
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════
   SECTION HEADING
══════════════════════════════════════════════ */
.miq-section {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 2rem 0 0.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
    animation: fade-in 0.4s var(--ease-silk) both;
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

/* ══════════════════════════════════════════════
   CARDS
══════════════════════════════════════════════ */
.miq-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 6px;
    transition: border-color 0.25s ease, background 0.25s ease,
                transform 0.25s var(--ease-silk), box-shadow 0.25s ease;
    position: relative;
    overflow: hidden;
}
.miq-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 0;
    background: var(--gold-dim);
    opacity: 0.5;
    transition: width 0.25s var(--ease-silk);
}
.miq-card:hover {
    border-color: rgba(201,168,76,0.2);
    background: var(--bg3);
    transform: translateY(-2px) translateX(2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25), 0 0 0 1px rgba(201,168,76,0.06);
}
.miq-card:hover::before { width: 2px; }
.miq-card-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    color: var(--text);
    line-height: 1.55;
    margin-bottom: 8px;
}
.miq-card-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
}
.miq-card-person { color: var(--gold-soft); font-size: 0.68rem; }
.miq-card-date   { color: var(--text2); }

/* ══════════════════════════════════════════════
   BADGES
══════════════════════════════════════════════ */
.miq-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem;
    letter-spacing: 0.1em;
    padding: 2px 7px;
    border-radius: 1px;
    text-transform: uppercase;
    font-weight: 500;
    transition: opacity 0.2s;
}
.miq-badge-high     { background: rgba(201,80,76,0.1);   color: #e07070; border: 1px solid rgba(201,80,76,0.22); }
.miq-badge-medium   { background: rgba(201,147,76,0.1);  color: #dda060; border: 1px solid rgba(201,147,76,0.22); }
.miq-badge-low      { background: rgba(76,175,130,0.1);  color: #6dcca0; border: 1px solid rgba(76,175,130,0.22); }
.miq-badge-decided  { background: rgba(76,175,130,0.1);  color: #6dcca0; border: 1px solid rgba(76,175,130,0.22); }
.miq-badge-deferred { background: rgba(201,147,76,0.1);  color: #dda060; border: 1px solid rgba(201,147,76,0.22); }
.miq-badge-pending  { background: rgba(201,80,76,0.1);   color: #e07070; border: 1px solid rgba(201,80,76,0.22); }

/* ══════════════════════════════════════════════
   REPORT HEADER
══════════════════════════════════════════════ */
.miq-report-header {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    animation: scale-in 0.5s var(--ease-silk) both;
}
.miq-report-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--gold), rgba(201,168,76,0.3) 50%, transparent);
}
.miq-report-header::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at top left, rgba(201,168,76,0.04) 0%, transparent 60%);
    pointer-events: none;
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

/* ══════════════════════════════════════════════
   RISK ALERT
══════════════════════════════════════════════ */
.miq-risk-alert {
    background: rgba(201,80,76,0.05);
    border: 1px solid rgba(201,80,76,0.18);
    border-left: 2px solid var(--red);
    border-radius: 2px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #e07070;
    letter-spacing: 0.04em;
    animation: fade-up 0.4s var(--ease-silk) both;
}

/* ══════════════════════════════════════════════
   STEP LIST
══════════════════════════════════════════════ */
.miq-step {
    display: flex;
    gap: 14px;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--border);
    align-items: flex-start;
    transition: background 0.2s ease;
    border-radius: 2px;
}
.miq-step:last-child { border-bottom: none; }
.miq-step:hover { background: rgba(255,255,255,0.01); }
.miq-step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--gold);
    background: rgba(201,168,76,0.07);
    border: 1px solid rgba(201,168,76,0.14);
    width: 20px; height: 20px;
    border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
    transition: background 0.2s, border-color 0.2s;
}
.miq-step:hover .miq-step-num {
    background: rgba(201,168,76,0.13);
    border-color: rgba(201,168,76,0.28);
}
.miq-step-text {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.55;
    font-weight: 300;
}

/* ══════════════════════════════════════════════
   PERSON CHIPS
══════════════════════════════════════════════ */
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
    transition: border-color 0.2s, transform 0.2s var(--ease-silk), box-shadow 0.2s;
    animation: scale-in 0.4s var(--ease-silk) both;
}
.miq-person-chip:hover {
    border-color: rgba(201,168,76,0.25);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
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

/* ══════════════════════════════════════════════
   FINANCIAL / DATE / QUESTION
══════════════════════════════════════════════ */
.miq-amount {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--gold-soft);
    letter-spacing: -0.01em;
    margin-bottom: 4px;
    transition: color 0.2s;
}
.miq-card:hover .miq-amount { color: var(--cream); }

.miq-question {
    border-left: 2px solid var(--gold-dim);
    padding-left: 1rem;
    transition: border-color 0.2s;
}
.miq-question:hover { border-left-color: var(--gold); }

.miq-date-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}

/* ══════════════════════════════════════════════
   EMAIL PREVIEW
══════════════════════════════════════════════ */
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
    transition: border-color 0.25s;
}
.miq-email-preview:hover { border-color: var(--border2); }

/* ══════════════════════════════════════════════
   HOW IT WORKS
══════════════════════════════════════════════ */
.miq-how {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 2px;
    overflow: hidden;
    margin-top: 3.5rem;
}
.miq-how-item {
    background: var(--bg2);
    padding: 1.8rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: background 0.3s ease;
}
.miq-how-item::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(201,168,76,0.04), transparent);
    opacity: 0;
    transition: opacity 0.35s ease;
}
.miq-how-item:hover { background: var(--bg3); }
.miq-how-item:hover::after { opacity: 1; }
.miq-how-num {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--border2);
    line-height: 1;
    margin-bottom: 0.8rem;
    transition: color 0.3s ease;
}
.miq-how-item:hover .miq-how-num { color: rgba(201,168,76,0.2); }
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
    line-height: 1.65;
    font-weight: 300;
}

/* ══════════════════════════════════════════════
   ANALYSIS OVERLAY
══════════════════════════════════════════════ */
.miq-analysis-status {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--gold);
    letter-spacing: 0.1em;
    text-align: center;
    padding: 8px 0;
    animation: fade-in 0.3s ease both;
}
.miq-analysis-tool {
    display: inline-block;
    animation: fade-up 0.3s var(--ease-silk) both;
}

/* ── Alert overrides ── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* ── Divider ── */
.miq-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.8rem 0;
}

</style>

<!-- Animated canvas background + scanline -->
<canvas id="bg-canvas"></canvas>
<div id="bg-scanline" style="
    position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;
"></div>

<script>
(function() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const PARTICLE_COUNT = 65;
    const particles = Array.from({length: PARTICLE_COUNT}, () => ({
        x:  Math.random() * window.innerWidth,
        y:  Math.random() * window.innerHeight,
        r:  Math.random() * 1.3 + 0.15,
        vx: (Math.random() - 0.5) * 0.16,
        vy: (Math.random() - 0.5) * 0.10,
        o:  Math.random() * 0.35 + 0.04,
        pulse: Math.random() * Math.PI * 2,
    }));

    let t = 0;
    function draw() {
        t += 0.0035;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const g1 = ctx.createRadialGradient(
            canvas.width * 0.12 + Math.sin(t * 0.6) * 70,
            canvas.height * 0.18 + Math.cos(t * 0.45) * 45,
            0,
            canvas.width * 0.12, canvas.height * 0.18, canvas.width * 0.42
        );
        g1.addColorStop(0, 'rgba(185,135,45,0.065)');
        g1.addColorStop(0.6, 'rgba(185,135,45,0.018)');
        g1.addColorStop(1, 'rgba(185,135,45,0)');
        ctx.fillStyle = g1;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const g2 = ctx.createRadialGradient(
            canvas.width * 0.84 + Math.sin(t * 0.38 + 1.4) * 55,
            canvas.height * 0.78 + Math.cos(t * 0.55 + 2.1) * 40,
            0,
            canvas.width * 0.84, canvas.height * 0.78, canvas.width * 0.46
        );
        g2.addColorStop(0, 'rgba(55,75,145,0.05)');
        g2.addColorStop(0.6, 'rgba(55,75,145,0.014)');
        g2.addColorStop(1, 'rgba(55,75,145,0)');
        ctx.fillStyle = g2;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const breathe = 0.5 + Math.sin(t * 0.8) * 0.5;
        const g3 = ctx.createRadialGradient(
            canvas.width * 0.5 + Math.sin(t * 0.28) * 35,
            canvas.height * 0.46 + Math.cos(t * 0.36) * 25,
            0,
            canvas.width * 0.5, canvas.height * 0.46, canvas.width * 0.3
        );
        g3.addColorStop(0, `rgba(145,115,52,${0.022 * breathe})`);
        g3.addColorStop(1, 'rgba(145,115,52,0)');
        ctx.fillStyle = g3;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            p.pulse += 0.012;
            const opa = p.o * (0.7 + 0.3 * Math.sin(p.pulse));
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(201,168,76,${opa})`;
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

    const scanContainer = document.getElementById('bg-scanline');
    if (scanContainer) {
        const line = document.createElement('div');
        line.style.cssText = `
            position:absolute;left:0;right:0;
            height:1px;
            background:linear-gradient(90deg,transparent,rgba(201,168,76,0.06),transparent);
            top:-1px;
        `;
        scanContainer.appendChild(line);
        let scanY = -2;
        function animateScan() {
            scanY += 0.4;
            if (scanY > window.innerHeight + 2) scanY = -2;
            line.style.top = scanY + 'px';
            requestAnimationFrame(animateScan);
        }
        animateScan();
    }

    function animateCounters() {
        const nums = document.querySelectorAll('.miq-stat-num[data-target]');
        nums.forEach(el => {
            if (el.dataset.animated) return;
            el.dataset.animated = '1';
            const target = parseInt(el.dataset.target, 10);
            const duration = 900;
            const start = performance.now();
            function step(now) {
                const p = Math.min((now - start) / duration, 1);
                const ease = 1 - Math.pow(1 - p, 3);
                el.textContent = Math.round(ease * target);
                if (p < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        });
    }
    const counterInterval = setInterval(() => {
        const els = document.querySelectorAll('.miq-stat-num[data-target]');
        if (els.length > 0) { animateCounters(); clearInterval(counterInterval); }
    }, 200);

})();
</script>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def nav(show_history_btn: bool = True):
    """
    Renders the top nav bar.
    show_history_btn=True  → shows the History button (upload + dashboard pages)
    """
    st.markdown("""
    <div class="miq-nav">
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

 
    if show_history_btn:
        col_spacer, col_btn = st.columns([6, 1])
        with col_btn:
            if st.button("◷  History", key="nav_history_btn", type="secondary"):
                st.session_state["page"] = "history"
                st.rerun()


def badge(value: str, kind: str = "priority") -> str:
    v = (value or "").upper()
    if kind == "priority":
        cls = {"HIGH": "miq-badge-high", "MEDIUM": "miq-badge-medium",
               "LOW": "miq-badge-low"}.get(v, "miq-badge-low")
    else:
        cls = {"DECIDED": "miq-badge-decided", "DEFERRED": "miq-badge-deferred",
               "PENDING": "miq-badge-pending"}.get(v, "miq-badge-pending")
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
        <div class="miq-stat">
            <div class="miq-stat-num">{n_a}</div>
            <div class="miq-stat-label">Actions</div>
        </div>
        <div class="miq-stat">
            <div class="miq-stat-num">{n_r}</div>
            <div class="miq-stat-label">Risks</div>
        </div>
        <div class="miq-stat">
            <div class="miq-stat-num">{n_f}</div>
            <div class="miq-stat-label">Financials</div>
        </div>
        <div class="miq-stat">
            <div class="miq-stat-num">{n_p}</div>
            <div class="miq-stat-label">People</div>
        </div>
        <div class="miq-stat">
            <div class="miq-stat-num">{n_q}</div>
            <div class="miq-stat-label">Questions</div>
        </div>
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
                color:var(--text3);letter-spacing:0.06em;
                animation:fade-in 0.4s ease both">— {msg} —</div>
    """, unsafe_allow_html=True)


# ── History page ──────────────────────────────────────────────────────────────

def page_history():
    nav(show_history_btn=False)

    # ── Page header ───────────────────────────────────────────────────────────
    col_title, col_new = st.columns([5, 1])
    with col_title:
        st.markdown("""
        <div style="padding: 1rem 0 0.4rem">
            <div class="miq-hero-kicker" style="
                font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                letter-spacing:0.22em;color:var(--gold);text-transform:uppercase;
                margin-bottom:0.7rem">Past Meetings</div>
            <div style="
                font-family:'Playfair Display',serif;font-size:2rem;
                font-weight:700;color:var(--cream);letter-spacing:-0.02em;
                line-height:1.15">Meeting Archive</div>
        </div>
        """, unsafe_allow_html=True)
    with col_new:
        st.markdown("<div style='height:2.4rem'></div>", unsafe_allow_html=True)
        if st.button("◈  New", key="history_new_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "upload"
            st.rerun()

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── Fetch from /reports ───────────────────────────────────────────────────
    data = call_api("/reports?limit=50", method="GET", timeout=10)

    if data is None:
        return  # call_api already showed the error

    if not data:
        st.markdown("""
        <div class="miq-history-empty">
            — No meetings analysed yet —<br>
            <span style="color:var(--gold-dim);font-size:0.6rem">
                Upload your first transcript to get started
            </span>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Render one button per report ─────────────────────────────────────────
    # We can't put buttons inside HTML blocks, so we interleave:
    # HTML card (summary + meta) on the left, Streamlit button on the right.
    for i, row in enumerate(data):
        report_id  = row.get("report_id", "")
        created_at = row.get("created_at", "")
        summary    = row.get("summary", "No summary available")
        short_id   = report_id[:8] if report_id else "——"

        col_info, col_btn = st.columns([5, 1])

        with col_info:
            st.markdown(f"""
            <div class="miq-history-card" style="animation-delay:{i * 0.05}s">
                <div>
                    <div class="miq-history-summary">{summary}</div>
                    <div class="miq-history-id">id: {short_id}…</div>
                </div>
                <div class="miq-history-meta">{created_at}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            # Vertical alignment tweak so button sits in the middle of the card
            st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
            if st.button("Open →", key=f"open_report_{report_id}", type="secondary"):
                _load_report_by_id(report_id)


def _load_report_by_id(report_id: str):
    """
    Fetches full report from /report/{id}, stuffs it into session state,
    and navigates to the dashboard. Called when user clicks Open in history.
    """
    with st.spinner("Loading report…"):
        data = call_api(f"/report/{report_id}", method="GET", timeout=15)

    if data is None:
        return  # error already shown by call_api

    st.session_state["report"]    = data["report"]
    st.session_state["report_id"] = data["report_id"]
    st.session_state["page"]      = "dashboard"
    st.rerun()


# ── Upload page ───────────────────────────────────────────────────────────────

def page_upload():
    nav()

    st.markdown("""
    <div style="padding:3.5rem 0 3rem">
        <div class="miq-hero-kicker" style="
            font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
            letter-spacing:0.22em;color:var(--gold);text-transform:uppercase;
            margin-bottom:1.2rem;display:flex;align-items:center;gap:12px">
            AI Meeting Intelligence
        </div>
        <div style="
            font-family:'Playfair Display',serif;
            font-size:clamp(2.4rem,4.5vw,3.8rem);font-weight:700;
            color:var(--cream);line-height:1.1;letter-spacing:-0.02em;margin-bottom:1.4rem">
            Every meeting,<br><em style="font-style:italic;color:#e8c97a">perfectly distilled.</em>
        </div>
        <div style="
            font-family:'IBM Plex Sans',sans-serif;font-size:0.95rem;
            color:var(--text2);line-height:1.75;max-width:420px;font-weight:300">
            Upload a recording or paste a transcript — the AI extracts every decision,
            action, risk, and commitment in seconds.
        </div>
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
            <div class="miq-how-body">Nine AI tools run concurrently, extracting actions, decisions, financials, risks, and more.</div>
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
        <div class="miq-analysis-status">
            <span style="color:var(--text3)">{i+1} / {len(tools)}</span>
            &nbsp;·&nbsp;
            <span class="miq-analysis-tool">{tool}</span>
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

        time.sleep(0.18)

    pb.progress(1.0)
    time.sleep(0.35)
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

    high_risks = sum(1 for r in report.get("risks", []) if r.get("severity") == "HIGH")
    if high_risks:
        st.markdown(f"""
        <div class="miq-risk-alert">
            ▲ &nbsp;{high_risks} high-severity risk(s) identified — review before proceeding
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="miq-report-header">
        <div class="miq-report-kicker">{summary.get('meeting_type','Meeting').upper()} &nbsp;·&nbsp; Report Ready</div>
        <div class="miq-report-title">{summary.get('one_line','Meeting Report')}</div>
    </div>
    """, unsafe_allow_html=True)

    stat_row(report)

    col_pdf, col_ppt, col_hist, col_new = st.columns([1.4, 1.4, 1, 1])
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
    with col_hist:
        if st.button("◷  All Reports", type="secondary", use_container_width=True):
            st.session_state["page"] = "history"
            st.rerun()
    with col_new:
        if st.button("↩  New Meeting", type="secondary", use_container_width=True):
            # Clear current report from session — history still accessible via DB
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


# ── Tab renderers ─────────────────────────────────────────────────────────────

def _tab_summary(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    summary   = report["summary"]
    decisions = summary.get("decisions_made", [])

    if decisions:
        section("◈", "Decisions Made", len(decisions))
        cards_html = ""
        for d in decisions:
            owner = f'<span class="miq-card-person">↳ {d.get("owner")}</span>' if d.get("owner") else ""
            cards_html += f"""
            <div class="miq-card miq-card-enter">
                <div class="miq-card-title">{d.get('decision','')}</div>
                <div class="miq-card-meta">{badge(d.get('status','PENDING'),'status')}{owner}</div>
            </div>"""
        st.markdown(cards_html, unsafe_allow_html=True)

    next_steps = summary.get("next_steps", [])
    if next_steps:
        section("→", "Next Steps", len(next_steps))
        steps_html = ""
        for i, step in enumerate(next_steps, 1):
            steps_html += f"""
            <div class="miq-step miq-card-enter">
                <div class="miq-step-num">{i:02d}</div>
                <div class="miq-step-text">{step}</div>
            </div>"""
        st.markdown(steps_html, unsafe_allow_html=True)


def _tab_actions(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("action_items", [])
    if not items:
        empty_state("No action items extracted"); return
    section("✓", "Action Items", len(items))
    cards_html = ""
    for item in items:
        deadline = f'<span class="miq-card-date">due {item.get("deadline")}</span>' if item.get("deadline") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter">
            <div class="miq-card-title">{item.get('task','')}</div>
            <div class="miq-card-meta">
                {badge(item.get('priority','LOW'))}
                <span class="miq-card-person">{item.get('owner','—')}</span>
                {deadline}
            </div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


def _tab_financials(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("financial_items", [])
    if not items:
        empty_state("No financial items extracted"); return
    section("$", "Financial Items", len(items))
    cards_html = ""
    for item in items:
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter">
            <div class="miq-amount">{item.get('amount','')}</div>
            <div class="miq-card-title">{item.get('context','')}</div>
            <div class="miq-card-meta">{badge(item.get('status','PENDING'),'status')}{owner}</div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


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
        cards_html = ""
        for item in group:
            owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
            cards_html += f"""
            <div class="miq-card miq-card-enter">
                <div class="miq-card-title">{item.get('item','')}</div>
                <div class="miq-card-meta">{owner}</div>
            </div>"""
        st.markdown(cards_html, unsafe_allow_html=True)


def _tab_commitments(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("commitments", [])
    if not items:
        empty_state("No commitments extracted"); return
    section("◉", "Targets & Commitments", len(items))
    cards_html = ""
    for item in items:
        target   = f'<span>Target: {item.get("target")}</span>'   if item.get("target")   else ""
        deadline = f'<span class="miq-card-date">by {item.get("deadline")}</span>' if item.get("deadline") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                        color:var(--gold);letter-spacing:0.08em;margin-bottom:6px">
                {item.get('person','')}
            </div>
            <div class="miq-card-title">{item.get('committed_to','')}</div>
            <div class="miq-card-meta">{target}{deadline}</div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


def _tab_questions(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("unresolved_questions", [])
    if not items:
        empty_state("No unresolved questions"); return
    section("?", "Unresolved Questions", len(items))
    cards_html = ""
    for item in items:
        raised = f'<span class="miq-card-person">raised by {item.get("raised_by")}</span>' if item.get("raised_by") else ""
        cards_html += f"""
        <div class="miq-card miq-question miq-card-enter">
            <div class="miq-card-title">{item.get('question','')}</div>
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.78rem;
                        color:var(--text3);margin:6px 0;font-weight:300">{item.get('context','')}</div>
            <div class="miq-card-meta">{raised}</div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


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

    cards_html = ""
    for p in people:
        role  = f'<span>{p.get("role")}</span>'              if p.get("role")  else ""
        email = f'<span class="miq-card-person">{p.get("email")}</span>' if p.get("email") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter">
            <div class="miq-card-title">{p.get('name','')}</div>
            <div class="miq-card-meta">{role}{email}</div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


def _tab_dates(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("dates_deadlines", [])
    if not items:
        empty_state("No dates extracted"); return
    section("◷", "Dates & Deadlines", len(items))
    cards_html = ""
    for item in items:
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter">
            <div class="miq-date-label">{item.get('date','')}</div>
            <div class="miq-card-title">{item.get('event','')}</div>
            <div class="miq-card-meta">{badge(item.get('priority','LOW'))}{owner}</div>
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


def _tab_risks(report: dict):
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    items = report.get("risks", [])
    if not items:
        empty_state("No risks extracted"); return
    section("▲", "Risks & Blockers", len(items))
    border_col = {"HIGH": "var(--red)", "MEDIUM": "var(--amber)", "LOW": "var(--green)"}
    sorted_items = sorted(items, key=lambda r: {"HIGH":0,"MEDIUM":1,"LOW":2}.get(r.get("severity","LOW"),3))
    cards_html = ""
    for item in sorted_items:
        col   = border_col.get(item.get("severity","LOW"), "var(--border2)")
        owner = f'<span class="miq-card-person">{item.get("owner")}</span>' if item.get("owner") else ""
        mit   = f"""<div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.78rem;
                       color:var(--green);margin-top:8px;font-weight:300">
                       ↳ {item.get('mitigation')}</div>""" if item.get("mitigation") else ""
        cards_html += f"""
        <div class="miq-card miq-card-enter" style="border-left:2px solid {col}">
            <div class="miq-card-title">{item.get('description','')}</div>
            <div class="miq-card-meta" style="margin-top:6px">{badge(item.get('severity','LOW'))}{owner}</div>
            {mit}
        </div>"""
    st.markdown(cards_html, unsafe_allow_html=True)


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
                st.success(f"✓ Report sent to {len(emails)} recipient(s) — PDF + PPT attached.")
            elif result:
                st.error(f"Send failed: {result.get('message','Unknown error')}")

    section("◎", "Email Preview")
    summary   = report["summary"]
    actions   = report.get("action_items", [])
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
Full report attached as PDF + PPT.
Generated by MeetingIQ
    </div>
    """, unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "upload"

    # Guard: if dashboard requested but no report in session, go to history
    # (user may have refreshed the page — report_id is gone but DB has it)
    if st.session_state["page"] == "dashboard" and "report" not in st.session_state:
        st.session_state["page"] = "history"

    page = st.session_state["page"]

    if page == "upload":
        page_upload()
    elif page == "history":
        page_history()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()