# Path: offer-catcher/backend/main.py
"""Offer-Catcher API — FastAPI backend with language-aware AI reports."""
import json
import os
import re
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
import fitz  # PyMuPDF
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()  # loads .env from the project root (or any parent directory)

# ── Config (read from environment / .env) ────────────────────────────
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
MAX_CHARS = 3000

if not LLM_API_KEY:
    raise RuntimeError(
        "LLM_API_KEY is not set. "
        "Copy .env.example to .env and fill in your API key."
    )

LANG_INSTRUCTION = {
    "zh": "【重要】请务必使用简体中文输出完整报告，包括所有章节标题、段落和建议列表。",
    "en": "[Important] Please write the entire report in English, including all headings and recommendations.",
}

TENCENT_COLOR = "#0052D9"

# ── High-quality fallback jobs (used when Tencent Careers API is unreachable) ──
FALLBACK_JOBS: list[dict] = [
    {
        "id": 1001, "company": "腾讯", "color": TENCENT_COLOR,
        "title": "计算机视觉算法实习生 - 腾讯AI Lab",
        "location": "深圳 · 实习", "salary": "竞争性薪酬", "type": "实习",
        "tags": ["Python", "PyTorch", "OpenCV", "深度学习", "CUDA"],
        "description": (
            "参与计算机视觉算法研究与落地，涵盖目标检测、图像分割、多模态大模型等方向，"
            "与顶级研究团队共同推进 AIGC 技术演进。"
        ),
        "keywords": [
            "python", "pytorch", "opencv", "深度学习", "计算机视觉", "目标检测",
            "图像分割", "cuda", "tensorflow", "c++", "resnet", "transformer",
            "yolo", "多模态", "大模型", "算法", "机器学习", "图像处理",
        ],
    },
    {
        "id": 1002, "company": "腾讯", "color": TENCENT_COLOR,
        "title": "后台开发工程师（校招）- 微信事业群",
        "location": "上海 · 校招", "salary": "N+2 薪 + RSU", "type": "校招",
        "tags": ["C++", "Go", "Linux", "分布式系统", "MySQL"],
        "description": (
            "负责微信核心后台服务设计与开发，参与亿级用户消息传递、"
            "存储系统优化和高可用架构建设。"
        ),
        "keywords": [
            "c++", "golang", "linux", "分布式", "mysql", "redis", "kafka",
            "后台开发", "微服务", "rpc", "tcp", "网络编程", "高并发",
            "kubernetes", "docker", "系统设计", "数据库", "缓存", "消息队列",
        ],
    },
    {
        "id": 1003, "company": "腾讯", "color": TENCENT_COLOR,
        "title": "NLP算法工程师实习生 - 腾讯AI Lab",
        "location": "北京 · 实习", "salary": "竞争性薪酬", "type": "实习",
        "tags": ["Python", "PyTorch", "Transformer", "NLP", "大模型"],
        "description": (
            "参与大语言模型预训练、对齐微调（RLHF/DPO）及推理优化研究，"
            "推动 LLM 在腾讯产品中的落地应用。"
        ),
        "keywords": [
            "python", "pytorch", "nlp", "transformer", "bert", "gpt", "llm",
            "rlhf", "dpo", "大模型", "自然语言处理", "机器学习", "深度学习",
            "cuda", "deepspeed", "推理", "量化", "微调", "accelerate",
        ],
    },
    {
        "id": 1004, "company": "腾讯", "color": TENCENT_COLOR,
        "title": "Android客户端开发实习生 - 微信支付",
        "location": "深圳 · 实习", "salary": "竞争性薪酬", "type": "实习",
        "tags": ["Java", "Kotlin", "Android", "性能优化", "支付安全"],
        "description": (
            "参与微信支付 Android 端核心功能迭代，包括支付流程优化、"
            "安全模块强化及性能调优，服务数亿移动端用户。"
        ),
        "keywords": [
            "java", "kotlin", "android", "mobile", "支付", "安全", "性能优化",
            "okhttp", "room", "jetpack", "mvvm", "coroutine", "gradle",
            "jni", "c++", "ndk", "逆向", "加固", "app开发",
        ],
    },
    {
        "id": 1005, "company": "腾讯", "color": TENCENT_COLOR,
        "title": "前端开发工程师（校招）- 腾讯云",
        "location": "成都 · 校招", "salary": "N+2 薪 + RSU", "type": "校招",
        "tags": ["TypeScript", "React", "Vue", "Node.js", "WebGL"],
        "description": (
            "负责腾讯云控制台与 SaaS 产品前端研发，"
            "参与低代码平台、可视化大屏及 Web3D 引擎的架构设计。"
        ),
        "keywords": [
            "typescript", "javascript", "react", "vue", "node.js", "webpack",
            "vite", "webgl", "three.js", "前端开发", "css", "html", "性能优化",
            "微前端", "ssr", "next.js", "可视化", "d3", "echarts", "工程化",
        ],
    },
]

# Active job database — overwritten at startup by fetch_real_jobs()
JOBS: list[dict] = list(FALLBACK_JOBS)


# ── Tencent Careers API helpers ───────────────────────────────────────

# (tag_label, regex_pattern) pairs for extracting tech tags from raw text
_TAG_PATTERNS: list[tuple[str, str]] = [
    ("Python",      r"python"),
    ("C++",         r"c\+\+"),
    ("Java",        r"\bjava\b"),
    ("Go",          r"\bgolang\b|\bgo语言\b"),
    ("Kotlin",      r"\bkotlin\b"),
    ("Swift",       r"\bswift\b"),
    ("JavaScript",  r"\bjavascript\b|\bjs\b"),
    ("TypeScript",  r"\btypescript\b|\bts\b"),
    ("Rust",        r"\brust\b"),
    ("PyTorch",     r"pytorch"),
    ("TensorFlow",  r"tensorflow"),
    ("CUDA",        r"\bcuda\b"),
    ("OpenCV",      r"opencv"),
    ("深度学习",    r"深度学习"),
    ("机器学习",    r"机器学习"),
    ("计算机视觉",  r"计算机视觉"),
    ("NLP",         r"\bnlp\b|自然语言处理"),
    ("大模型",      r"大模型|\bllm\b"),
    ("Android",     r"\bandroid\b"),
    ("iOS",         r"\bios\b"),
    ("React",       r"\breact\b"),
    ("Vue",         r"\bvue\b"),
    ("Node.js",     r"\bnode\.?js\b"),
    ("Kubernetes",  r"kubernetes|k8s"),
    ("Docker",      r"\bdocker\b"),
    ("Redis",       r"\bredis\b"),
    ("MySQL",       r"\bmysql\b"),
    ("Linux",       r"\blinux\b"),
    ("Kafka",       r"\bkafka\b"),
    ("Spark",       r"\bspark\b"),
]

# Seed keywords used for matching resumes to Tencent jobs
_KEYWORD_SEEDS: list[str] = [
    "python", "java", "c++", "golang", "kotlin", "javascript", "typescript", "rust",
    "pytorch", "tensorflow", "cuda", "opencv", "深度学习", "机器学习", "计算机视觉",
    "自然语言处理", "大模型", "llm", "rlhf", "android", "ios", "react", "vue",
    "node.js", "kubernetes", "docker", "redis", "mysql", "linux", "kafka",
    "分布式", "微服务", "高并发", "算法", "数据结构", "后台开发", "前端开发",
    "移动开发", "安全", "逆向", "数据库", "云原生", "spark", "hadoop",
]


def _extract_tags(text: str, max_tags: int = 5) -> list[str]:
    low = text.lower()
    return [label for label, pat in _TAG_PATTERNS if re.search(pat, low, re.I)][:max_tags]


def _extract_keywords(text: str) -> list[str]:
    low = text.lower()
    return [kw for kw in _KEYWORD_SEEDS if kw.lower() in low]


def _parse_tencent_posts(posts: list[dict]) -> list[dict]:
    """Map raw Tencent API post objects to our internal job dict format."""
    result = []
    for i, post in enumerate(posts, start=1):
        full_text = " ".join([
            post.get("RecruitPostName", ""),
            post.get("Responsibility", ""),
            post.get("Requirement", ""),
        ])
        tags = _extract_tags(full_text) or ["技术岗位"]
        keywords = _extract_keywords(full_text) or ["python", "算法"]

        raw_desc = post.get("Responsibility", "")
        description = (raw_desc[:200].rstrip() + "…") if len(raw_desc) > 200 else raw_desc
        description = description or "参与腾讯核心业务研发与技术创新。"

        post_name: str = post.get("RecruitPostName", "未知职位")
        job_type = "实习" if "实习" in post_name else "校招"

        result.append({
            "id": post.get("RecruitPostId", 2000 + i),
            "company": "腾讯",
            "color": TENCENT_COLOR,
            "title": post_name,
            "location": f"{post.get('LocationName', '深圳')} · {post.get('BGName', '腾讯')}",
            "salary": "竞争性薪酬",
            "type": job_type,
            "tags": tags,
            "description": description,
            "keywords": keywords,
        })
    return result


async def fetch_real_jobs() -> list[dict]:
    """
    Fetch live campus/internship jobs from Tencent Careers API.
    Gracefully degrades to FALLBACK_JOBS on any network error or anti-scraping block.
    """
    queries = ["校园招聘", "实习生", "算法工程师"]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://careers.tencent.com/",
    }

    collected: list[dict] = []
    seen_ids: set = set()

    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            for keyword in queries:
                url = (
                    "https://careers.tencent.com/tencentcareer/api/post/Query"
                    f"?timestamp={int(time.time() * 1000)}"
                    f"&keyword={keyword}&pageIndex=1&pageSize=5"
                    "&language=zh-cn&area=cn"
                )
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    posts = resp.json().get("Data", {}).get("Posts") or []
                    for job in _parse_tencent_posts(posts):
                        if job["id"] not in seen_ids:
                            seen_ids.add(job["id"])
                            collected.append(job)
                except Exception as e:
                    print(f"[offer-catcher] Query '{keyword}' failed: {e!r} — skipping.")
                    continue

        if collected:
            print(f"[offer-catcher] Fetched {len(collected)} live jobs from Tencent Careers API.")
            return collected

        print("[offer-catcher] Tencent API returned no posts — using fallback data.")
        return list(FALLBACK_JOBS)

    except Exception as exc:
        print(f"[offer-catcher] Tencent API unreachable ({exc!r}) — using fallback data.")
        return list(FALLBACK_JOBS)


# ── App lifecycle ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_: FastAPI):
    global JOBS
    JOBS = await fetch_real_jobs()
    yield


# ── Scoring helpers ───────────────────────────────────────────────────

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "this", "that", "these", "those", "as", "if", "when",
    "where", "who", "which", "what", "how", "all", "any", "some", "than", "too", "very", "just",
    "also", "into", "about", "i", "you", "he", "she", "we", "they", "my", "your", "our", "their",
    "experience", "years", "skills", "role", "work", "using", "team", "job",
}


def tokenize(text: str) -> list[str]:
    text = re.sub(r"[^a-z0-9\s\+\#\.\/\-]", " ", text.lower())
    return [w for w in text.split() if len(w) > 1 and w not in STOPWORDS]


def score_job(tokens: list[str], job: dict) -> int:
    ts = set(tokens)
    hits = 0.0
    for kw in job["keywords"]:
        parts = kw.split()
        if (len(parts) == 1 and kw in ts) or (len(parts) > 1 and all(p in ts for p in parts)):
            hits += 1
    for tag in job["tags"]:
        if re.sub(r"[^a-z0-9]", "", tag.lower()) in ts:
            hits += 0.4
    return min(int(32 + hits / max(len(job["keywords"]), 1) * 62), 94)


def get_top_jobs(text: str, n: int = 3) -> list[dict]:
    tokens = tokenize(text)
    scored = [{**j, "score": score_job(tokens, j)} for j in JOBS]
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:n]


def extract_pdf_text(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def build_prompt(resume_text: str, jobs: list[dict], lang: str) -> str:
    instr = LANG_INSTRUCTION.get(lang, LANG_INSTRUCTION["zh"])
    job_list = "\n\n".join(
        f"Position {i+1}: {j['title']} at {j['company']} (Match: {j['score']}%)\n"
        f"Skills: {', '.join(j['tags'])}\nRole: {j['description']}"
        for i, j in enumerate(jobs)
    )
    return f"""{instr}

You are a world-class career coach with deep Big Tech hiring expertise. Analyze
this resume and the 3 matched positions, then write a "Resume-to-Job Matching
Diagnosis & Optimization Report."

=== RESUME (first {MAX_CHARS} chars) ===
{resume_text[:MAX_CHARS]}

=== TOP 3 POSITIONS ===
{job_list}

Write the report using these exact section headers:
## 🎯 Executive Summary
## 💪 Key Strengths Identified
## 🔍 Match Analysis by Role
## 🚀 Optimization Roadmap   (5 numbered, concrete steps)
## ⭐ Best-Fit Role Recommendation

Reference actual resume content, be encouraging but honest, ~400-600 words."""


async def stream_llm_report(resume_text: str, jobs: list[dict], lang: str) -> AsyncGenerator[str, None]:
    clean_api_key = LLM_API_KEY.strip()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {clean_api_key}",
    }
    payload = {
        "model": LLM_MODEL,
        "stream": True,
        "messages": [{"role": "user", "content": build_prompt(resume_text, jobs, lang)}],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    base_url = LLM_BASE_URL.rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", endpoint, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                raw = line[6:].strip()
                if raw == "[DONE]":
                    break
                try:
                    obj = json.loads(raw)
                    choices = obj.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue


# ── FastAPI app ───────────────────────────────────────────────────────

app = FastAPI(title="Offer-Catcher API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/match")
async def match_resume(
    file: UploadFile = File(...),
    accept_language: str = Header(default="zh-CN"),
):
    lang = "zh" if accept_language.lower().startswith("zh") else "en"

    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")
    try:
        resume_text = extract_pdf_text(raw)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {e}")
    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=422,
                            detail="PDF appears to be image-only. Use a text-based PDF.")

    matched = get_top_jobs(resume_text)

    async def event_stream():
        yield f"data: {json.dumps({'type': 'jobs', 'jobs': matched})}\n\n"
        try:
            async for chunk in stream_llm_report(resume_text, matched, lang):
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
