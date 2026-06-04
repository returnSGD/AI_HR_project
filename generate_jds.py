#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_jds.py — Batch pre-generate full_jd for all seed jobs.
Run from project root: python generate_jds.py
Processes BATCH_SIZE jobs per API call to minimise total round-trips.
Saves a checkpoint every 10 batches so it's safe to interrupt/resume.
"""
import asyncio, json, os, sys, io
from pathlib import Path

import httpx
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()
LLM_API_KEY  = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL    = os.getenv("LLM_MODEL",    "deepseek-chat")
SEED_PATH    = Path("backend/data/seed_jobs.json")
BATCH_SIZE   = 10   # jobs per API call

if not LLM_API_KEY:
    sys.exit("ERROR: LLM_API_KEY not set.")

_SYS = """\
You are a senior HR professional at a top-tier tech company.
For each job in the input JSON array, write a complete, professional job description in Chinese.

Output ONLY a valid JSON array of markdown strings, one per job, in the EXACT same order as input.
Each markdown string must contain exactly these four H2 sections:

## 岗位描述
[One overview sentence, then a numbered list of 5-6 specific responsibilities tailored to this role]

## 岗位要求
必须具备的：
[Numbered list of 3-5 hard technical requirements matching this job's actual tech stack]

有一定了解的：
[Numbered list of 2-3 nice-to-have skills]

## 加分项或注意事项
[Numbered list of 2 bonus items or important notes for candidates]

## 参加面试的城市
[City derived from the job's location field, add "远程面试可协商" where appropriate]

Strict rules:
- Output ONLY the JSON array — no prose, no markdown fences, no explanation
- Every element must be a single string; use \\n for line breaks inside the string
- Requirements must accurately reflect each job's specific tech stack, NOT be generic
"""


async def gen_batch(jobs: list[dict]) -> list[str]:
    payload = [
        {
            "id":          j["id"],
            "title":       j["title"],
            "company":     j["company"],
            "location":    j.get("location", ""),
            "type":        j.get("type", ""),
            "salary":      j.get("salary", ""),
            "tags":        j.get("tags", []),
            "description": j.get("description", ""),
        }
        for j in jobs
    ]
    user_msg = (
        f"Generate full JDs for these {len(jobs)} jobs:\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    async with httpx.AsyncClient(timeout=150.0) as client:
        resp = await client.post(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY.strip()}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       LLM_MODEL,
                "messages":    [
                    {"role": "system", "content": _SYS},
                    {"role": "user",   "content": user_msg},
                ],
                "max_tokens":  10000,
                "temperature": 0.5,
            },
        )
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:]).rsplit("```", 1)[0].strip()

    result: list[str] = json.loads(raw)
    if len(result) != len(jobs):
        raise ValueError(f"Got {len(result)} JDs for {len(jobs)} jobs")
    return result


async def main() -> None:
    with open(SEED_PATH, encoding="utf-8") as f:
        all_jobs: list[dict] = json.load(f)

    by_id  = {j["id"]: j for j in all_jobs}
    todo   = [j for j in all_jobs if not (j.get("full_jd") or "").strip()]
    have   = len(all_jobs) - len(todo)

    print(f"Total jobs: {len(all_jobs)}  |  Already have JD: {have}  |  To generate: {len(todo)}")

    if not todo:
        print("Nothing to do — all jobs already have full_jd.")
        return

    batches = [todo[i : i + BATCH_SIZE] for i in range(0, len(todo), BATCH_SIZE)]
    total   = len(batches)
    success = 0

    for idx, batch in enumerate(batches, 1):
        id_range = f"{batch[0]['id']}-{batch[-1]['id']}"
        print(f"[{idx:03d}/{total}] IDs {id_range} ({len(batch)} jobs) ... ", end="", flush=True)

        for attempt in range(3):
            try:
                jds = await gen_batch(batch)
                for job, jd in zip(batch, jds):
                    by_id[job["id"]]["full_jd"] = jd.strip()
                success += 1
                print("OK", flush=True)
                break
            except Exception as exc:
                if attempt < 2:
                    print(f"retry {attempt + 1} ... ", end="", flush=True)
                    await asyncio.sleep(5)
                else:
                    print(f"FAILED ({exc!r})", flush=True)

        # Checkpoint every 10 batches
        if idx % 10 == 0:
            ordered = sorted(by_id.values(), key=lambda x: x["id"])
            with open(SEED_PATH, "w", encoding="utf-8") as f:
                json.dump(ordered, f, ensure_ascii=False, indent=2)
            print(f"  >>> checkpoint saved ({idx}/{total})", flush=True)

        await asyncio.sleep(2.0)

    # Final save
    ordered = sorted(by_id.values(), key=lambda x: x["id"])
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

    print(f"\nFinished: {success}/{total} batches OK  |  file: {SEED_PATH.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
