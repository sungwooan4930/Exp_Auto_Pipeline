# Streamlit UI — 설계 문서

**날짜:** 2026-04-02
**상태:** 승인됨

---

## 1. 목표

RAP 파이프라인을 터미널 없이 브라우저에서 실행할 수 있는 단일 페이지 Streamlit 앱(`app.py`)을 구축한다.
전체 파이프라인 실행과 개별 단계 재실행을 모두 지원하며, 진행 상황과 산출물을 실시간으로 확인할 수 있다.

---

## 2. 파일 구조

```
Exp_Auto_Pipeline/
└── app.py      # Streamlit 앱 (신규)
```

기존 `run_pipeline.py`, `run_stage.py`는 수정하지 않는다. `app.py`가 subprocess로 호출한다.

---

## 3. 레이아웃

```
┌─────────────────────────────────────────────────────┐
│  사이드바                  메인 영역                  │
│  ─────────                ──────────────────────     │
│  📌 도메인 입력            [ S1 ][ S2 ][ S3 ]        │
│  ─────────                [ S4 ][ S5 ][ S6 ][ S7 ]  │
│  ▶ 전체 실행               (단계 상태 카드)            │
│  ─────────                ──────────────────────     │
│  단계별 재실행:            📋 실행 로그 (스트리밍)      │
│  [S1] [S2] [S3]           ──────────────────────     │
│  [S4] [S5] [S6] [S7]      📄 산출물 미리보기 + 다운로드│
│  ─────────                                           │
│  📁 이전 실행 선택                                    │
└─────────────────────────────────────────────────────┘
```

---

## 4. 단계 카드 상태

| 상태 | 색상 | 의미 |
|------|------|------|
| pending | ⬜ 회색 | 아직 실행 전 |
| running | 🟡 노란색 | 현재 실행 중 |
| done | ✅ 초록색 | 완료 |
| error | ❌ 빨간색 | 실패 |

---

## 5. 상태 관리

Streamlit `st.session_state`로 관리:

```python
st.session_state.run_id        # str: 현재 실행 타임스탬프 폴더명 (e.g. "2026-04-02_143022")
st.session_state.stage_status  # dict[str, str]: {"s1": "pending"|"running"|"done"|"error", ...}
st.session_state.log_lines     # list[str]: 실행 로그 라인 목록
```

---

## 6. 실행 흐름

### 전체 실행
1. 도메인 입력 확인
2. `run_id` 생성 (`YYYY-MM-DD_HHMMSS`)
3. `subprocess.Popen`으로 `run_pipeline.py --domain <domain>` 호출
4. stdout을 실시간 읽어 `log_lines`에 추가, `st.empty()`로 렌더링
5. 각 단계 시작/완료 시 `stage_status` 업데이트

### 단계별 재실행
1. 사이드바 드롭다운에서 기존 `run_id` 선택 (필수)
2. 해당 단계 버튼 클릭
3. `subprocess.Popen`으로 `run_stage.py --stage <N> --input outputs/<run_id>/` 호출
4. 동일하게 로그 스트리밍

---

## 7. 산출물 표시

각 단계 완료 후 메인 영역 하단에 순서대로 누적 표시:

| 파일 | Streamlit 위젯 |
|------|---------------|
| `search_queries.json` | `st.json()` |
| `collected_papers.bib` | `st.text_area()` (읽기 전용) |
| `screening_results.json` | `st.dataframe()` |
| `gap_analysis.json` | `st.json()` |
| `hypotheses.json` | `st.dataframe()` |
| `experiment_design.md` | `st.markdown()` |
| `weekly_metrics.json` | `st.metric()` (수치 강조) |

각 산출물 옆에 `st.download_button()` 배치.

### 이전 실행 불러오기
- 사이드바에서 `outputs/` 폴더를 스캔해 드롭다운 제공
- 선택 시 해당 폴더의 산출물 자동 로드 및 표시

---

## 8. 의존성 추가

```
streamlit>=1.35.0
```

`requirements.txt`에 추가.

---

## 9. 실행 방법

```bash
pip install streamlit
streamlit run app.py
```
