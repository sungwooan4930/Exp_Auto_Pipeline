import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

# ── 상수 ──────────────────────────────────────────────
STAGES = ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]
STAGE_LABELS = {
    "s1": "S1 쿼리생성",
    "s2": "S2 논문수집",
    "s3": "S3 문헌선별",
    "s4": "S4 갭분석",
    "s5": "S5 가설도출",
    "s6": "S6 실험설계",
    "s7": "S7 메트릭",
}
OUTPUT_FILES = {
    "s1": "search_queries.json",
    "s2": "collected_papers.bib",
    "s3": "screening_results.json",
    "s4": "gap_analysis.json",
    "s5": "hypotheses.json",
    "s6": "experiment_design.md",
    "s7": "weekly_metrics.json",
}
STATUS_COLOR = {
    "pending": "⬜",
    "running": "🟡",
    "done": "✅",
    "error": "❌",
}

# ── 상태 초기화 ────────────────────────────────────────
def init_state():
    if "run_id" not in st.session_state:
        st.session_state.run_id = None
    if "stage_status" not in st.session_state:
        st.session_state.stage_status = {s: "pending" for s in STAGES}
    if "log_lines" not in st.session_state:
        st.session_state.log_lines = []

init_state()
st.set_page_config(page_title="RAP Pipeline", layout="wide")
st.title("RAP — Research Automation Pipeline")
