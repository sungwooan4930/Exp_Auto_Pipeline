from pipeline.config import Config
from pipeline.llm import LLMClient

SYSTEM = "You are a research experiment designer. Write clear, reproducible experiment plans in Markdown."

PROMPT_TEMPLATE = """Design a complete experiment plan to test the following research hypotheses.

Hypotheses:
{hypotheses_text}

Write a Markdown document with EXACTLY these 5 sections (use these exact headings):
## 1. Research Overview
## 2. Variables
## 3. Methodology
## 4. Evaluation Metrics
## 5. Expected Results

Requirements:
- Section 2: List all independent and dependent variables with operational definitions
- Section 3: Describe dataset selection, baseline models, experimental conditions, and procedure step-by-step
- Section 4: Define each metric with formula or measurement method
- Section 5: State predicted outcomes for each hypothesis

A third party should be able to replicate the experiment from this document alone."""


def design_experiment(hypotheses: list[dict], llm: LLMClient, config: Config) -> str:
    hypotheses_text = "\n\n".join(
        f"[{h['hypothesis_id']}] {h['hypothesis']}\n"
        f"  Independent: {h['independent_var']}\n"
        f"  Dependent: {h['dependent_var']}\n"
        f"  Expected: {h['expected_relation']}"
        for h in hypotheses
    )
    prompt = PROMPT_TEMPLATE.format(hypotheses_text=hypotheses_text)
    return llm.complete(prompt, system=SYSTEM)
