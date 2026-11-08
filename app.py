"""
Student Registry — Streamlit frontend for the FastAPI student API.

Run the API first:     uvicorn main:app --reload
Then this app:         streamlit run streamlit_app/app.py

Needs streamlit >= 1.50 (pills, segmented controls, dialogs, selectable tables).
"""

import math
import re
import time
from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Student Registry", page_icon="📘", layout="wide")

# ═══════════════════════════════ Styling ═══════════════════════════════
# ═══════════════════════════════ Theme ═══════════════════════════════
# Follow whatever theme Streamlit is actually showing (dark or light), so every
# custom colour below matches Streamlit's own widgets.
def _theme_type() -> str:
    try:
        t = st.context.theme.type
    except Exception:
        t = None
    return t if t in ("light", "dark") else "dark"


THEME = _theme_type()
DARK = THEME == "dark"

P = (
    dict(bg="#111110", surface="#191917", surface2="#211f1c", raised="#262420",
         ink="#edebe4", ink2="#c3bfb5", muted="#8b877c", line="#2a2824", line_strong="#3b3832",
         accent="#8fcfb5", accent_soft="#8fcfb51a", danger="#ef8a74", danger_strong="#d9654c",
         grid="#24221f", shadow="0 1px 0 rgba(255,255,255,.03) inset, 0 10px 30px rgba(0,0,0,.35)")
    if DARK else
    dict(bg="#f5f3ee", surface="#fffdf9", surface2="#efece5", raised="#ffffff",
         ink="#1d1c19", ink2="#4a4740", muted="#7a766c", line="#e2ded4", line_strong="#cfcabd",
         accent="#2d5a4c", accent_soft="#2d5a4c14", danger="#b0412d", danger_strong="#b0412d",
         grid="#ece8df", shadow="0 1px 2px rgba(20,18,14,.04), 0 8px 24px rgba(20,18,14,.06)")
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap');

:root {
  --bg: %(bg)s; --surface: %(surface)s; --surface-2: %(surface2)s; --raised: %(raised)s;
  --ink: %(ink)s; --ink-2: %(ink2)s; --muted: %(muted)s;
  --line: %(line)s; --line-strong: %(line_strong)s;
  --accent: %(accent)s; --accent-soft: %(accent_soft)s;
  --danger: %(danger)s; --danger-strong: %(danger_strong)s;
  --shadow: %(shadow)s;
}

/* ---------- Base ---------- */
.stApp { background: var(--bg) !important; color: var(--ink); }
html, body, .stApp, .stMarkdown, p, label, input, textarea, button {
  font-family: "Geist", system-ui, -apple-system, sans-serif !important;
}
code, .mono { font-family: "Geist Mono", ui-monospace, monospace !important; font-size: .86em; }
.stMarkdown code { background: var(--surface-2); color: var(--ink-2); padding: 1px 6px; border-radius: 5px; }
#MainMenu, footer, [data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="InputInstructions"] { display: none !important; }
.block-container { padding-top: 2.4rem !important; padding-bottom: 4rem; max-width: 1240px; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

/* ---------- Header ---------- */
.reg-title { font-family: "Instrument Serif", Georgia, serif !important; font-weight: 400; font-size: 54px;
  line-height: 1; margin: 0 0 8px; color: var(--ink); letter-spacing: -0.015em; }
.reg-title em { color: var(--accent); font-style: italic; }
.reg-sub { color: var(--muted); margin: 0; font-size: 15px; }

/* ---------- Stat cards ---------- */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 26px 0 10px; }
.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px;
  box-shadow: var(--shadow); transition: transform .18s ease, border-color .18s; animation: fadeUp .4s ease both; }
.stat:nth-child(2) { animation-delay: .05s; } .stat:nth-child(3) { animation-delay: .1s; } .stat:nth-child(4) { animation-delay: .15s; }
.stat:hover { transform: translateY(-2px); border-color: var(--line-strong); }
.stat-label { font-size: 11.5px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
.stat-value { font-family: "Instrument Serif", Georgia, serif !important; font-size: 40px; line-height: 1.1; color: var(--ink);
  margin-top: 6px; font-variant-numeric: tabular-nums; }
.stat-sub { font-size: 12.5px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.spread { display: flex; height: 8px; border-radius: 999px; overflow: hidden; margin: 18px 0 12px; gap: 2px; }
.legend { display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 12px; color: var(--muted); }
.legend i { display: inline-block; width: 7px; height: 7px; border-radius: 2px; margin-right: 5px; }
@media (max-width: 900px) { .stats { grid-template-columns: 1fr 1fr; } }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 28px; border-bottom: 1px solid var(--line); background: transparent; }
.stTabs [data-baseweb="tab"] { padding: 12px 0; background: transparent !important; }
.stTabs [data-baseweb="tab"] p { font-size: 15px; font-weight: 500; color: var(--muted) !important; }
.stTabs [data-baseweb="tab"]:hover p { color: var(--ink) !important; }
.stTabs [aria-selected="true"] p { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--ink) !important; height: 2px; }
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px; animation: fadeUp .3s ease both; }

/* ---------- Labels & inputs ---------- */
[data-testid="stWidgetLabel"] p { font-size: 12px !important; color: var(--muted) !important; font-weight: 500;
  text-transform: uppercase; letter-spacing: .06em; }
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div {
  background: var(--surface) !important; border-color: var(--line) !important; border-radius: 10px !important; }
[data-baseweb="input"] input, [data-baseweb="select"] div { color: var(--ink) !important; }
[data-baseweb="input"] input::placeholder { color: var(--muted) !important; opacity: 1; }
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
  border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-soft) !important; }

/* ---------- Buttons ---------- */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
  border-radius: 10px !important; font-weight: 500; min-height: 42px;
  background: var(--surface) !important; color: var(--ink) !important; border: 1px solid var(--line) !important;
  transition: transform .12s ease, background .15s, border-color .15s; }
.stButton button p, .stDownloadButton button p, .stFormSubmitButton button p { color: inherit !important; }
.stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
  background: var(--surface-2) !important; border-color: var(--line-strong) !important; }
.stButton button:active { transform: scale(.98); }
.stButton button:disabled, .stFormSubmitButton button:disabled { opacity: .4; }
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--ink) !important; color: var(--bg) !important; border-color: var(--ink) !important; }
.stButton button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { opacity: .88; background: var(--ink) !important; }
.st-key-danger_zone button { background: var(--danger-strong) !important; border-color: var(--danger-strong) !important; color: #fff !important; }
.st-key-danger_zone button:hover { opacity: .9; }

/* Pills & segmented controls */
[data-testid="stButtonGroup"] { gap: 6px !important; }
[data-testid="stButtonGroup"] button {
  border-radius: 999px !important; border: 1px solid var(--line) !important; background: var(--surface) !important;
  color: var(--ink-2) !important; min-height: 34px; padding: 0 14px !important; transition: all .15s; }
[data-testid="stButtonGroup"] button p { color: inherit !important; font-size: 13.5px; }
[data-testid="stButtonGroup"] button:hover { border-color: var(--line-strong) !important; color: var(--ink) !important; }
[data-testid="stButtonGroup"] button[kind$="Active"], [data-testid="stButtonGroup"] button[data-testid$="Active"] {
  background: var(--ink) !important; color: var(--bg) !important; border-color: var(--ink) !important; }
[data-testid="stButtonGroup"] button:disabled { opacity: .35; }

/* Slider */
[data-testid="stSlider"] [role="slider"] { background: var(--ink) !important; border: 3px solid var(--bg); box-shadow: 0 0 0 1px var(--line-strong) !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {
  color: var(--ink-2) !important; font-family: "Geist Mono", monospace !important; font-size: 12px; }

/* ---------- Request line ---------- */
.req { font-family: "Geist Mono", monospace; font-size: 12px; background: var(--surface); border: 1px solid var(--line); color: var(--ink-2);
  padding: 10px 14px; border-radius: 10px; display: flex; gap: 10px; margin: 8px 0 14px; overflow-x: auto; white-space: nowrap; }
.req .m { font-weight: 600; color: var(--accent); }
.req .m.POST { color: #7aaee0; } .req .m.PUT { color: #d9a65e; } .req .m.DELETE { color: var(--danger); }
.req .c { margin-left: auto; color: var(--muted); } .req .c.err { color: var(--danger); }

/* ---------- Table ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
.hint { font-size: 12.5px; color: var(--muted); margin: 8px 2px 4px; }
.pageinfo { text-align: center; color: var(--muted); font-size: 13px; padding-top: 11px; }

/* ---------- Profile panel ---------- */
.profile { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 22px;
  box-shadow: var(--shadow); animation: fadeUp .3s ease both; }
.profile .pid { font-size: 12px; color: var(--muted); }
.profile .pname { font-family: "Instrument Serif", Georgia, serif !important; font-size: 32px; line-height: 1.1;
  margin: 2px 0 16px; color: var(--ink); }
.ring-row { display: flex; align-items: center; gap: 16px; padding: 14px; background: var(--surface-2); border-radius: 12px; margin-bottom: 16px; }
.ring { width: 76px; height: 76px; border-radius: 50%%; display: grid; place-items: center; flex: none; }
.ring > div { width: 62px; height: 62px; border-radius: 50%%; background: var(--surface-2); display: grid; place-items: center;
  font-family: "Instrument Serif", serif; font-size: 26px; color: var(--ink); }
.ring-meta { font-size: 13px; color: var(--muted); line-height: 1.75; }
.ring-meta b { color: var(--ink); font-weight: 500; }
.facts { display: grid; grid-template-columns: 70px 1fr; row-gap: 10px; font-size: 13.5px; margin: 0; }
.facts dt { color: var(--muted); } .facts dd { margin: 0; color: var(--ink); word-break: break-word; }
.facts a { color: var(--ink) !important; text-decoration: underline; text-decoration-color: var(--line-strong); text-underline-offset: 3px; }
.cmp { margin-top: 16px; font-size: 12.5px; color: var(--muted); }
.cmp-bar { position: relative; height: 6px; border-radius: 999px; background: var(--surface-2); margin: 10px 0 4px; }
.cmp-bar .fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; }
.cmp-bar .avg { position: absolute; top: -4px; width: 2px; height: 14px; background: var(--ink); border-radius: 1px; }
.empty-panel { border: 1px dashed var(--line-strong); border-radius: 14px; padding: 44px 22px; text-align: center; color: var(--muted); font-size: 13.5px; }
.empty-panel .eh { font-family: "Instrument Serif", serif; font-size: 26px; color: var(--ink); margin-bottom: 6px; }

.chip { display: inline-block; padding: 1px 9px; border-radius: 999px; font-size: 12px; font-weight: 600; vertical-align: 1px; }
.course { display: inline-flex; align-items: center; gap: 6px; }
.course::before { content: ""; width: 7px; height: 7px; border-radius: 50%%; background: var(--cc); }

/* ---------- Dialog ---------- */
[data-testid="stDialog"] [role="dialog"] { background: var(--surface) !important; border: 1px solid var(--line); border-radius: 18px !important; }
[data-testid="stDialog"] h2, [data-testid="stDialog"] [role="dialog"] > div:first-child div[class*="Heading"] {
  font-family: "Instrument Serif", Georgia, serif !important; font-weight: 400 !important; font-size: 30px !important; }
.ferr { color: var(--danger); font-size: 12.5px; margin: -8px 0 10px; }
.preview, .diff { font-size: 13px; color: var(--ink-2); background: var(--surface-2); border-radius: 10px; padding: 11px 14px; margin: 4px 0 16px; }
.preview { display: flex; align-items: center; gap: 10px; }
.diff div { padding: 2px 0; } .diff s { color: var(--muted); } .diff b { color: var(--accent); font-weight: 600; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] * { color: var(--ink); }
.side-h { font-size: 11.5px; color: var(--muted) !important; text-transform: uppercase; letter-spacing: .08em; font-weight: 500; margin: 6px 0 8px; }
.status { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; padding: 6px 12px; border-radius: 999px;
  background: var(--surface-2); border: 1px solid var(--line); color: var(--ink-2) !important; margin: 2px 0 10px; }
.status i { width: 8px; height: 8px; border-radius: 50%%; }
.status.ok i { background: #4fb486; animation: pulse 2s ease-in-out infinite; }
.status.bad i { background: var(--danger); }
@keyframes pulse { 0%%, 100%% { box-shadow: 0 0 0 0 #4fb48666; } 50%% { box-shadow: 0 0 0 6px #4fb48600; } }
[data-testid="stSidebar"] [data-testid="stExpander"] details { border: 1px solid var(--line) !important; border-radius: 10px; background: var(--surface-2); }

/* ---------- Charts ---------- */
[data-testid="stVegaLiteChart"] { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 12px 8px; }
.chart-title { font-family: "Instrument Serif", serif !important; font-size: 24px; color: var(--ink); margin: 0 0 2px; }
.chart-sub { font-size: 12.5px; color: var(--muted); margin: 0 0 12px; }
</style>
""" % P,
    unsafe_allow_html=True,
)

# ═══════════════════════════════ Helpers ═══════════════════════════════
GRADES = ["A+", "A", "B", "C", "F"]
GRADE_COLORS = (
    {"A+": "#8fcfb5", "A": "#6aa891", "B": "#b6c27f", "C": "#dfa95f", "F": "#ef8a74"} if DARK else
    {"A+": "#2d5a4c", "A": "#4f7f6b", "B": "#8a9a5b", "C": "#c08a3e", "F": "#b0412d"}
)
COURSE_HUES = (
    ["#8fcfb5", "#7aaee0", "#dfa95f", "#b49ae0", "#ef8a74", "#79c2c4", "#b6c27f", "#e08fb6"] if DARK else
    ["#2d5a4c", "#3a7bbf", "#b8862b", "#8a5fb0", "#c0563f", "#4f8a8b", "#7a8b3a", "#b0587f"]
)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def grade_of(marks: int) -> str:
    if marks >= 90:
        return "A+"
    if marks >= 80:
        return "A"
    if marks >= 70:
        return "B"
    if marks >= 60:
        return "C"
    return "F"


def esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def chip(g: str) -> str:
    c = GRADE_COLORS[g]
    return f'<span class="chip" style="color:{c};background:{c}1f">{g}</span>'


def to_rows(data) -> list[dict]:
    """Accept the dict shape ({id: {...}}) or the list shape ([{id, ...}])."""
    if isinstance(data, dict):
        return [{"id": k, **v} for k, v in data.items()]
    return [dict(r) for r in (data or [])]


class ApiError(Exception):
    def __init__(self, status: int, detail):
        self.status, self.detail = status, detail
        super().__init__(self.message)

    @property
    def fields(self) -> dict:
        """422 detail → {field: message}"""
        out = {}
        if isinstance(self.detail, list):
            for e in self.detail:
                out[str(e.get("loc", ["?"])[-1])] = str(e.get("msg", "Invalid")).removeprefix("Value error, ")
        return out

    @property
    def message(self) -> str:
        if self.fields:
            return " · ".join(f"{k}: {v}" for k, v in self.fields.items())
        return str(self.detail)


def api(method: str, path: str, body: dict | None = None):
    """Call the API, remember it for the request bar, and log it for the Activity tab."""
    base = st.session_state.api_base.rstrip("/")
    started = time.perf_counter()
    try:
        res = requests.request(method, base + path, json=body, timeout=8)
    except requests.RequestException:
        _record(method, path, "—", 0, True)
        raise ApiError(0, "Can't reach the API. Is `uvicorn main:app --reload` running?")
    ms = round((time.perf_counter() - started) * 1000)
    _record(method, path, res.status_code, ms, not res.ok)
    try:
        data = res.json()
    except ValueError:
        data = None
    if not res.ok:
        detail = data.get("detail", res.reason) if isinstance(data, dict) else res.reason
        raise ApiError(res.status_code, detail)
    return data


def _record(method, path, status, ms, err):
    st.session_state.last_req = (method, path, f"{status} · {ms} ms" if ms else "network error", err)
    st.session_state.log.insert(
        0, {"time": datetime.now().strftime("%H:%M:%S"), "method": method, "path": path, "status": status, "ms": ms}
    )
    del st.session_state.log[100:]


def request_line():
    req = st.session_state.get("last_req")
    if req:
        m, p, code, err = req
        st.markdown(
            f'<div class="req"><span class="m {m}">{m}</span><span>{esc(p)}</span>'
            f'<span class="c {"err" if err else ""}">{esc(code)}</span></div>',
            unsafe_allow_html=True,
        )


def validate(v: dict, *, editing: bool) -> dict:
    """Mirror the Pydantic rules so the user sees problems before sending."""
    e = {}
    if not editing and not v["id"].strip():
        e["id"] = "ID is required."
    name = v["name"].strip()
    if not 2 <= len(name) <= 50:
        e["name"] = "Name must be 2–50 characters."
    elif not name.replace(" ", "").isalpha():
        e["name"] = "Name must contain only letters and spaces."
    if not EMAIL_RE.match(v["email"].strip()):
        e["email"] = "Enter a valid email address."
    if not v["course"].strip():
        e["course"] = "Course is required."
    elif len(v["course"]) > 50:
        e["course"] = "Course must be 50 characters or fewer."
    return e


def field_error(errors: dict, key: str):
    if key in errors:
        st.markdown(f'<div class="ferr">{esc(errors[key])}</div>', unsafe_allow_html=True)


def flash(msg: str, icon: str = "✅"):
    st.session_state.flash = (msg, icon)


# ═══════════════════════════════ Session state ═══════════════════════════════
for k, v in {"api_base": "http://127.0.0.1:8000", "last_req": None, "log": [], "page": 1,
             "focus_id": None, "view_sig": None}.items():
    st.session_state.setdefault(k, v)

if f := st.session_state.pop("flash", None):
    st.toast(f[0], icon=f[1])

# ═══════════════════════════════ Load data ═══════════════════════════════
try:
    all_students = to_rows(api("GET", "/student"))
    connected = True
except ApiError as e:
    all_students, connected, load_error = [], False, e.message

by_id = {s["id"]: s for s in all_students}
courses = sorted({s["course"] for s in all_students}, key=str.lower)
course_color = {c: COURSE_HUES[i % len(COURSE_HUES)] for i, c in enumerate(courses)}
n = len(all_students)
class_avg = sum(s["marks"] for s in all_students) / n if n else 0


def next_id() -> str:
    nums = [int(m[1]) for i in by_id if (m := re.fullmatch(r"S(\d+)", i))]
    return f"S{(max(nums) + 1 if nums else 1):03d}"


# ═══════════════════════════════ Dialogs ═══════════════════════════════
@st.dialog("Add a student", width="large")
def add_dialog():
    st.caption("Sends `POST /create`. Fields are checked as you type.")
    c1, c2 = st.columns([1, 2])
    sid = c1.text_input("Student ID", value=next_id())
    name = c2.text_input("Full name", placeholder="Letters and spaces only")
    email = st.text_input("Email", placeholder="name@example.com")
    course = st.selectbox("Course", courses, index=None, accept_new_options=True,
                          placeholder="Pick one or type a new course")
    c3, c4 = st.columns(2)
    age = c3.number_input("Age", min_value=1, max_value=100, value=20, step=1)
    marks = c4.slider("Marks", 0, 100, 75)

    g = grade_of(marks)
    st.markdown(f'<div class="preview">Grade will be {chip(g)} &nbsp;·&nbsp; '
                f'{marks - class_avg:+.1f} vs class average</div>', unsafe_allow_html=True)

    values = {"id": sid, "name": name, "email": email, "course": course or "", "age": age, "marks": marks}
    touched = bool(name or email or course)
    errors = validate(values, editing=False) if touched else {}
    if sid.strip() in by_id:
        errors["id"] = f"{sid.strip()} is already taken."
    for k in ("id", "name", "email", "course"):
        field_error(errors, k)

    b1, b2 = st.columns(2)
    if b1.button("Cancel", width="stretch"):
        st.rerun()
    if b2.button("Create student", type="primary", width="stretch", disabled=not touched or bool(errors)):
        payload = {k: (v.strip() if isinstance(v, str) else int(v)) for k, v in values.items()}
        try:
            res = api("POST", "/create", payload)
            st.session_state.focus_id = payload["id"]
            flash(f"Created {res['student']['name']} · grade {grade_of(res['student']['marks'])}")
            st.rerun()
        except ApiError as err:
            st.error(err.message)


@st.dialog("Edit student", width="large")
def edit_dialog(sid: str):
    cur = by_id[sid]
    st.caption(f"Only changed fields are sent to `PUT /update/{sid}`.")
    name = st.text_input("Full name", value=cur["name"], key=f"e_name_{sid}")
    email = st.text_input("Email", value=cur["email"], key=f"e_email_{sid}")
    course = st.selectbox("Course", courses, index=courses.index(cur["course"]) if cur["course"] in courses else None,
                          accept_new_options=True, key=f"e_course_{sid}")
    c1, c2 = st.columns(2)
    age = c1.number_input("Age", 1, 99, value=min(int(cur["age"]), 99), key=f"e_age_{sid}")
    marks = c2.slider("Marks", 0, 100, int(cur["marks"]), key=f"e_marks_{sid}")

    values = {"id": sid, "name": name.strip(), "email": email.strip(), "course": (course or "").strip(),
              "age": int(age), "marks": int(marks)}
    errors = validate(values, editing=True)
    for k in ("name", "email", "course"):
        field_error(errors, k)

    changes = {k: values[k] for k in ("name", "email", "course", "age", "marks") if values[k] != cur[k]}
    if changes:
        rows = "".join(f"<div>{k}: <s>{esc(cur[k])}</s> → <b>{esc(v)}</b></div>" for k, v in changes.items())
        if "marks" in changes and grade_of(changes["marks"]) != grade_of(cur["marks"]):
            rows += f"<div>grade: {chip(grade_of(cur['marks']))} → {chip(grade_of(changes['marks']))}</div>"
        st.markdown(f'<div class="diff">{rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="diff" style="color:var(--muted)">No changes yet.</div>', unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    if b1.button("Cancel", width="stretch", key=f"e_cancel_{sid}"):
        st.rerun()
    if b2.button("Save changes", type="primary", width="stretch", key=f"e_save_{sid}",
                 disabled=not changes or bool(errors)):
        try:
            res = api("PUT", f"/update/{requests.utils.quote(sid)}", changes)
            flash(f"Updated {res['student']['name']} ({', '.join(changes)})")
            st.rerun()
        except ApiError as err:
            st.error(err.message)


@st.dialog("Delete student?")
def delete_dialog(sid: str):
    s = by_id[sid]
    st.markdown(
        f"This permanently removes **{esc(s['name'])}** (`{sid}`) from `students.json`. "
        "There's no undo.", unsafe_allow_html=True,
    )
    confirm = st.text_input(f"Type **{sid}** to confirm", key=f"d_confirm_{sid}")
    b1, b2 = st.columns(2)
    if b1.button("Cancel", width="stretch", key=f"d_cancel_{sid}"):
        st.rerun()
    with b2, st.container(key="danger_zone"):
        go = st.button("Delete", type="primary", width="stretch", key=f"d_go_{sid}",
                       disabled=confirm.strip() != sid)
    if go:
        try:
            res = api("DELETE", f"/delete/{requests.utils.quote(sid)}")
            if st.session_state.focus_id == sid:
                st.session_state.focus_id = None
            flash(res.get("message", f"Deleted {sid}"), "🗑️")
            st.rerun()
        except ApiError as err:
            st.error(err.message)


# ═══════════════════════════════ Sidebar ═══════════════════════════════
with st.sidebar:
    st.markdown('<div class="side-h">Connection</div>', unsafe_allow_html=True)
    st.text_input("API base URL", key="api_base")
    st.markdown(
        f'<div class="status {"ok" if connected else "bad"}"><i></i>{"Connected" if connected else "Offline"}'
        f'{f" · {n} students" if connected else ""}</div>',
        unsafe_allow_html=True,
    )
    if st.button("↻  Refresh", width="stretch"):
        st.rerun()

    st.markdown('<div class="side-h" style="margin-top:22px">Quick find</div>', unsafe_allow_html=True)
    with st.form("quick_find", border=False, clear_on_submit=True):
        qid = st.text_input("Student ID", placeholder="S001", label_visibility="collapsed")
        if st.form_submit_button("Open profile", width="stretch") and qid.strip():
            try:
                api("GET", f"/student/{requests.utils.quote(qid.strip())}")
                st.session_state.focus_id = qid.strip()
            except ApiError as e:
                st.session_state.flash = (e.message, "⚠️")
            st.rerun()

    with st.expander("Endpoints used"):
        st.markdown(
            "`GET /student` · `GET /paginate`  \n`GET /filter` · `GET /sort`  \n`GET /student/{id}`  \n"
            "`POST /create`  \n`PUT /update/{id}`  \n`DELETE /delete/{id}`"
        )

# ═══════════════════════════════ Header ═══════════════════════════════
h1, h2 = st.columns([4, 1], vertical_alignment="bottom")
h1.markdown('<div class="reg-title">Student <em>Registry</em></div>'
            '<p class="reg-sub">A front desk for your FastAPI student records.</p>', unsafe_allow_html=True)
if h2.button("＋  New student", type="primary", width="stretch", disabled=not connected):
    add_dialog()

if not connected:
    st.error(load_error)
    st.info("Start the API with `uvicorn main:app --reload`, check the URL in the sidebar, then press **Refresh**.")
    st.stop()

# ═══════════════════════════════ Stat cards ═══════════════════════════════
if n:
    avg_age = sum(s["age"] for s in all_students) / n
    top = max(all_students, key=lambda s: s["marks"])
    counts = {g: 0 for g in GRADES}
    for s in all_students:
        counts[grade_of(s["marks"])] += 1
    spread = "".join(f'<span title="{g}: {c}" style="flex-grow:{c};background:{GRADE_COLORS[g]}"></span>'
                     for g, c in counts.items() if c)
    legend = "".join(f'<span><i style="background:{GRADE_COLORS[g]}"></i>{g} {c}</span>' for g, c in counts.items())
    passing = sum(1 for s in all_students if s["marks"] >= 60)
    st.markdown(
        f"""
<div class="stats">
  <div class="stat"><div class="stat-label">Students</div><div class="stat-value">{n}</div>
    <div class="stat-sub">across {len(courses)} course{"s" if len(courses) != 1 else ""} · avg age {avg_age:.1f}</div></div>
  <div class="stat"><div class="stat-label">Class average</div><div class="stat-value">{class_avg:.1f}</div>
    <div class="stat-sub">{passing} of {n} passing (60+)</div></div>
  <div class="stat"><div class="stat-label">Top scorer</div><div class="stat-value">{top["marks"]}</div>
    <div class="stat-sub">{esc(top["name"])} · {esc(top["course"])}</div></div>
  <div class="stat"><div class="stat-label">Grade spread</div><div class="spread">{spread}</div>
    <div class="legend">{legend}</div></div>
</div>""",
        unsafe_allow_html=True,
    )

tab_roster, tab_insights, tab_activity = st.tabs(["Roster", "Insights", "Activity"])

# ═══════════════════════════════ Roster ═══════════════════════════════
with tab_roster:
    t1, t2 = st.columns([3, 1])
    search = t1.text_input("Search", placeholder="🔍  Search by name, email or ID…", label_visibility="collapsed")
    limit = t2.selectbox("Rows per page", [5, 10, 20, 50], index=1, label_visibility="collapsed",
                         format_func=lambda x: f"{x} per page")

    course = st.pills("Course", courses, selection_mode="single", label_visibility="collapsed")

    f1, f2, f3 = st.columns([1.6, 1, 2])
    sort_label = f1.segmented_control("Sort by", ["Marks", "Name", "Age"], selection_mode="single")
    order_label = f2.segmented_control("Order", ["↑ Asc", "↓ Desc"], default="↑ Asc",
                                       disabled=sort_label is None)
    marks_range = f3.slider("Marks range", 0, 100, (0, 100))

    sort_by = sort_label.lower() if sort_label else None
    order = "desc" if order_label == "↓ Desc" else "asc"
    search = search.strip().lower()
    refine = bool(search) or marks_range != (0, 100)

    # Reset to page 1 whenever the view changes
    sig = (course, sort_by, order, search, marks_range, limit)
    if st.session_state.view_sig != sig:
        st.session_state.view_sig, st.session_state.page = sig, 1

    try:
        server_paged = False
        if course:                                  # GET /filter
            rows = to_rows(api("GET", f"/filter?course={requests.utils.quote(course)}"))
        elif sort_by:                               # GET /sort
            rows = to_rows(api("GET", f"/sort?sort_by={sort_by}&order={order}"))
        elif not refine:                            # GET /paginate
            pages = max(1, math.ceil(n / limit))
            st.session_state.page = min(st.session_state.page, pages)
            data = api("GET", f"/paginate?page={st.session_state.page}&limit={limit}")
            rows, total, server_paged = to_rows(data["students"]), data["total_students"], True
        else:                                       # search/slider only → everything from GET /student
            rows = list(all_students)

        if not server_paged:
            if search:
                rows = [r for r in rows if search in r["name"].lower() or search in r["email"].lower()
                        or search in r["id"].lower()]
            lo, hi = marks_range
            rows = [r for r in rows if lo <= r["marks"] <= hi]
            if sort_by and course:  # /filter doesn't sort, so sort here
                rows.sort(key=lambda r: r[sort_by], reverse=order == "desc")
            total = len(rows)
            pages = max(1, math.ceil(total / limit))
            st.session_state.page = min(st.session_state.page, pages)
            start = (st.session_state.page - 1) * limit
            rows = rows[start:start + limit]
    except ApiError as e:
        rows, total, pages = [], 0, 1
        st.error(e.message)

    pages = max(1, math.ceil(total / limit))
    request_line()

    left, right = st.columns([2.3, 1], gap="large")

    with left:
        selected_id = None
        if rows:
            df = pd.DataFrame(rows)
            df["grade"] = df["marks"].apply(grade_of)
            df = df[["id", "name", "course", "age", "marks", "grade", "email"]]
            event = st.dataframe(
                df,
                hide_index=True,
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
                key=f"roster_{hash(sig)}_{st.session_state.page}",
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("Name", width="medium"),
                    "course": st.column_config.TextColumn("Course"),
                    "age": st.column_config.NumberColumn("Age", width="small"),
                    "marks": st.column_config.ProgressColumn("Marks", min_value=0, max_value=100, format="%d"),
                    "grade": st.column_config.TextColumn("Grade", width="small"),
                    "email": st.column_config.TextColumn("Email"),
                },
            )
            picked = event.selection.rows
            if picked and picked[0] < len(df):
                selected_id = df.iloc[picked[0]]["id"]
                st.session_state.focus_id = selected_id
            st.markdown('<p class="hint">Click a row to open the student’s profile.</p>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-panel"><div class="eh">No matches</div>Try clearing the search, course or marks range.</div>',
                        unsafe_allow_html=True)

        # Pager
        p1, p2, p3 = st.columns([1, 2, 1])
        if p1.button("← Prev", width="stretch", disabled=st.session_state.page <= 1):
            st.session_state.page -= 1
            st.rerun()
        first = (st.session_state.page - 1) * limit + 1 if total else 0
        p2.markdown(f'<div class="pageinfo">{first}–{min(total, st.session_state.page * limit)} of {total}'
                    f' · page {st.session_state.page} of {pages}</div>', unsafe_allow_html=True)
        if p3.button("Next →", width="stretch", disabled=st.session_state.page >= pages):
            st.session_state.page += 1
            st.rerun()

    with right:
        fid = selected_id or st.session_state.focus_id
        s = by_id.get(fid) if fid else None
        if not s:
            st.markdown('<div class="empty-panel"><div class="eh">No one selected</div>Pick a row in the table, or use '
                        '<b>Quick find</b> in the sidebar.</div>', unsafe_allow_html=True)
        else:
            g = grade_of(s["marks"])
            color = GRADE_COLORS[g]
            rank = 1 + sum(1 for x in all_students if x["marks"] > s["marks"])
            in_course = [x for x in all_students if x["course"] == s["course"]]
            course_rank = 1 + sum(1 for x in in_course if x["marks"] > s["marks"])
            delta = s["marks"] - class_avg
            st.markdown(
                f"""
<div class="profile">
  <div class="pid mono">{esc(fid)}</div>
  <div class="pname">{esc(s["name"])}</div>
  <div class="ring-row">
    <div class="ring" style="background:conic-gradient({color} {s["marks"]}%, {P["line"]} 0)"><div>{s["marks"]}</div></div>
    <div class="ring-meta">{chip(g)}<br><b>#{rank}</b> of {n} overall<br><b>#{course_rank}</b> of {len(in_course)} in course</div>
  </div>
  <dl class="facts">
    <dt>Course</dt><dd><span class="course" style="--cc:{course_color.get(s["course"], "#999")}">{esc(s["course"])}</span></dd>
    <dt>Age</dt><dd>{s["age"]}</dd>
    <dt>Email</dt><dd><a href="mailto:{esc(s["email"])}">{esc(s["email"])}</a></dd>
  </dl>
  <div class="cmp">vs class average ({class_avg:.1f}): <b style="color:{'var(--accent)' if delta >= 0 else 'var(--danger)'}">{delta:+.1f}</b>
    <div class="cmp-bar"><div class="fill" style="width:{s["marks"]}%;background:{color}"></div>
      <div class="avg" style="left:calc({class_avg}% - 1px)" title="Class average"></div></div>
  </div>
</div>""",
                unsafe_allow_html=True,
            )
            st.write("")
            e1, e2 = st.columns(2)
            if e1.button("Edit", width="stretch", key="panel_edit"):
                edit_dialog(fid)
            if e2.button("Delete", width="stretch", key="panel_delete"):
                delete_dialog(fid)

# ═══════════════════════════════ Insights ═══════════════════════════════
with tab_insights:
    if not n:
        st.info("Add some students to see insights.")
    else:
        df_all = pd.DataFrame(all_students)
        df_all["grade"] = df_all["marks"].apply(grade_of)
        course_scale = alt.Scale(domain=courses, range=[course_color[c] for c in courses])
        grade_scale = alt.Scale(domain=GRADES, range=[GRADE_COLORS[g] for g in GRADES])

        def style(chart):
            return (chart.configure_view(strokeWidth=0)
                    .configure_axis(labelColor=P["muted"], titleColor=P["muted"], gridColor=P["grid"],
                                    domainColor=P["line"], tickColor=P["line"], labelFont="Geist", titleFont="Geist",
                                    titleFontWeight=500)
                    .configure_legend(labelColor=P["ink2"], titleColor=P["muted"], labelFont="Geist", titleFont="Geist"))

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown('<p class="chart-title">Average marks by course</p>'
                        '<p class="chart-sub">Hover a bar for details. The line is the class average.</p>',
                        unsafe_allow_html=True)
            hover = alt.selection_point(on="mouseover", fields=["course"], empty=False)
            bars = alt.Chart(df_all).mark_bar(cornerRadiusEnd=5, size=22).encode(
                y=alt.Y("course:N", sort="-x", title=None),
                x=alt.X("mean(marks):Q", title="Average marks", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("course:N", scale=course_scale, legend=None),
                opacity=alt.condition(hover, alt.value(1), alt.value(0.75)),
                tooltip=[alt.Tooltip("course:N", title="Course"),
                         alt.Tooltip("mean(marks):Q", title="Average", format=".1f"),
                         alt.Tooltip("max(marks):Q", title="Best"),
                         alt.Tooltip("count():Q", title="Students")],
            ).add_params(hover)
            rule = alt.Chart(pd.DataFrame({"avg": [class_avg]})).mark_rule(
                color=P["ink"], strokeDash=[4, 3]).encode(x="avg:Q")
            st.altair_chart(style((bars + rule).properties(height=max(220, 46 * len(courses)), background="transparent")), theme=None)

        with c2:
            st.markdown('<p class="chart-title">Grade distribution</p>'
                        '<p class="chart-sub">How many students fall in each grade band.</p>',
                        unsafe_allow_html=True)
            gd = (df_all.groupby("grade").size().reindex(GRADES, fill_value=0)
                  .rename("students").reset_index())
            grade_chart = alt.Chart(gd).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=38).encode(
                x=alt.X("grade:N", sort=GRADES, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("students:Q", title="Students", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color("grade:N", scale=grade_scale, legend=None),
                tooltip=[alt.Tooltip("grade:N", title="Grade"), alt.Tooltip("students:Q", title="Students")],
            )
            labels = grade_chart.mark_text(dy=-8, color=P["ink2"], font="Geist").encode(text="students:Q")
            st.altair_chart(style((grade_chart + labels).properties(height=max(220, 46 * len(courses)), background="transparent")), theme=None)

        st.markdown('<p class="chart-title" style="margin-top:18px">Age vs marks</p>'
                    '<p class="chart-sub">Click a course in the legend to highlight it. Scroll to zoom, drag to pan.</p>',
                    unsafe_allow_html=True)
        pick = alt.selection_point(fields=["course"], bind="legend")
        scatter = alt.Chart(df_all).mark_circle(size=160, stroke=P["surface"], strokeWidth=1.5).encode(
            x=alt.X("age:Q", title="Age", scale=alt.Scale(zero=False, padding=12)),
            y=alt.Y("marks:Q", title="Marks", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("course:N", scale=course_scale, title="Course"),
            opacity=alt.condition(pick, alt.value(0.95), alt.value(0.12)),
            tooltip=[alt.Tooltip("name:N", title="Name"), alt.Tooltip("id:N", title="ID"),
                     alt.Tooltip("course:N", title="Course"), alt.Tooltip("age:Q", title="Age"),
                     alt.Tooltip("marks:Q", title="Marks"), alt.Tooltip("grade:N", title="Grade")],
        ).add_params(pick).interactive()
        pass_line = alt.Chart(pd.DataFrame({"y": [60]})).mark_rule(color=P["danger"], strokeDash=[4, 3], opacity=.6).encode(y="y:Q")
        st.altair_chart(style((scatter + pass_line).properties(height=340, background="transparent")), theme=None)

# ═══════════════════════════════ Activity ═══════════════════════════════
with tab_activity:
    a1, a2, a3 = st.columns([3, 1, 1], vertical_alignment="bottom")
    a1.markdown('<p class="chart-title">API activity</p>'
                '<p class="chart-sub">Every request this app made to your FastAPI server, newest first.</p>',
                unsafe_allow_html=True)
    if n:
        n = len(all_students)
        export = pd.DataFrame(all_students)
        export["grade"] = export["marks"].apply(grade_of)
        a2.download_button("⬇  Export CSV", export.to_csv(index=False), "students.csv", "text/csv", width="stretch")
    if a3.button("Clear log", width="stretch"):
        st.session_state.log = []
        st.rerun()

    if st.session_state.log:
        log = pd.DataFrame(st.session_state.log)
        log["ok"] = log["status"].apply(lambda s: isinstance(s, int) and s < 400)
        log["status"] = log["status"].astype(str)  # mixes ints and "—"; keep one type for Arrow
        st.dataframe(
            log[["time", "method", "path", "status", "ms", "ok"]],
            hide_index=True,
            width="stretch",
            column_config={
                "time": st.column_config.TextColumn("Time", width="small"),
                "method": st.column_config.TextColumn("Method", width="small"),
                "path": st.column_config.TextColumn("Path", width="large"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "ms": st.column_config.NumberColumn("ms", width="small"),
                "ok": st.column_config.CheckboxColumn("OK", width="small"),
            },
        )
    else:
        st.caption("No requests yet.")