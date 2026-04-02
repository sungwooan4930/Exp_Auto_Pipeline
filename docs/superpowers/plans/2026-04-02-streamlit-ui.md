# Streamlit UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** RAP 파이프라인을 브라우저에서 실행할 수 있는 단일 페이지 Streamlit 앱(`app.py`)을 구축한다.

**Architecture:** 단일 `app.py`. 사이드바에서 도메인 입력 및 실행 제어, 메인 영역에서 단계 상태 카드 + 실시간 로그 + 산출물 미리보기/다운로드를 제공한다. `subprocess.Popen`으로 기존 `run_pipeline.py` / `run_stage.py`를 호출하고, stdout을 파싱해 단계 상태를 업데이트한다.

**Tech Stack:** Python 3.11+, streamlit>=1.35.0, subprocess (표준 라이브러리)

---

## File Map

| 파일 | 역할 |
|------|------|
| `app.py` | Streamlit 앱 전체 (신규) |
| `requirements.txt` | streamlit 의존성 추가 (수정) |

---

## Task 1: requirements.txt에 streamlit 추가

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: streamlit 라인 추가**

`requirements.txt` 마지막에 추가:
```
streamlit>=1.35.0
```

- [ ] **Step 2: 설치 확인**

```bash
pip install -r requirements.txt
python -c "import streamlit; print(streamlit.__version__)"
```

Expected: 버전 번호 출력 (예: `1.35.0`)

- [ ] **Step 3: 커밋**

```bash
git add requirements.txt
git commit -m "chore: add streamlit dependency"
```

---

## Task 2: 앱 기본 골격 + 상태 초기화

**Files:**
- Create: `app.py`

- [ ] **Step 1: app.py 기본 골격 작성**

```python
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
```

- [ ] **Step 2: 앱 실행 확인**

```bash
streamlit run app.py
```

Expected: 브라우저에서 "RAP — Research Automation Pipeline" 제목이 표시됨.

- [ ] **Step 3: 커밋**

```bash
git add app.py
git commit -m "feat: add streamlit app skeleton with state init"
```

---

## Task 3: 사이드바 구현

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 사이드바 코드 추가 (`init_state()` 호출 아래)**

```python
# ── 사이드바 ───────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 실행 설정")

    domain = st.text_input("연구 도메인", placeholder="예: LLM-based autonomous agents")

    run_all = st.button("▶ 전체 실행", type="primary", use_container_width=True)

    st.divider()
    st.subheader("단계별 재실행")
    st.caption("기존 실행 폴더를 선택 후 단계를 클릭하세요.")

    # 이전 실행 목록
    outputs_dir = Path("outputs")
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
```

- [ ] **Step 2: 확인**

```bash
streamlit run app.py
```

Expected: 사이드바에 도메인 입력창, "▶ 전체 실행" 버튼, 단계 버튼 7개 표시됨.

- [ ] **Step 3: 커밋**

```bash
git add app.py
git commit -m "feat: add sidebar with domain input and stage buttons"
```

---

## Task 4: 단계 상태 카드 구현

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 단계 카드 렌더링 함수 추가 (사이드바 코드 아래)**

```python
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
```

- [ ] **Step 2: 확인**

```bash
streamlit run app.py
```

Expected: 메인 영역에 S1~S7 카드가 4열로 표시되고 모두 "⬜ pending" 상태.

- [ ] **Step 3: 커밋**

```bash
git add app.py
git commit -m "feat: add stage status cards"
```

---

## Task 5: subprocess 실행 + 로그 스트리밍

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 로그 파싱 및 상태 업데이트 함수 추가 (카드 코드 아래)**

```python
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
```

- [ ] **Step 2: 실행 트리거 코드 추가 (run_subprocess 함수 아래)**

```python
# ── 실행 트리거 ────────────────────────────────────────
if run_all:
    if not domain.strip():
        st.sidebar.error("도메인을 입력하세요.")
    else:
        st.session_state.stage_status = {s: "pending" for s in STAGES}
        cmd = [sys.executable, "run_pipeline.py", "--domain", domain.strip()]
        run_subprocess(cmd, from_stage_num=1)
        # 완료 후 가장 최신 outputs 폴더를 run_id로 설정
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            runs = sorted([d.name for d in outputs_dir.iterdir() if d.is_dir()])
            if runs:
                st.session_state.run_id = runs[-1]
        st.rerun()

for stage, clicked in stage_buttons.items():
    if clicked:
        stage_num = int(stage[1])
        run_dir = Path("outputs") / selected_run
        cmd = [
            sys.executable, "run_stage.py",
            "--stage", str(stage_num),
            "--input", str(run_dir),
        ]
        run_subprocess(cmd, from_stage_num=stage_num)
        st.session_state.run_id = selected_run
        st.rerun()
```

- [ ] **Step 3: 전체 실행 smoke test**

터미널에서:
```bash
streamlit run app.py
```
브라우저에서 도메인 입력 후 "▶ 전체 실행" 클릭.

Expected:
- 로그 박스에 실시간 텍스트 출력
- 단계 카드 색상이 running(🟡) → done(✅)으로 순차 변경
- 완료 후 `outputs/YYYY-MM-DD_HHMMSS/` 폴더 생성됨

- [ ] **Step 4: 커밋**

```bash
git add app.py
git commit -m "feat: add subprocess execution and real-time log streaming"
```

---

## Task 6: 산출물 미리보기 + 다운로드

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 산출물 렌더링 함수 추가 (실행 트리거 코드 아래)**

```python
# ── 산출물 표시 ────────────────────────────────────────
def render_outputs(run_dir: Path):
    st.subheader("📄 산출물")

    # S1: search_queries.json
    f = run_dir / "search_queries.json"
    if f.exists():
        with st.expander("S1 — search_queries.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="search_queries.json")

    # S2: collected_papers.bib
    f = run_dir / "collected_papers.bib"
    if f.exists():
        with st.expander("S2 — collected_papers.bib", expanded=False):
            text = f.read_text(encoding="utf-8")
            st.text_area("BibTeX", text, height=200, disabled=True)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="collected_papers.bib")

    # S3: screening_results.json
    f = run_dir / "screening_results.json"
    if f.exists():
        with st.expander("S3 — screening_results.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.dataframe(data, use_container_width=True)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="screening_results.json")

    # S4: gap_analysis.json
    f = run_dir / "gap_analysis.json"
    if f.exists():
        with st.expander("S4 — gap_analysis.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.json(data)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="gap_analysis.json")

    # S5: hypotheses.json
    f = run_dir / "hypotheses.json"
    if f.exists():
        with st.expander("S5 — hypotheses.json", expanded=False):
            data = json.loads(f.read_text(encoding="utf-8"))
            st.dataframe(data, use_container_width=True)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="hypotheses.json")

    # S6: experiment_design.md
    f = run_dir / "experiment_design.md"
    if f.exists():
        with st.expander("S6 — experiment_design.md", expanded=False):
            md_text = f.read_text(encoding="utf-8")
            st.markdown(md_text)
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="experiment_design.md")

    # S7: weekly_metrics.json
    f = run_dir / "weekly_metrics.json"
    if f.exists():
        with st.expander("S7 — weekly_metrics.json", expanded=True):
            metrics = json.loads(f.read_text(encoding="utf-8"))
            cols = st.columns(5)
            cols[0].metric("수집 논문", metrics.get("collected", "-"))
            cols[1].metric("선별 논문", metrics.get("screened", "-"))
            cols[2].metric("선별율", f"{metrics.get('screen_rate', 0):.0%}")
            cols[3].metric("갭 수", metrics.get("gaps", "-"))
            cols[4].metric("가설 수", metrics.get("hypotheses", "-"))
            st.download_button("⬇ 다운로드", f.read_bytes(), file_name="weekly_metrics.json")
```

- [ ] **Step 2: 산출물 렌더링 호출 추가 (파일 맨 아래)**

```python
# 현재 run_id 결정: 전체 실행 완료 후 또는 이전 실행 선택 시
active_run_id = st.session_state.run_id
if selected_run != "(새 실행)":
    active_run_id = selected_run

if active_run_id:
    render_outputs(Path("outputs") / active_run_id)
```

- [ ] **Step 3: 확인**

```bash
streamlit run app.py
```

Expected:
- 이전 실행 폴더 선택 시 산출물 섹션에 각 파일의 expander가 표시됨
- `weekly_metrics.json`은 기본 expanded 상태로 수치 카드 표시
- 각 expander에 "⬇ 다운로드" 버튼 존재

- [ ] **Step 4: 커밋**

```bash
git add app.py
git commit -m "feat: add output preview and download buttons"
```

---

## Task 7: 전체 통합 확인

**Files:**
- 없음 (기존 파일 검증만)

- [ ] **Step 1: 전체 실행 흐름 확인**

```bash
streamlit run app.py
```

체크리스트:
1. 도메인 입력 후 "▶ 전체 실행" → 로그 스트리밍 시작
2. S1→S7 단계 카드가 순서대로 🟡→✅ 전환
3. 완료 후 산출물 섹션에 7개 expander 표시
4. `weekly_metrics.json` expander에 수치 메트릭 5개 표시
5. 각 파일 "⬇ 다운로드" 버튼 동작 확인

- [ ] **Step 2: 단계별 재실행 확인**

1. 사이드바 드롭다운에서 기존 실행 폴더 선택
2. "S4" 버튼 클릭 → S4부터 S7까지 재실행
3. S4~S7 카드가 pending → running → done 전환
4. 산출물 업데이트 확인

- [ ] **Step 3: 오류 케이스 확인**

도메인 비워두고 "▶ 전체 실행" 클릭.
Expected: 사이드바에 "도메인을 입력하세요." 에러 메시지 표시, 실행 없음.

- [ ] **Step 4: 최종 커밋**

```bash
git add app.py requirements.txt
git commit -m "feat: complete Streamlit UI for RAP pipeline"
```
