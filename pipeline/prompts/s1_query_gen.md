## System
You are a research assistant. Output ONLY valid JSON arrays, no explanation.

## Prompt
Generate {n_queries} diverse academic search queries for the research domain: "{domain}"

Rules:
- Each query should target a different angle (methods, benchmarks, applications, limitations)
- Queries should be suitable for Semantic Scholar and arXiv search
- Output ONLY a JSON array of strings, e.g. ["query1", "query2", ...]

Domain: {domain}
