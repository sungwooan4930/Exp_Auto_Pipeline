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
    if proc.returncode != 0:
        if current_stage:
            st.session_state.stage_status[current_stage] = "error"
        # Also mark any stage still running/pending as error
        for s in STAGES:
            if st.session_state.stage_status[s] in ("running", "pending"):
                st.session_state.stage_status[s] = "error"

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

# ── 산출물 표시 ────────────────────────────────────────
def render_outputs(run_dir: Path):
    st.subheader("📄 산출물")

    # S1: search_queries.json
    f = run_dir / "search_queries.json"
    if f.exists():
        with st.expander("S1 — search_queries.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="search_queries.json", key="dl_s1")

    # S2: collected_papers.bib
    f = run_dir / "collected_papers.bib"
    if f.exists():
        with st.expander("S2 — collected_papers.bib", expanded=False):
            text = f.read_text(encoding="utf-8")
            st.text_area("BibTeX", text, height=200, disabled=True)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="collected_papers.bib", key="dl_s2")

    # S3: screening_results.json
    f = run_dir / "screening_results.json"
    if f.exists():
        with st.expander("S3 — screening_results.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            try:
                st.dataframe(data, use_container_width=True)
            except Exception:
                st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="screening_results.json", key="dl_s3")

    # S4: gap_analysis.json
    f = run_dir / "gap_analysis.json"
    if f.exists():
        with st.expander("S4 — gap_analysis.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="gap_analysis.json", key="dl_s4")

    # S5: hypotheses.json
    f = run_dir / "hypotheses.json"
    if f.exists():
        with st.expander("S5 — hypotheses.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            try:
                st.dataframe(data, use_container_width=True)
            except Exception:
                st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="hypotheses.json", key="dl_s5")

    # S6: experiment_design.md
    f = run_dir / "experiment_design.md"
    if f.exists():
        with st.expander("S6 — experiment_design.md", expanded=False):
            md_text = f.read_text(encoding="utf-8")
            st.markdown(md_text)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="experiment_design.md", key="dl_s6")

    # S7: weekly_metrics.json
    f = run_dir / "weekly_metrics.json"
    if f.exists():
        with st.expander("S7 — weekly_metrics.json", expanded=True):
            metrics = json.loads(f.read_text(encoding="utf-8"))
            cols = st.columns(5)
            cols[0].metric("수집 논문", metrics.get("collected", "-"))
            cols[1].metric("선별 논문", metrics.get("screened", "-"))
            cols[2].metric("선별율", f"{float(metrics.get('screen_rate', 0)):.0%}")
            cols[3].metric("갭 수", metrics.get("gaps", "-"))
            cols[4].metric("가설 수", metrics.get("hypotheses", "-"))
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="weekly_metrics.json", key="dl_s7")

# 현재 run_id 결정: 전체 실행 완료 후 또는 이전 실행 선택 시
active_run_id = st.session_state.run_id
if selected_run != "(새 실행)":
    active_run_id = selected_run

if active_run_id:
    render_outputs(Path(__file__).parent / "outputs" / active_run_id)
