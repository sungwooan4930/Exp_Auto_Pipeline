# RAP Project Profile Schema

이 문서는 하이브리드 구조에서 프로젝트 로컬 프로필인 `RAP_PROJECT_PROFILE.json`의 역할을 설명한다.

## 목적

전역 또는 마켓플레이스에 설치된 `rap-pipeline` 코어 스킬이, 현재 저장소의 로컬 설정을 이해하기 위해 읽는 표준 파일이다.

## 핵심 필드

- `project_id`
  - 프로젝트 식별자
- `project_name`
  - 사람이 읽는 프로젝트 이름
- `pipeline_invocation_name`
  - 호출 이름. 기본값은 `rap-pipeline`
- `topic`
  - 현재 프로젝트의 연구 도메인과 키워드
- `researcher_preferences`
  - 연도 제한, 인간 승인 루프 우선 여부, 기본 데이터 모드 같은 선호 조건
- `artifact_paths`
  - 로컬 run log, search input, outputs 위치
- `json_contract`
  - 각 단계의 표준 JSON 파일 이름
- `core_skillpack`
  - 전역 코어 스킬 정보와 로컬 초안 위치

## 운영 규칙

- 프로젝트를 시작할 때는 `RAP_PROJECT_PROFILE.json`을 먼저 읽는다.
- 코어 스킬은 이 파일을 기준으로 로컬 입출력 파일을 찾는다.
- 프로젝트별 차이는 가급적 이 파일에서 해결한다.
- 공통 workflow와 단계 로직은 코어 스킬팩이 담당한다.
