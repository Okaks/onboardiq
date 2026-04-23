from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import text
from database import SessionLocal
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------- Dashboard ----------

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>OnboardIQ — Funnel Analytics</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.2.0/chartjs-plugin-datalabels.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0d0f14;
  --bg2: #13151c;
  --bg3: #1a1d27;
  --surface: #1e2130;
  --surface2: #252840;
  --border: rgba(255,255,255,0.06);
  --border-md: rgba(255,255,255,0.1);
  --text: #e8eaf0;
  --text-muted: #8b90a8;
  --text-hint: #555a72;
  --accent: #6c63ff;
  --accent-light: rgba(108,99,255,0.15);
  --accent-glow: rgba(108,99,255,0.4);
  --green: #4ade80;
  --green-bg: rgba(74,222,128,0.1);
  --red: #f87171;
  --red-bg: rgba(248,113,113,0.1);
  --amber: #fbbf24;
  --amber-bg: rgba(251,191,36,0.1);
  --blue: #60a5fa;
  --blue-bg: rgba(96,165,250,0.1);
  --teal: #2dd4bf;
  --teal-bg: rgba(45,212,191,0.1);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --font: 'Syne', sans-serif;
  --mono: 'DM Mono', monospace;
}
body { font-family: var(--font); background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.6; min-height: 100vh; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 4px; }

/* LAYOUT */
.shell { display: flex; min-height: 100vh; }

/* SIDEBAR */
.sidebar {
  width: 230px; flex-shrink: 0;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  padding: 1.5rem 1rem;
  display: flex; flex-direction: column; gap: 2rem;
  position: sticky; top: 0; height: 100vh; overflow-y: auto;
}
.brand { display: flex; align-items: center; gap: 10px; padding: 0 4px; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: var(--accent);
  box-shadow: 0 0 20px var(--accent-glow);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.brand-icon svg { width: 18px; height: 18px; fill: #fff; }
.brand-name { font-size: 16px; font-weight: 800; letter-spacing: -0.01em; color: var(--text); }
.brand-sub { font-size: 10px; color: var(--text-hint); letter-spacing: 0.08em; text-transform: uppercase; }

.nav-section { display: flex; flex-direction: column; gap: 2px; }
.nav-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; color: var(--text-hint); text-transform: uppercase; margin-bottom: 6px; padding: 0 8px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-muted); cursor: pointer;
  transition: all 0.15s; text-decoration: none; font-weight: 500;
  border: 1px solid transparent;
}
.nav-item:hover { background: var(--surface); color: var(--text); }
.nav-item.active {
  background: var(--accent-light); color: var(--accent);
  border-color: rgba(108,99,255,0.2);
}
.nav-item svg { width: 15px; height: 15px; flex-shrink: 0; }

.sidebar-filters { display: flex; flex-direction: column; gap: 10px; margin-top: auto; }
.filter-label { font-size: 10px; font-weight: 700; letter-spacing: 0.08em; color: var(--text-hint); text-transform: uppercase; margin-bottom: 4px; }
.filter-select, .filter-date {
  width: 100%; font-family: var(--font); font-size: 12px;
  padding: 7px 10px; border-radius: var(--radius-sm);
  border: 1px solid var(--border-md); background: var(--surface);
  color: var(--text); outline: none;
  transition: border-color 0.15s;
}
.filter-select:focus, .filter-date:focus { border-color: var(--accent); }
.filter-select { appearance: none; cursor: pointer; }
.custom-dates { display: none; flex-direction: column; gap: 6px; }
.apply-btn {
  width: 100%; padding: 9px; border-radius: var(--radius-sm);
  background: var(--accent); color: #fff; border: none;
  font-family: var(--font); font-size: 13px; font-weight: 700;
  cursor: pointer; letter-spacing: 0.02em;
  transition: all 0.15s;
  box-shadow: 0 0 20px var(--accent-glow);
}
.apply-btn:hover { background: #5751e8; box-shadow: 0 0 30px var(--accent-glow); }

/* MAIN */
.main { flex: 1; padding: 2rem 2.5rem; overflow-y: auto; min-width: 0; }

/* PAGE HEADER */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: flex-start; justify-content: space-between;
}
.page-header h1 { font-size: 26px; font-weight: 800; letter-spacing: -0.02em; color: var(--text); }
.page-header p { font-size: 12px; color: var(--text-muted); margin-top: 3px; font-family: var(--mono); }
.header-badge {
  display: flex; align-items: center; gap: 6px;
  background: var(--surface); border: 1px solid var(--border-md);
  padding: 6px 12px; border-radius: 20px;
  font-size: 11px; color: var(--text-muted); font-family: var(--mono);
}
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }

/* STATES */
.state-box {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 6rem 2rem; gap: 16px; color: var(--text-muted);
}
.spinner {
  width: 32px; height: 32px;
  border: 2px solid var(--border-md);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* SECTION LABELS */
.section-label {
  font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
  color: var(--text-hint); text-transform: uppercase;
  margin-bottom: 12px; margin-top: 2rem;
  scroll-margin-top: 1rem;
  display: flex; align-items: center; gap: 10px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }
.section-label:first-child { margin-top: 0; }

/* METRICS */
.metrics-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 1.5rem; }
.metric {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  position: relative; overflow: hidden;
  transition: border-color 0.2s;
}
.metric:hover { border-color: var(--border-md); }
.metric::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--accent), transparent);
  opacity: 0.6;
}
.metric .m-label { font-size: 11px; color: var(--text-hint); margin-bottom: 8px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }
.metric .m-value { font-size: 28px; font-weight: 800; line-height: 1; letter-spacing: -0.02em; }
.metric .m-sub { font-size: 11px; margin-top: 6px; font-family: var(--mono); }
.up { color: var(--green); } .down { color: var(--red); } .neutral { color: var(--text-muted); }

/* ALERT */
.alert {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; border-radius: var(--radius-md);
  background: var(--amber-bg); border: 1px solid rgba(251,191,36,0.2);
  font-size: 13px; color: var(--amber); margin-bottom: 1.5rem;
}
.alert svg { flex-shrink: 0; width: 16px; height: 16px; }

/* CARDS */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  transition: border-color 0.2s;
}
.card:hover { border-color: var(--border-md); }
.card-title { font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }

/* FUNNEL VIZ */
.funnel-visual { display: flex; flex-direction: column; gap: 6px; }
.drop-row { display: flex; justify-content: flex-end; margin-bottom: 2px; }
.drop-pill {
  font-size: 10px; color: var(--red); background: var(--red-bg);
  padding: 2px 8px; border-radius: 20px;
  border: 1px solid rgba(248,113,113,0.2);
  font-family: var(--mono);
}
.funnel-bar-row { display: flex; align-items: center; gap: 10px; }
.funnel-step-label { font-size: 11px; min-width: 130px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-muted); font-weight: 500; }
.funnel-bar-track { flex: 1; height: 28px; background: var(--bg3); border-radius: 6px; overflow: hidden; }
.funnel-bar-fill { height: 100%; border-radius: 6px; display: flex; align-items: center; padding-left: 10px; transition: width 0.6s cubic-bezier(0.4,0,0.2,1); }
.funnel-bar-fill span { font-size: 11px; font-weight: 700; color: #fff; white-space: nowrap; font-family: var(--mono); }
.funnel-pct { font-size: 11px; color: var(--text-hint); min-width: 38px; text-align: right; font-family: var(--mono); }

/* TABLE */
.tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
.tbl th {
  font-size: 10px; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--text-hint);
  padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: left;
}
.tbl td { padding: 10px 12px; border-bottom: 1px solid var(--border); color: var(--text); }
.tbl tr:last-child td { border-bottom: none; }
.tbl .num { text-align: right; font-family: var(--mono); }
.tbl tr.clickable { cursor: pointer; }
.tbl tr.clickable:hover td { background: var(--bg3); }

/* BADGES */
.badge { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 20px; letter-spacing: 0.04em; }
.badge-red { background: var(--red-bg); color: var(--red); border: 1px solid rgba(248,113,113,0.2); }
.badge-amber { background: var(--amber-bg); color: var(--amber); border: 1px solid rgba(251,191,36,0.2); }
.badge-green { background: var(--green-bg); color: var(--green); border: 1px solid rgba(74,222,128,0.2); }
.badge-blue { background: var(--blue-bg); color: var(--blue); border: 1px solid rgba(96,165,250,0.2); }
.badge-teal { background: var(--teal-bg); color: var(--teal); border: 1px solid rgba(45,212,191,0.2); }
.badge-accent { background: var(--accent-light); color: var(--accent); border: 1px solid rgba(108,99,255,0.2); }

/* CHANNEL CARDS */
.channel-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 1rem; }
.channel-card {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 16px 18px;
  transition: border-color 0.2s;
}
.channel-card:hover { border-color: var(--border-md); }
.channel-card .ch-name { font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-hint); margin-bottom: 8px; }
.channel-card .ch-conv { font-size: 26px; font-weight: 800; letter-spacing: -0.02em; }
.channel-card .ch-sub { font-size: 10px; color: var(--text-muted); margin-top: 4px; font-family: var(--mono); }
.ch-bar { height: 3px; border-radius: 2px; background: var(--border); margin-top: 10px; overflow: hidden; }
.ch-bar-fill { height: 100%; border-radius: 2px; }

/* FILTER PILLS */
.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
.filter-pill {
  font-size: 11px; font-weight: 600; padding: 5px 14px; border-radius: 20px;
  cursor: pointer; border: 1px solid var(--border-md);
  background: var(--surface); color: var(--text-muted);
  transition: all 0.15s;
}
.filter-pill:hover { background: var(--surface2); color: var(--text); }
.filter-pill.active { background: var(--accent-light); color: var(--accent); border-color: rgba(108,99,255,0.3); }

/* DRAWER */
.drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; display: none; backdrop-filter: blur(4px); }
.drawer-overlay.open { display: block; }
.drawer {
  position: fixed; right: 0; top: 0; bottom: 0; width: 420px;
  background: var(--bg2); border-left: 1px solid var(--border);
  z-index: 101; transform: translateX(100%);
  transition: transform 0.25s cubic-bezier(0.4,0,0.2,1);
  overflow-y: auto; padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.drawer.open { transform: translateX(0); }
.drawer-header { display: flex; align-items: center; justify-content: space-between; }
.drawer-title { font-size: 15px; font-weight: 800; letter-spacing: -0.01em; font-family: var(--mono); color: var(--accent); }
.drawer-close { background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 20px; line-height: 1; padding: 4px; transition: color 0.15s; }
.drawer-close:hover { color: var(--text); }
.user-stat-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.user-stat { background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 12px 14px; }
.user-stat .us-label { font-size: 10px; color: var(--text-hint); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.user-stat .us-value { font-size: 18px; font-weight: 800; margin-top: 4px; letter-spacing: -0.01em; }

/* INSIGHTS */
.insight {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 14px 16px; border-radius: var(--radius-md);
  border: 1px solid var(--border); margin-bottom: 8px;
  background: var(--bg3);
  transition: border-color 0.2s;
}
.insight:hover { border-color: var(--border-md); }
.insight-icon {
  width: 32px; height: 32px; border-radius: var(--radius-sm);
  flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.i-warn { background: var(--amber-bg); }
.i-info { background: var(--blue-bg); }
.i-ok { background: var(--green-bg); }
.insight-body .i-title { font-size: 13px; font-weight: 700; margin-bottom: 3px; }
.insight-body .i-desc { font-size: 12px; color: var(--text-muted); line-height: 1.6; }
.recs { list-style: none; }
.recs li { display: flex; gap: 14px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.recs li:last-child { border-bottom: none; }
.rec-n { font-size: 10px; font-weight: 700; color: var(--accent); min-width: 20px; padding-top: 2px; font-family: var(--mono); }
.chart-box { position: relative; width: 100%; }
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
.date-range-label { font-size: 11px; color: var(--text-hint); font-family: var(--mono); }

/* SLOW HIGHLIGHT */
.slow-highlight {
  margin-top: 12px; padding: 12px 14px;
  background: var(--amber-bg); border: 1px solid rgba(251,191,36,0.2);
  border-radius: var(--radius-sm); font-size: 12px; color: var(--amber);
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .sidebar { display: none; }
  .metrics-row { grid-template-columns: 1fr 1fr; }
  .two-col, .three-col { grid-template-columns: 1fr; }
  .drawer { width: 100%; }
  .main { padding: 1.5rem; }
}
</style>
</head>
<body>
<div class="shell">
  <!-- SIDEBAR -->
  <nav class="sidebar">
    <div class="brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24"><path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3zm13 2a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"/></svg>
      </div>
      <div>
        <div class="brand-name">OnboardIQ</div>
        <div class="brand-sub">Funnel Analytics</div>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-label">Views</div>
      <a class="nav-item active" href="#" onclick="scrollToSection('sec-summary', this); return false;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><circle cx="17.5" cy="17.5" r="3.5"/></svg>
        Dashboard
      </a>
      <a class="nav-item" href="#" onclick="scrollToSection('sec-steps', this); return false;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        Step Analysis
      </a>
      <a class="nav-item" href="#" onclick="scrollToSection('sec-time', this); return false;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        Time Analysis
      </a>
      <a class="nav-item" href="#" onclick="scrollToSection('sec-channels', this); return false;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        Channels
      </a>
      <a class="nav-item" href="#" onclick="scrollToSection('sec-users', this); return false;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        Users
      </a>
    </div>

    <div class="sidebar-filters">
      <div>
        <div class="filter-label">Active funnel</div>
        <select class="filter-select" id="funnelSelect" onchange="onFunnelChange(this.value)">
          <option value="">Loading...</option>
        </select>
      </div>
      <div>
        <div class="filter-label">Date range</div>
        <select class="filter-select" id="datePreset" onchange="handlePresetChange(this.value)">
          <option value="all">All time</option>
          <option value="7">Last 7 days</option>
          <option value="14">Last 14 days</option>
          <option value="30">Last 30 days</option>
          <option value="custom">Custom range</option>
        </select>
      </div>
      <div class="custom-dates" id="customDates">
        <input type="date" class="filter-date" id="startDate"/>
        <input type="date" class="filter-date" id="endDate"/>
      </div>
      <button class="apply-btn" onclick="applyFilters()">Apply filters</button>
    </div>
  </nav>

  <!-- MAIN -->
  <main class="main" id="mainContent">
    <div class="state-box">
      <div class="spinner"></div>
      <p>Loading dashboard...</p>
    </div>
  </main>
</div>

<!-- DRAWER -->
<div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
<div class="drawer" id="userDrawer">
  <div class="drawer-header">
    <div class="drawer-title" id="drawerTitle"></div>
    <button class="drawer-close" onclick="closeDrawer()">×</button>
  </div>
  <div id="drawerContent"></div>
</div>

<script>
Chart.register(ChartDataLabels);

const BASE = '/api';
let currentFunnelId = null;
let currentStartDate = null;
let currentEndDate = null;
let allUsers = [];
let currentUserFilter = 'all';
const chartInstances = {};

const q = id => document.getElementById(id);
const fmt = v => v != null ? Number(v).toFixed(1) : '—';
const fmtInt = v => v != null ? Number(v).toLocaleString() : '—';
const cap = s => s ? s.replace(/_/g,' ').replace(/\\b\\w/g, c => c.toUpperCase()) : '';

const STEP_COLORS = ['#6c63ff','#4ade80','#60a5fa','#fbbf24','#f472b6','#2dd4bf'];
const stepColor = i => STEP_COLORS[i % STEP_COLORS.length];
const channelColor = ch => ({ web: '#60a5fa', mobile: '#4ade80', email: '#fbbf24', referral: '#f472b6' }[ch] || '#8b90a8');

const tickStyle = { color: '#555a72', font: { family: "'DM Mono', monospace", size: 10 } };
const gridColor = 'rgba(255,255,255,0.04)';

function makeChart(id, config) {
  if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
  const el = q(id);
  if (!el) return;
  chartInstances[id] = new Chart(el, config);
}
function destroyCharts() {
  Object.keys(chartInstances).forEach(k => { chartInstances[k].destroy(); delete chartInstances[k]; });
}

function scrollToSection(id, el) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  el.classList.add('active');
  const sec = document.getElementById(id);
  if (sec) sec.scrollIntoView({ behavior: 'smooth' });
}

function initScrollObserver() {
  const sections = ['sec-summary','sec-steps','sec-time','sec-channels','sec-users'];
  const navMap = { 'sec-summary': 0, 'sec-steps': 1, 'sec-time': 2, 'sec-channels': 3, 'sec-users': 4 };
  const navItems = document.querySelectorAll('.nav-item');
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const idx = navMap[e.target.id];
        if (idx !== undefined) {
          navItems.forEach(n => n.classList.remove('active'));
          if (navItems[idx]) navItems[idx].classList.add('active');
        }
      }
    });
  }, { rootMargin: '-30% 0px -60% 0px' });
  sections.forEach(id => { const el = document.getElementById(id); if (el) obs.observe(el); });
}

function handlePresetChange(val) {
  q('customDates').style.display = val === 'custom' ? 'flex' : 'none';
}

function applyFilters() {
  const preset = q('datePreset').value;
  if (preset === 'all') {
    currentStartDate = null; currentEndDate = null;
  } else if (preset === 'custom') {
    currentStartDate = q('startDate').value ? q('startDate').value + 'T00:00:00' : null;
    currentEndDate = q('endDate').value ? q('endDate').value + 'T23:59:59' : null;
  } else {
    const days = parseInt(preset);
    const end = new Date(), start = new Date();
    start.setDate(start.getDate() - days);
    currentStartDate = start.toISOString().split('T')[0] + 'T00:00:00';
    currentEndDate = end.toISOString().split('T')[0] + 'T23:59:59';
  }
  if (currentFunnelId) loadDashboard(currentFunnelId);
}

function dateParams() {
  const p = new URLSearchParams();
  if (currentStartDate) p.set('start_date', currentStartDate);
  if (currentEndDate) p.set('end_date', currentEndDate);
  return p.toString() ? '?' + p.toString() : '';
}

function dateLabel() {
  if (!currentStartDate && !currentEndDate) return 'All time';
  if (currentStartDate && currentEndDate) return `${currentStartDate.split('T')[0]} → ${currentEndDate.split('T')[0]}`;
  if (currentStartDate) return `From ${currentStartDate.split('T')[0]}`;
  return `Until ${currentEndDate.split('T')[0]}`;
}

async function loadFunnelList() {
  try {
    const data = await fetch(`${BASE}/funnels`).then(r => r.json());
    const sel = q('funnelSelect');
    if (!data.funnels || !data.funnels.length) { sel.innerHTML = '<option>No funnels found</option>'; return; }
    sel.innerHTML = data.funnels.map(f => `<option value="${f.id}">${cap(f.funnel_name)}</option>`).join('');
    currentFunnelId = data.funnels[0].id;
    sel.value = currentFunnelId;
    loadDashboard(currentFunnelId);
  } catch(e) { showError('Could not connect to the API.'); }
}

function onFunnelChange(id) { currentFunnelId = id; loadDashboard(id); }

async function loadDashboard(funnelId) {
  q('mainContent').innerHTML = `<div class="state-box"><div class="spinner"></div><p>Loading funnel data...</p></div>`;
  destroyCharts();
  try {
    const dp = dateParams();
    const [summary, steps, time, channel, users] = await Promise.all([
      fetch(`${BASE}/analytics/funnel/${funnelId}/summary${dp}`).then(r => r.json()),
      fetch(`${BASE}/analytics/funnel/${funnelId}/steps${dp}`).then(r => r.json()),
      fetch(`${BASE}/analytics/funnel/${funnelId}/time${dp}`).then(r => r.json()),
      fetch(`${BASE}/analytics/funnel/${funnelId}/channel${dp}`).then(r => r.json()),
      fetch(`${BASE}/analytics/funnel/${funnelId}/users${dp}`).then(r => r.json()),
    ]);
    if (summary.error) { showError(summary.error); return; }
    allUsers = users.users || [];
    renderDashboard(summary, steps, time, channel, users);
  } catch(e) { showError('Failed to load funnel data.'); }
}

function showError(msg) {
  q('mainContent').innerHTML = `<div class="state-box">
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity=".3"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    <p>${msg}</p>
  </div>`;
}

function renderDashboard(summary, stepsData, timeData, channelData, usersData) {
  const steps = stepsData.steps || [];
  const time = timeData.time_analysis || [];
  const channels = channelData.channels || [];
  const drop = summary.biggest_drop_off_step;
  const slow = timeData.slowest_transition;
  const conv = summary.overall_conversion_percentage;
  const funnelName = summary.funnel_name || '';
  q('mainContent').innerHTML = buildHTML(summary, steps, time, channels, drop, slow, conv, funnelName, usersData);
  renderDropChart(steps);
  renderTimeChart(time);
  renderChannelCharts(channels);
  setTimeout(() => { renderChannelCards(channels); initScrollObserver(); }, 50);
}

function buildHTML(summary, steps, time, channels, drop, slow, conv, funnelName, usersData) {
  const users = usersData.users || [];
  const completedCount = users.filter(u => u.status === 'completed').length;
  const droppedEarly = users.filter(u => u.status === 'dropped early').length;
  const droppedMid = users.filter(u => u.status === 'dropped mid-funnel').length;
  const convColor = conv == null ? 'neutral' : conv >= 50 ? 'up' : 'down';

  return `
    <div class="page-header">
      <div>
        <h1>${cap(funnelName)}</h1>
        <p>Funnel ID ${summary.funnel_id} · <span class="date-range-label">${dateLabel()}</span></p>
      </div>
      <div class="header-badge"><div class="live-dot"></div>Live</div>
    </div>

    <div class="section-label" id="sec-summary">Overview</div>
    <div class="metrics-row">
      <div class="metric">
        <div class="m-label">Total started</div>
        <div class="m-value">${fmtInt(summary.total_started)}</div>
        <div class="m-sub neutral">unique users</div>
      </div>
      <div class="metric">
        <div class="m-label">Completed</div>
        <div class="m-value">${fmtInt(summary.total_completed)}</div>
        <div class="m-sub neutral">reached final step</div>
      </div>
      <div class="metric">
        <div class="m-label">Conversion rate</div>
        <div class="m-value ${convColor}">${conv != null ? conv + '%' : '—'}</div>
        <div class="m-sub ${convColor}">${conv != null ? (conv >= 50 ? '↑ Above 50% target' : '↓ Below 50% target') : 'No data'}</div>
      </div>
      <div class="metric">
        <div class="m-label">Funnel steps</div>
        <div class="m-value">${steps.length}</div>
        <div class="m-sub neutral">tracked steps</div>
      </div>
    </div>

    ${drop ? `<div class="alert">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      <span>Biggest drop-off at <strong>Step ${drop.step_order}: ${drop.step_name.replace(/_/g,' ')}</strong> — ${drop.drop_off_users} users lost (${drop.drop_off_percentage}% drop)</span>
    </div>` : ''}

    <div class="section-label" id="sec-steps">Step analysis</div>
    <div class="two-col">
      <div class="card">
        <div class="card-title">Funnel progression</div>
        <div class="funnel-visual">${buildFunnelViz(steps)}</div>
      </div>
      <div class="card">
        <div class="card-title">Drop-off by step</div>
        <div class="chart-box" style="height:220px;"><canvas id="dropChart"></canvas></div>
      </div>
    </div>
    <div class="card" style="margin-bottom:1rem;">
      <div class="card-title">Step breakdown</div>
      <table class="tbl">
        <thead><tr><th>Step</th><th class="num">Users</th><th class="num">Drop-off</th><th class="num">Drop %</th><th class="num">Conv %</th><th>Status</th></tr></thead>
        <tbody>${buildStepRows(steps)}</tbody>
      </table>
    </div>

    <div class="section-label" id="sec-time">Time analysis</div>
    <div class="two-col">
      <div class="card">
        <div class="card-title">Avg. minutes between steps</div>
        <div class="chart-box" style="height:220px;"><canvas id="timeChart"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Transition detail</div>
        <table class="tbl">
          <thead><tr><th>Transition</th><th class="num">Avg</th><th class="num">Min</th><th class="num">Max</th></tr></thead>
          <tbody>${buildTimeRows(time)}</tbody>
        </table>
        ${slow ? `<div class="slow-highlight">Slowest: <strong>${slow.step_name.replace(/_/g,' ')} → ${slow.next_step_name.replace(/_/g,' ')}</strong> · avg ${fmt(slow.avg_minutes_to_next_step)} min</div>` : ''}
      </div>
    </div>

    <div class="section-label" id="sec-channels">Channel breakdown</div>
    <div class="channel-grid" id="channelCards"></div>
    <div class="two-col">
      <div class="card">
        <div class="card-title">Users started by channel</div>
        <div class="chart-box" style="height:200px;"><canvas id="chanStartChart"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">Conversion rate by channel</div>
        <div class="chart-box" style="height:200px;"><canvas id="chanConvChart"></canvas></div>
      </div>
    </div>

    <div class="section-label" id="sec-users">User drill-down</div>
    <div class="filter-row">
      <div class="filter-pill active" onclick="filterUsers('all', this)">All (${users.length})</div>
      <div class="filter-pill" onclick="filterUsers('completed', this)">Completed (${completedCount})</div>
      <div class="filter-pill" onclick="filterUsers('dropped mid-funnel', this)">Dropped mid-funnel (${droppedMid})</div>
      <div class="filter-pill" onclick="filterUsers('dropped early', this)">Dropped early (${droppedEarly})</div>
    </div>
    <div class="card" style="margin-bottom:1.5rem;">
      <table class="tbl">
        <thead><tr><th>User</th><th>Channel</th><th>Last step</th><th>Status</th><th class="num">Time (min)</th><th>First seen</th></tr></thead>
        <tbody id="userTableBody">${buildUserRows(users)}</tbody>
      </table>
    </div>

    <div class="section-label">Insights</div>
    <div style="margin-bottom:1rem;">${buildInsights(summary, drop, slow, conv, channels)}</div>
    <div class="card" style="margin-bottom:2rem;">
      <div class="card-title">Strategic recommendations</div>
      <ul class="recs">
        <li><span class="rec-n">01</span><span>Simplify the highest drop-off step — reduce required fields, add inline help text, and break long forms into smaller sub-steps.</span></li>
        <li><span class="rec-n">02</span><span>Add a visible progress indicator so users know how many steps remain. This alone reduces abandonment by setting expectations.</span></li>
        <li><span class="rec-n">03</span><span>Implement save-and-resume so users interrupted mid-funnel can return without starting over.</span></li>
        <li><span class="rec-n">04</span><span>Send a re-engagement nudge 30 minutes after a user goes inactive at a high-drop step.</span></li>
        <li><span class="rec-n">05</span><span>A/B test the slowest step — try auto-filling fields from known data to cut avg. completion time.</span></li>
      </ul>
    </div>
  `;
}

function buildFunnelViz(steps) {
  if (!steps.length) return '<p style="color:var(--text-hint);font-size:13px;">No steps found.</p>';
  const maxUsers = steps[0].users_at_step || 1;
  return steps.map((s, i) => {
    const pct = Math.round(((s.users_at_step || 0) / maxUsers) * 100);
    return `<div>
      ${i > 0 && s.drop_off_percentage != null ? `<div class="drop-row"><span class="drop-pill">↓ ${fmt(s.drop_off_percentage)}% (${s.drop_off_users})</span></div>` : ''}
      <div class="funnel-bar-row">
        <div class="funnel-step-label" title="${s.step_name}">${s.step_name.replace(/_/g,' ')}</div>
        <div class="funnel-bar-track">
          <div class="funnel-bar-fill" style="width:${pct}%;background:${stepColor(i)};box-shadow:0 0 12px ${stepColor(i)}40;">
            <span>${s.users_at_step}</span>
          </div>
        </div>
        <div class="funnel-pct">${pct}%</div>
      </div>
    </div>`;
  }).join('');
}

function buildStepRows(steps) {
  return steps.map((s, i) => {
    const dropBadge = s.drop_off_percentage == null ? '' :
      s.drop_off_percentage > 25 ? '<span class="badge badge-red">High risk</span>' :
      s.drop_off_percentage > 10 ? '<span class="badge badge-amber">Watch</span>' :
      '<span class="badge badge-green">Healthy</span>';
    return `<tr>
      <td>${i+1}. ${s.step_name.replace(/_/g,' ')}</td>
      <td class="num">${fmtInt(s.users_at_step)}</td>
      <td class="num" style="color:${s.drop_off_users ? 'var(--red)' : 'inherit'}">${s.drop_off_users != null ? '−'+s.drop_off_users : '—'}</td>
      <td class="num">${s.drop_off_percentage != null ? s.drop_off_percentage+'%' : '—'}</td>
      <td class="num">${s.conversion_rate_percentage != null ? fmt(s.conversion_rate_percentage)+'%' : '—'}</td>
      <td>${i === 0 ? '<span class="badge badge-accent">Entry</span>' : dropBadge}</td>
    </tr>`;
  }).join('');
}

function buildTimeRows(time) {
  if (!time.length) return '<tr><td colspan="4" style="color:var(--text-hint);text-align:center;padding:1.5rem;">No time data available</td></tr>';
  return time.map(t => `<tr>
    <td style="font-size:11px;font-family:var(--mono);">${t.step_name.replace(/_/g,' ')} → ${t.next_step_name.replace(/_/g,' ')}</td>
    <td class="num">${fmt(t.avg_minutes_to_next_step)}m</td>
    <td class="num" style="color:var(--text-hint)">${fmt(t.min_minutes_to_next_step)}m</td>
    <td class="num" style="color:var(--text-hint)">${fmt(t.max_minutes_to_next_step)}m</td>
  </tr>`).join('');
}

function buildUserRows(users) {
  if (!users.length) return '<tr><td colspan="6" style="color:var(--text-hint);text-align:center;padding:1.5rem;">No users found</td></tr>';
  return users.map(u => {
    const statusBadge = u.status === 'completed' ? 'badge-green' : u.status === 'dropped early' ? 'badge-red' : 'badge-amber';
    const date = u.first_seen ? new Date(u.first_seen).toLocaleDateString() : '—';
    return `<tr class="clickable" onclick="openUserDrawer(${JSON.stringify(u).replace(/"/g,'&quot;')})">
      <td style="font-family:var(--mono);font-size:11px;color:var(--accent);">${u.user_id}</td>
      <td><span class="badge badge-blue">${u.channel || '—'}</span></td>
      <td style="font-size:12px;">${u.last_step ? u.last_step.replace(/_/g,' ') : '—'}</td>
      <td><span class="badge ${statusBadge}">${u.status}</span></td>
      <td class="num">${u.total_minutes != null ? u.total_minutes : '—'}</td>
      <td style="font-size:11px;color:var(--text-muted)">${date}</td>
    </tr>`;
  }).join('');
}

function buildInsights(summary, drop, slow, conv, channels) {
  const insights = [];
  if (conv != null && conv < 50) insights.push({ type:'warn', icon:'⚠️', title:'Low overall conversion', desc:`Only ${conv}% of users complete the funnel. Industry average for financial onboarding is 50–60%.` });
  if (drop) insights.push({ type:'warn', icon:'📉', title:`High drop-off at "${drop.step_name.replace(/_/g,' ')}"`, desc:`${drop.drop_off_users} users (${drop.drop_off_percentage}%) drop at this step — your biggest single point of leakage.` });
  if (slow) insights.push({ type:'info', icon:'⏱️', title:`Slowest: ${slow.step_name.replace(/_/g,' ')} → ${slow.next_step_name.replace(/_/g,' ')}`, desc:`Average of ${fmt(slow.avg_minutes_to_next_step)} minutes between these steps. Investigate friction in this transition.` });
  if (channels.length >= 2) {
    const sorted = [...channels].sort((a,b) => (b.conversion_rate||0) - (a.conversion_rate||0));
    const best = sorted[0], worst = sorted[sorted.length-1];
    if (best.channel !== worst.channel && best.conversion_rate - (worst.conversion_rate||0) > 10) {
      insights.push({ type:'info', icon:'📊', title:`${cap(best.channel)} outperforms ${worst.channel}`, desc:`${cap(best.channel)} converts at ${best.conversion_rate}% vs ${worst.conversion_rate||0}% on ${worst.channel}.` });
    }
  }
  if (conv != null && conv >= 50) insights.push({ type:'ok', icon:'✅', title:'Conversion above target', desc:`${conv}% end-to-end conversion is healthy. Focus on closing the gap at the highest drop-off step.` });
  if (!insights.length) insights.push({ type:'info', icon:'ℹ️', title:'Funnel loaded', desc:'Add more user events to generate actionable insights.' });
  return insights.map(ins => `
    <div class="insight">
      <div class="insight-icon i-${ins.type}">${ins.icon}</div>
      <div class="insight-body">
        <div class="i-title">${ins.title}</div>
        <div class="i-desc">${ins.desc}</div>
      </div>
    </div>`).join('');
}

function renderChannelCards(channels) {
  const el = q('channelCards');
  if (!el) return;
  if (!channels.length) { el.innerHTML = '<p style="color:var(--text-hint);font-size:13px;">No channel data.</p>'; return; }
  el.innerHTML = channels.map(ch => {
    const color = channelColor(ch.channel);
    return `<div class="channel-card">
      <div class="ch-name">${ch.channel || 'unknown'}</div>
      <div class="ch-conv" style="color:${color}">${ch.conversion_rate != null ? ch.conversion_rate + '%' : '—'}</div>
      <div class="ch-sub">${ch.started} started · ${ch.completed} completed</div>
      <div class="ch-bar"><div class="ch-bar-fill" style="width:${ch.conversion_rate||0}%;background:${color};box-shadow:0 0 8px ${color}60;"></div></div>
    </div>`;
  }).join('');
}

function filterUsers(status, el) {
  document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  currentUserFilter = status;
  const filtered = status === 'all' ? allUsers : allUsers.filter(u => u.status === status);
  const tbody = q('userTableBody');
  if (tbody) tbody.innerHTML = buildUserRows(filtered);
}

function openUserDrawer(user) {
  q('drawerTitle').textContent = user.user_id;
  const date = d => d ? new Date(d).toLocaleString() : '—';
  const statusBadge = user.status === 'completed' ? 'badge-green' : user.status === 'dropped early' ? 'badge-red' : 'badge-amber';
  q('drawerContent').innerHTML = `
    <div class="user-stat-row">
      <div class="user-stat"><div class="us-label">Status</div><div class="us-value" style="font-size:13px;margin-top:6px;"><span class="badge ${statusBadge}">${user.status}</span></div></div>
      <div class="user-stat"><div class="us-label">Channel</div><div class="us-value"><span class="badge badge-blue">${user.channel || '—'}</span></div></div>
      <div class="user-stat"><div class="us-label">Steps</div><div class="us-value">${user.steps_completed}</div></div>
      <div class="user-stat"><div class="us-label">Time</div><div class="us-value">${user.total_minutes != null ? user.total_minutes+'m' : '—'}</div></div>
    </div>
    <div style="margin-top:1rem;">
      <div style="font-size:10px;color:var(--text-hint);font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">First seen</div>
      <div style="font-size:13px;font-family:var(--mono);">${date(user.first_seen)}</div>
    </div>
    <div style="margin-top:12px;">
      <div style="font-size:10px;color:var(--text-hint);font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">Last seen</div>
      <div style="font-size:13px;font-family:var(--mono);">${date(user.last_seen)}</div>
    </div>
    <div style="margin-top:12px;">
      <div style="font-size:10px;color:var(--text-hint);font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">Last step reached</div>
      <div style="font-size:15px;font-weight:800;">${user.last_step ? user.last_step.replace(/_/g,' ') : '—'}</div>
    </div>
    ${!user.completed
      ? `<div style="margin-top:1rem;padding:14px;background:var(--red-bg);border:1px solid rgba(248,113,113,0.2);border-radius:var(--radius-md);font-size:12px;color:var(--red);">This user did not complete the funnel. Consider a re-engagement campaign targeting users who dropped at <strong>${user.last_step ? user.last_step.replace(/_/g,' ') : 'the last'}</strong> step.</div>`
      : `<div style="margin-top:1rem;padding:14px;background:var(--green-bg);border:1px solid rgba(74,222,128,0.2);border-radius:var(--radius-md);font-size:12px;color:var(--green);">✓ This user successfully completed the funnel in ${user.total_minutes} minutes.</div>`
    }
  `;
  q('drawerOverlay').classList.add('open');
  q('userDrawer').classList.add('open');
}

function closeDrawer() {
  q('drawerOverlay').classList.remove('open');
  q('userDrawer').classList.remove('open');
}

function renderDropChart(steps) {
  const labels = steps.slice(1).map(s => s.step_name.replace(/_/g,' '));
  const data = steps.slice(1).map(s => s.drop_off_percentage || 0);
  const colors = data.map(v => v > 25 ? '#f87171' : v > 10 ? '#fbbf24' : '#4ade80');
  makeChart('dropChart', {
    type: 'bar',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderRadius: 6, borderSkipped: false }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 20 } },
      plugins: {
        legend: { display: false },
        datalabels: { anchor: 'end', align: 'top', color: '#8b90a8', font: { family: "'DM Mono'", size: 10 }, formatter: v => v > 0 ? v + '%' : '' }
      },
      scales: {
        x: { grid: { display: false }, ticks: { ...tickStyle, maxRotation: 25 } },
        y: { max: 100, grid: { color: gridColor }, ticks: { ...tickStyle, callback: v => v + '%' }, beginAtZero: true }
      }
    }
  });
}

function renderTimeChart(time) {
  const labels = time.map(t => t.step_name.replace(/_/g,' ').split(' ')[0] + ' →');
  const data = time.map(t => t.avg_minutes_to_next_step || 0);
  makeChart('timeChart', {
    type: 'bar',
    data: { labels, datasets: [{ data, backgroundColor: '#6c63ff', borderRadius: 6, borderSkipped: false }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 20 } },
      plugins: {
        legend: { display: false },
        datalabels: { anchor: 'end', align: 'top', color: '#8b90a8', font: { family: "'DM Mono'", size: 10 }, formatter: v => v > 0 ? v + 'm' : '' }
      },
      scales: {
        x: { grid: { display: false }, ticks: tickStyle },
        y: { grid: { color: gridColor }, ticks: { ...tickStyle, callback: v => v + 'm' }, beginAtZero: true }
      }
    }
  });
}

function renderChannelCharts(channels) {
  if (!channels.length) return;
  const labels = channels.map(c => cap(c.channel));
  const colors = channels.map(c => channelColor(c.channel));
  makeChart('chanStartChart', {
    type: 'bar',
    data: { labels, datasets: [{ data: channels.map(c => c.started), backgroundColor: colors, borderRadius: 6, borderSkipped: false }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 20 } },
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'top', color: '#8b90a8', font: { family: "'DM Mono'", size: 10 }, formatter: v => v > 0 ? v : '' } },
      scales: { x: { grid: { display: false }, ticks: tickStyle }, y: { grid: { color: gridColor }, ticks: tickStyle, beginAtZero: true } }
    }
  });
  makeChart('chanConvChart', {
    type: 'bar',
    data: { labels, datasets: [{ data: channels.map(c => c.conversion_rate || 0), backgroundColor: colors, borderRadius: 6, borderSkipped: false }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 20 } },
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'top', color: '#8b90a8', font: { family: "'DM Mono'", size: 10 }, formatter: v => v > 0 ? v + '%' : '' } },
      scales: { x: { grid: { display: false }, ticks: tickStyle }, y: { max: 100, grid: { color: gridColor }, ticks: { ...tickStyle, callback: v => v + '%' }, beginAtZero: true } }
    }
  });
}

loadFunnelList();
</script>
</body>
</html>
"""

@app.get("/")
def serve_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)


# ---------- Models ----------

class StartEvent(BaseModel):
    user_id: str
    funnel_name: str
    step_name: str
    channel: str

class FunnelCreate(BaseModel):
    funnel_name: str
    description: str | None = None


# ---------- Helpers ----------

def build_date_params(base: dict, start_date: Optional[str], end_date: Optional[str]) -> dict:
    if start_date:
        base["start_date"] = start_date
    if end_date:
        base["end_date"] = end_date
    return base


# ---------- Health ----------

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ---------- Events ----------

@app.post("/api/events/start")
def create_start_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'start', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/step")
def create_step_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'step', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "step event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/complete")
def create_complete_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'complete', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "complete event saved", "event_id": new_id}
    finally:
        db.close()

@app.post("/api/events/abandon")
def create_abandon_event(event: StartEvent):
    db = SessionLocal()
    try:
        new_id = db.execute(text("""
            INSERT INTO events (user_id, funnel_name, step_name, event_type, channel)
            VALUES (:user_id, :funnel_name, :step_name, 'abandon', :channel)
            RETURNING id;
        """), {"user_id": event.user_id, "funnel_name": event.funnel_name,
               "step_name": event.step_name, "channel": event.channel}).scalar()
        db.commit()
        return {"message": "abandon event saved", "event_id": new_id}
    finally:
        db.close()


# ---------- Funnels ----------

@app.post("/api/funnels")
def create_funnel(funnel: FunnelCreate):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            INSERT INTO funnels (funnel_name, description)
            VALUES (:funnel_name, :description)
            RETURNING id, funnel_name, description, created_at;
        """), {"funnel_name": funnel.funnel_name, "description": funnel.description}).mappings().first()
        db.commit()
        return dict(result)
    finally:
        db.close()

@app.get("/api/funnels")
def get_funnels():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels ORDER BY id ASC;
        """)).mappings().all()
        return {"funnels": [dict(row) for row in result]}
    finally:
        db.close()

@app.get("/api/funnels/{funnel_id}")
def get_funnel_by_id(funnel_id: int):
    db = SessionLocal()
    try:
        funnel = db.execute(text("""
            SELECT id, funnel_name, description, created_at
            FROM funnels WHERE id = :funnel_id;
        """), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        steps = db.execute(text("""
            SELECT id, step_name, step_order, created_at
            FROM funnel_steps WHERE funnel_id = :funnel_id ORDER BY step_order;
        """), {"funnel_id": funnel_id}).mappings().all()
        return {"funnel": dict(funnel), "steps": [dict(s) for s in steps]}
    finally:
        db.close()


# ---------- Analytics ----------

@app.get("/api/analytics/funnel/{funnel_id}/steps")
def funnel_step_report(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        date_filter = ""
        if start_date:
            date_filter += " AND e.created_at >= :start_date"
        if end_date:
            date_filter += " AND e.created_at <= :end_date"
        params = build_date_params({"funnel_id": funnel_id}, start_date, end_date)
        rows = db.execute(text(f"""
            WITH step_users AS (
                SELECT fs.step_order, fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e
                    ON e.funnel_name = (SELECT funnel_name FROM funnels WHERE id = :funnel_id)
                    AND e.step_name = fs.step_name
                    {date_filter}
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            )
            SELECT step_order, step_name, users_at_step,
                LAG(users_at_step) OVER (ORDER BY step_order) AS users_previous_step,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     ELSE LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step
                END AS drop_off_users,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                     ELSE ROUND(((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                          / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                END AS drop_off_percentage,
                CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                     WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                     ELSE ROUND((users_at_step::numeric / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                END AS conversion_rate_percentage
            FROM step_users ORDER BY step_order;
        """), params).mappings().all()
        return {"funnel_id": funnel_id, "funnel_name": funnel["funnel_name"], "steps": [dict(r) for r in rows]}
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/summary")
def funnel_summary(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        where_date_filter = ""
        join_date_filter = ""
        if start_date:
            where_date_filter += " AND created_at >= :start_date"
            join_date_filter += " AND e.created_at >= :start_date"
        if end_date:
            where_date_filter += " AND created_at <= :end_date"
            join_date_filter += " AND e.created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        total_started = db.execute(text(f"""
            SELECT COUNT(DISTINCT user_id) FROM events
            WHERE funnel_name = :funnel_name AND event_type = 'start' {where_date_filter};
        """), params).scalar() or 0
        total_completed = db.execute(text(f"""
            SELECT COUNT(DISTINCT user_id) FROM events
            WHERE funnel_name = :funnel_name AND event_type = 'complete' {where_date_filter};
        """), params).scalar() or 0
        overall_conversion = round((total_completed / total_started) * 100, 2) if total_started > 0 else None
        biggest_drop = db.execute(text(f"""
            WITH step_users AS (
                SELECT fs.step_order, fs.step_name,
                    COUNT(DISTINCT e.user_id) AS users_at_step
                FROM funnel_steps fs
                LEFT JOIN events e ON e.funnel_name = :funnel_name
                    AND e.step_name = fs.step_name {join_date_filter}
                WHERE fs.funnel_id = :funnel_id
                GROUP BY fs.step_order, fs.step_name
            ),
            step_metrics AS (
                SELECT step_order, step_name,
                    CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                         ELSE LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step
                    END AS drop_off_users,
                    CASE WHEN LAG(users_at_step) OVER (ORDER BY step_order) IS NULL THEN NULL
                         WHEN LAG(users_at_step) OVER (ORDER BY step_order) = 0 THEN NULL
                         ELSE ROUND(((LAG(users_at_step) OVER (ORDER BY step_order) - users_at_step)::numeric
                              / LAG(users_at_step) OVER (ORDER BY step_order)) * 100, 2)
                    END AS drop_off_percentage
                FROM step_users
            )
            SELECT step_order, step_name, drop_off_users, drop_off_percentage
            FROM step_metrics WHERE drop_off_percentage IS NOT NULL
            ORDER BY drop_off_percentage DESC LIMIT 1;
        """), params).mappings().first()
        return {
            "funnel_id": funnel_id, "funnel_name": funnel_name,
            "total_started": total_started, "total_completed": total_completed,
            "overall_conversion_percentage": overall_conversion,
            "biggest_drop_off_step": dict(biggest_drop) if biggest_drop else None
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/time")
def funnel_time_analysis(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        date_filter = ""
        if start_date:
            date_filter += " AND created_at >= :start_date"
        if end_date:
            date_filter += " AND created_at <= :end_date"
        params = build_date_params(
            {"funnel_id": funnel_id, "funnel_name": funnel_name},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH ordered_steps AS (
                SELECT step_order, step_name,
                    LEAD(step_name) OVER (ORDER BY step_order) AS next_step_name,
                    LEAD(step_order) OVER (ORDER BY step_order) AS next_step_order
                FROM funnel_steps WHERE funnel_id = :funnel_id
            ),
            first_step_time AS (
                SELECT user_id, step_name, MIN(created_at) AS first_time
                FROM events WHERE funnel_name = :funnel_name {date_filter}
                GROUP BY user_id, step_name
            ),
            step_pairs AS (
                SELECT os.step_order, os.step_name, os.next_step_order, os.next_step_name,
                    fst1.user_id, fst1.first_time AS step_time, fst2.first_time AS next_step_time
                FROM ordered_steps os
                JOIN first_step_time fst1 ON fst1.step_name = os.step_name
                JOIN first_step_time fst2 ON fst2.step_name = os.next_step_name AND fst2.user_id = fst1.user_id
                WHERE os.next_step_name IS NOT NULL
            )
            SELECT step_order, step_name, next_step_order, next_step_name,
                COUNT(*) AS users_with_both_steps,
                ROUND(AVG(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS avg_minutes_to_next_step,
                ROUND(MIN(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS min_minutes_to_next_step,
                ROUND(MAX(EXTRACT(EPOCH FROM (next_step_time - step_time)) / 60), 2) AS max_minutes_to_next_step
            FROM step_pairs WHERE next_step_time >= step_time
            GROUP BY step_order, step_name, next_step_order, next_step_name
            ORDER BY step_order;
        """), params).mappings().all()
        time_analysis = [dict(r) for r in rows]
        slowest = max(time_analysis, key=lambda x: x["avg_minutes_to_next_step"] or -1) if time_analysis else None
        return {
            "funnel_id": funnel_id, "funnel_name": funnel_name,
            "slowest_transition": slowest, "time_analysis": time_analysis
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/channel")
def funnel_channel_breakdown(
    funnel_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        date_filter = ""
        if start_date:
            date_filter += " AND created_at >= :start_date"
        if end_date:
            date_filter += " AND created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH channel_stats AS (
                SELECT
                    channel,
                    COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'start') AS started,
                    COUNT(DISTINCT user_id) FILTER (WHERE event_type = 'complete') AS completed
                FROM events
                WHERE funnel_name = :funnel_name {date_filter}
                GROUP BY channel
            )
            SELECT channel, started, completed,
                CASE WHEN started = 0 THEN NULL
                     ELSE ROUND((completed::numeric / started) * 100, 2)
                END AS conversion_rate
            FROM channel_stats ORDER BY started DESC;
        """), params).mappings().all()
        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "channels": [dict(r) for r in rows]
        }
    finally:
        db.close()

@app.get("/api/analytics/funnel/{funnel_id}/users")
def funnel_user_drilldown(
    funnel_id: int,
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    db = SessionLocal()
    try:
        funnel = db.execute(text(
            "SELECT funnel_name FROM funnels WHERE id = :funnel_id;"
        ), {"funnel_id": funnel_id}).mappings().first()
        if not funnel:
            return {"error": "Funnel not found"}
        funnel_name = funnel["funnel_name"]
        where_date_filter = ""
        e_date_filter = ""
        if start_date:
            where_date_filter += " AND created_at >= :start_date"
            e_date_filter += " AND e.created_at >= :start_date"
        if end_date:
            where_date_filter += " AND created_at <= :end_date"
            e_date_filter += " AND e.created_at <= :end_date"
        params = build_date_params(
            {"funnel_name": funnel_name, "funnel_id": funnel_id},
            start_date, end_date
        )
        rows = db.execute(text(f"""
            WITH user_journey AS (
                SELECT
                    user_id,
                    MAX(channel) AS channel,
                    MIN(created_at) AS first_seen,
                    MAX(created_at) AS last_seen,
                    COUNT(DISTINCT step_name) AS steps_completed,
                    BOOL_OR(event_type = 'complete') AS completed,
                    ROUND(EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 60, 1) AS total_minutes
                FROM events
                WHERE funnel_name = :funnel_name {where_date_filter}
                GROUP BY user_id
            ),
            user_last_step AS (
                SELECT DISTINCT ON (e.user_id)
                    e.user_id, fs.step_name AS last_step, fs.step_order
                FROM events e
                JOIN funnel_steps fs ON fs.step_name = e.step_name AND fs.funnel_id = :funnel_id
                WHERE e.funnel_name = :funnel_name {e_date_filter}
                ORDER BY e.user_id, fs.step_order DESC
            )
            SELECT
                uj.user_id, uj.channel, uj.first_seen, uj.last_seen,
                uj.steps_completed, uj.completed, uls.last_step, uj.total_minutes,
                CASE WHEN uj.completed THEN 'completed'
                     WHEN uj.steps_completed = 1 THEN 'dropped early'
                     ELSE 'dropped mid-funnel'
                END AS status
            FROM user_journey uj
            LEFT JOIN user_last_step uls ON uls.user_id = uj.user_id
            ORDER BY uj.first_seen DESC;
        """), params).mappings().all()
        users = [dict(r) for r in rows]
        if status:
            users = [u for u in users if u["status"] == status]
        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel_name,
            "total_users": len(users),
            "users": users
        }
    finally:
        db.close()


        