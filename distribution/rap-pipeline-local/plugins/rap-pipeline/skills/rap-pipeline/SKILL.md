---
name: rap-pipeline
description: Global entrypoint for the RAP research automation pipeline. Use when the user says "rap-pipeline 시작", "rap-pipeline 연구 서치 시작", "rap-pipeline gap 가설 단계 시작", "rap-pipeline 실험 설계 시작", "rap-pipeline 시뮬레이션 시작", or "rap-pipeline 상태 업데이트". This skill reads the local RAP project files in the current repository and routes work to the right stage.
---

# RAP Pipeline

Use this skill as the single entrypoint for the RAP workflow.

## Missing Project Files Rule

If the current directory does not have `RAP_PROJECT_PROFILE.json`, treat that as a normal bootstrap case, not as a plugin failure.

- Do not speculate that the Claude Code plugin system is unsupported or broken.
- Do not say the plugin failed to load if this skill is already active.
- Explain that the current directory is not yet an initialized RAP project.
- Offer only these two next steps:
  1. move to an existing RAP project directory
  2. initialize a new RAP project here from the templates

If local RAP files exist but still contain placeholder values such as `replace_with_project_name`, `replace_with_research_domain`, or other obvious template markers:

- Do not say "project confirmed".
- Do not summarize the placeholder topic as if it were the real project.
- Explain that the RAP scaffold exists but still needs real project values.

## Read First

Read these files when they exist in the current repository:

1. `RAP_PROJECT_PROFILE.json`
2. `run_logging.md`
3. `references/PROJECT_GUIDE.md`
4. `references/PIPELINE_START.md`
5. `references/rap-workflow.md`

If the repository does not have `RAP_PROJECT_PROFILE.json`, scaffold the local project files from:

- `templates/RAP_PROJECT_PROFILE.template.json`
- `templates/search_cycle_input.template.json`
- `templates/run_logging.template.md`

## Invocation Rules

If the user says `rap-pipeline 시작`, do not start work immediately.

For this exact invocation:

- Do not infer the stage from `search_cycle_input.json`.
- Do not infer the stage from the project topic.
- Do not begin literature search automatically.
- Always ask which stage to start from first.

Present exactly these options:

1. `연구 서치 시작`
2. `gap 가설 단계 시작`
3. `실험 설계 시작`
4. `시뮬레이션 시작`
5. `상태 업데이트`

If the user already named a stage, skip the question and start that stage.

Only after the user chooses `연구 서치 시작` should you read `search_cycle_input.json`.

## Stage Routing

- For `연구 서치 시작`, read `skills/rap-search-cycle/SKILL.md`.
- For `gap 가설 단계 시작`, read `skills/rap-gap-hypothesis-cycle/SKILL.md`.
- For `실험 설계 시작`, read `skills/rap-experiment-design/SKILL.md`.
- For `시뮬레이션 시작`, read `skills/rap-simulation-prediction/SKILL.md`.
- For `상태 업데이트`, read `skills/rap-metrics-tracking/SKILL.md`.

## Required Project Rules

- Treat `RAP_PROJECT_PROFILE.json` as the local project contract.
- Store stage input and output as normalized JSON files.
- Keep the approval loops explicit:
  - search loop until researcher approval
  - gap and hypothesis loop until researcher approval
  - simulation failure may send the workflow back to gap and hypothesis or experiment design
- Update `run_logging.md` after meaningful progress, blocker changes, or workflow state changes.
