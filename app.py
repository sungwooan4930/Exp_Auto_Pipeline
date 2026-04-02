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

st.set_page_config(page_title="RAP Pipeline", layout="wide")
init_state()
st.title("RAP — Research Automation Pipeline")

# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 실행 설정")

    domain = st.text_input("연구 도메인", key="domain", placeholder="예: LLM-based autonomous agents")

    run_all = st.button("▶ 전체 실행", type="primary", use_container_width=True)

    st.divider()
    st.subheader("단계별 재실행")
    st.caption("기존 실행 폴더를 선택 후 단계를 클릭하세요.")

    # 이전 실행 목록
    outputs_dir = Path(__file__).parent / "outputs"
    existing_runs = sorted(
        [d.name for d in outputs_dir.iterdir() if d.is_dir()],
        reverse=True,
    ) if outputs_dir.exists() else []

    selected_run = st.selectbox(
        "실행 폴더 선택",
        options=["(새 실행)"] + existing_runs,
        index=0,
    )

    # 단계별 버튼 (3열 배치)
    stage_cols = st.columns(3)
    stage_buttons = {}
    for i, stage in enumerate(STAGES):
        with stage_cols[i % 3]:
            stage_buttons[stage] = st.button(
                STAGE_LABELS[stage].split(" ")[0],  # "S1", "S2", ...
                use_container_width=True,
                disabled=(selected_run == "(새 실행)"),
            )

# ── 메인 영역: 단계 카드 ───────────────────────────────
def render_stage_cards():
    cols = st.columns(4)
    for i, stage in enumerate(STAGES):
        status = st.session_state.stage_status[stage]
        icon = STATUS_COLOR[status]
        label = STAGE_LABELS[stage]
        with cols[i % 4]:
            st.metric(label=f"{icon} {label}", value=status)

render_stage_cards()
st.divider()

# ── 실행 로직 ──────────────────────────────────────────
STAGE_LOG_MARKERS = {
    "Stage 1:": "s1",
    "Stage 2:": "s2",
    "Stage 3:": "s3",
    "Stage 4:": "s4",
    "Stage 5:": "s5",
    "Stage 6:": "s6",
    "Stage 7:": "s7",
}


def _parse_stage_from_line(line: str) -> str | None:
    for marker, stage in STAGE_LOG_MARKERS.items():
        if marker in line:
            return stage
    return None


def run_subprocess(cmd: list[str], from_stage_num: int):
    """subprocess 실행, stdout 실시간 파싱 → stage_status + log_lines 업데이트."""
    st.session_state.log_lines = []
    for s in STAGES:
        snum = int(s[1])
        if snum >= from_stage_num:
            st.session_state.stage_status[s] = "pending"

    log_box = st.empty()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    current_stage = None
    for line in proc.stdout:
        line = line.rstrip()
        st.session_state.log_lines.append(line)

        detected = _parse_stage_from_line(line)
        if detected:
            if current_stage:
                st.session_state.stage_status[current_stage] = "done"
            current_stage = detected
            st.session_state.stage_status[current_stage] = "running"

        if "Pipeline complete." in line:
            if current_stage:
                st.session_state.stage_status[current_stage] = "done"

        log_box.code("\n".join(st.session_state.log_lines[-50:]), language="")

    proc.wait()
    if proc.returncode != 0 and current_stage:
        st.session_state.stage_status[current_stage] = "error"

# ── 실행 트리거 ────────────────────────────────────────
if run_all:
    if not st.session_state.get("domain", "").strip():
        st.sidebar.error("도메인을 입력하세요.")
    else:
        st.session_state.stage_status = {s: "pending" for s in STAGES}
        cmd = [sys.executable, "run_pipeline.py", "--domain", st.session_state.domain.strip()]
        run_subprocess(cmd, from_stage_num=1)
        # 완료 후 가장 최신 outputs 폴더를 run_id로 설정
        outputs_dir = Path(__file__).parent / "outputs"
        if outputs_dir.exists():
            runs = sorted([d.name for d in outputs_dir.iterdir() if d.is_dir()])
            if runs:
                st.session_state.run_id = runs[-1]
        st.rerun()

for stage, clicked in stage_buttons.items():
    if clicked:
        stage_num = int(stage[1])
        run_dir = Path(__file__).parent / "outputs" / selected_run
        cmd = [
            sys.executable, "run_stage.py",
            "--stage", str(stage_num),
            "--input", str(run_dir),
        ]
        run_subprocess(cmd, from_stage_num=stage_num)
        st.session_state.run_id = selected_run
        st.rerun()
