import asyncio
import json
import logging
import re
import httpx
from pipeline.config import Config

logger = logging.getLogger(__name__)

SS_API = "https://api.semanticscholar.org/graph/v1/paper/search"
ARXIV_API = "https://export.arxiv.org/api/query"


async def fetch_semantic_scholar(query: str, limit: int = 25, year_range: str = None) -> list[dict]:
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,abstract,authors,year,externalIds,citationCount,referenceCount"
    }
    if year_range:
        params["year"] = year_range
        
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SS_API, params=params)
        resp.raise_for_status()
        data = resp.json()
    papers = []
    for p in data.get("data", []):
        if not p: continue
        doi = (p.get("externalIds") or {}).get("DOI", "")
        papers.append({
            "paper_id": f"ss_{p.get('paperId', '')[:8]}",
            "full_paper_id": p.get("paperId"),
            "title": p.get("title", ""),
            "abstract": p.get("abstract", ""),
            "authors": [a["name"] for a in (p.get("authors") or [])],
            "year": p.get("year", 0),
            "doi": doi,
            "citation_count": p.get("citationCount", 0),
            "reference_count": p.get("referenceCount", 0),
            "source": "semantic_scholar"
        })
    return papers


async def fetch_citations(paper_id: str, limit: int = 10) -> list[dict]:
    """해당 논문을 인용한 논문들을 가져옵니다 (Forward Snowballing)"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    params = {"limit": limit, "fields": "citingPaper.paperId,citingPaper.title,citingPaper.abstract,citingPaper.authors,citingPaper.year,citingPaper.externalIds"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200: return []
        data = resp.json()
    
    papers = []
    for item in data.get("data", []):
        p = item.get("citingPaper")
        if not p: continue
        doi = (p.get("externalIds") or {}).get("DOI", "")
        papers.append({
            "paper_id": f"ss_{p.get('paperId', '')[:8]}",
            "full_paper_id": p.get("paperId"),
            "title": p.get("title", ""),
            "abstract": p.get("abstract", ""),
            "authors": [a["name"] for a in (p.get("authors") or [])],
            "year": p.get("year", 0),
            "doi": doi,
            "source": "snowball_citation"
        })
    return papers


async def fetch_references(paper_id: str, limit: int = 10) -> list[dict]:
    """해당 논문이 인용한 논문들을 가져옵니다 (Backward Snowballing)"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
    params = {"limit": limit, "fields": "citedPaper.paperId,citedPaper.title,citedPaper.abstract,citedPaper.authors,citedPaper.year,citedPaper.externalIds"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200: return []
        data = resp.json()
        
    papers = []
    for item in data.get("data", []):
        p = item.get("citedPaper")
        if not p: continue
        doi = (p.get("externalIds") or {}).get("DOI", "")
        papers.append({
            "paper_id": f"ss_{p.get('paperId', '')[:8]}",
            "full_paper_id": p.get("paperId"),
            "title": p.get("title", ""),
            "abstract": p.get("abstract", ""),
            "authors": [a["name"] for a in (p.get("authors") or [])],
            "year": p.get("year", 0),
            "doi": doi,
            "source": "snowball_reference"
        })
    return papers


async def fetch_arxiv(query: str, limit: int = 25) -> list[dict]:
    params = {"search_query": f"all:{query}", "start": 0, "max_results": limit}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
        text = resp.text
    papers = []
    entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
    for entry in entries:
        title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        abstract = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
        doi_match = re.search(r'<arxiv:doi>(.*?)</arxiv:doi>', entry)
        id_match = re.search(r'<id>(.*?)</id>', entry)
        authors = re.findall(r'<name>(.*?)</name>', entry)
        year_match = re.search(r'<published>(\d{4})', entry)
        arxiv_id = (id_match.group(1) if id_match else "").split("/")[-1]
        doi = doi_match.group(1).strip() if doi_match else f"arxiv:{arxiv_id}"
        papers.append({
            "paper_id": f"ax_{arxiv_id[:8]}",
            "title": (title.group(1) if title else "").strip(),
            "abstract": (abstract.group(1) if abstract else "").strip(),
            "authors": authors,
            "year": int(year_match.group(1)) if year_match else 0,
            "doi": doi,
            "source": "arxiv"
        })
    return papers


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen = {}
    for p in papers:
        doi = p.get("doi", "").strip().lower()
        if doi:
            key = doi
        else:
            # DOI 없으면 제목 정규화로 중복 판단
            key = re.sub(r'\s+', ' ', p.get("title", "").lower().strip())
        if key and key not in seen:
            seen[key] = p
    return list(seen.values())


def papers_to_bibtex(papers: list[dict]) -> str:
    lines = []
    for p in papers:
        key = re.sub(r'\W+', '', p.get("paper_id", "p"))
        authors = " and ".join(p.get("authors", ["Unknown"]))
        lines.append(f'@article{{{key},')
        lines.append(f'  title = {{{p.get("title", "")}}},')
        lines.append(f'  author = {{{authors}}},')
        lines.append(f'  year = {{{p.get("year", "")}}},')
        lines.append(f'  doi = {{{p.get("doi", "")}}},')
        lines.append(f'  abstract = {{{p.get("abstract", "")}}},')
        lines.append('}')
        lines.append('')
    return "\n".join(lines)


async def collect_papers(queries: list[str], config: Config) -> list[dict]:
    tasks = []
    # 쿼리당 수집 개수 결정
    per_query = max(5, config.target_papers // len(queries))
    for q in queries:
        tasks.append(fetch_semantic_scholar(q, per_query, year_range=config.year_range))
        tasks.append(fetch_arxiv(q, per_query))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_papers = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"API fetch failed: {r}")
        else:
            all_papers.extend(r)
            
    deduped = deduplicate_papers(all_papers)
    
    # Snowball Search 확장 (필요 시)
    if config.use_snowball and len(deduped) < config.target_papers * 1.5:
        logger.info("Performing Snowball Search expansion...")
        # 상위 5개 논문에 대해 인용/참조 추적
        seed_papers = sorted(deduped, key=lambda x: x.get("citation_count", 0), reverse=True)[:5]
        snowball_tasks = []
        for p in seed_papers:
            full_id = p.get("full_paper_id")
            if full_id:
                snowball_tasks.append(fetch_citations(full_id, limit=10))
                snowball_tasks.append(fetch_references(full_id, limit=10))
        
        snowball_results = await asyncio.gather(*snowball_tasks, return_exceptions=True)
        for r in snowball_results:
            if not isinstance(r, Exception):
                deduped.extend(r)
        
        deduped = deduplicate_papers(deduped)
        logger.info(f"  → Total papers after snowballing: {len(deduped)}")

    if len(deduped) < config.target_papers:
        logger.warning(f"Collected {len(deduped)} papers, target was {config.target_papers}")
        
    return deduped[:config.target_papers * 2]  # 좀 더 넉넉하게 반환하여 S3에서 거를 수 있게 함
