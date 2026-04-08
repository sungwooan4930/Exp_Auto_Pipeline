from pipeline.config import Config
from pipeline.llm import LLMClient
from pipeline.prompts import load_prompt

_SYSTEM, _PROMPT_TEMPLATE = load_prompt("s6_experiment")


def design_experiment(hypotheses: list[dict], llm: LLMClient, config: Config) -> str:
    hypotheses_text = "\n\n".join(
        f"[{h['hypothesis_id']}] hypothesis: {h['hypothesis']}\n"
        f"  independent_var: {h['independent_var']}\n"
        f"  dependent_var: {h['dependent_var']}\n"
        f"  expected_relation: {h['expected_relation']}"
        for h in hypotheses
    )
    prompt = _PROMPT_TEMPLATE.format(hypotheses_text=hypotheses_text)
    return llm.complete(prompt, system=_SYSTEM)
