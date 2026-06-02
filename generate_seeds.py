#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_seeds.py -- Batch-generate comprehensive job seed data via DeepSeek API.
Run from project root:  python generate_seeds.py
Generates 18 categories x 3 types x 20 jobs ~= 1080 new entries.
Saves incrementally after each batch so safe to interrupt and re-run.
"""
import asyncio
import sys, io
# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY  = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL    = os.getenv("LLM_MODEL",    "deepseek-chat")
SEED_PATH    = Path("backend/data/seed_jobs.json")

if not LLM_API_KEY:
    sys.exit("ERROR: LLM_API_KEY not set.")

# ── Job categories: (display_name, keyword_hints) ────────────────────────────
CATEGORIES: list[tuple[str, str]] = [
    ("AI算法/大模型",
     "python pytorch llm 大模型 深度学习 transformer rlhf cuda megatron deepspeed 预训练 微调"),
    ("计算机视觉",
     "python pytorch opencv 计算机视觉 yolo 目标检测 图像分割 cuda tensorrt 多模态 bev 3d检测"),
    ("NLP/语音技术",
     "python pytorch nlp bert gpt asr tts 自然语言处理 transformer whisper kaldi 语音识别"),
    ("后端开发",
     "java golang python mysql redis 微服务 分布式 kafka grpc kubernetes 高并发 spring rpc"),
    ("前端开发",
     "javascript typescript react vue node.js webpack vite 前端开发 css html ssr 微前端 低代码"),
    ("移动端开发",
     "java kotlin android swift objective-c ios flutter 移动开发 jetpack mvvm 音视频 性能优化"),
    ("嵌入式软件",
     "c c++ rtos freertos 嵌入式 stm32 驱动 单片机 can autosar arm linux内核 bsp fpga"),
    ("数据工程/分析",
     "python sql spark flink hive 数据仓库 大数据 etl clickhouse kafka olap 数据建模"),
    ("安全工程",
     "python c 逆向 漏洞 渗透测试 安全 ctf pwn ida fuzzing frida linux 二进制 密码学"),
    ("自动驾驶",
     "c++ python ros 自动驾驶 slam 激光雷达 传感器融合 bev mpc 规划控制 点云 apollo"),
    ("芯片/半导体设计",
     "verilog systemverilog fpga 芯片设计 eda vlsi 数字电路 仿真 signoff dft sta 验证"),
    ("通信工程",
     "c c++ 5g 信号处理 协议栈 fpga 通信 dsp matlab 物理层 基带 无线 射频 调制解调"),
    ("云原生/DevOps",
     "kubernetes docker golang linux devops ci/cd prometheus terraform ansible istio grafana"),
    ("游戏开发",
     "c++ unity unreal 渲染 游戏引擎 shader 图形学 hlsl glsl opengl vulkan lua ecs 物理引擎"),
    ("产品经理",
     "产品经理 需求分析 用户研究 axure 产品规划 数据分析 原型设计 竞品分析 b端 c端"),
    ("测试/QA",
     "python selenium pytest 自动化测试 性能测试 qa jmeter postman unittest appium 接口测试"),
    ("运营/市场",
     "数据分析 运营 市场 增长 用户增长 策略 sql excel a/b测试 crm 投放 私域流量"),
    ("硬件工程",
     "altium cadence pcb 原理图 硬件设计 信号完整性 电路 emi emc 高速信号 电源 射频硬件"),
]

JOB_TYPES = ["实习", "校招", "社招"]

COMPANIES: list[str] = [
    "腾讯", "字节跳动", "阿里巴巴", "百度", "华为", "美团", "京东", "网易",
    "小米", "滴滴", "快手", "携程", "拼多多", "哔哩哔哩", "微博", "陌陌",
    "大疆", "商汤科技", "旷视科技", "地平线", "寒武纪", "文远知行", "元戎启行",
    "理想汽车", "蔚来", "小鹏汽车", "比亚迪", "宁德时代", "吉利汽车", "长城汽车",
    "中芯国际", "联发科", "海思半导体", "芯原微电子", "紫光展锐", "长鑫存储", "长江存储",
    "蚂蚁集团", "陆金所", "同花顺", "东方财富", "万得资讯", "平安科技", "招商银行科技",
    "Shopee", "贝壳找房", "作业帮", "猿辅导", "OPPO", "vivo", "荣耀", "联想",
    "中国移动", "中国联通", "中国电信", "中兴通讯", "爱立信中国", "诺基亚贝尔",
    "三一重工", "海尔", "海信", "格力", "中国航天科工", "中国航空工业", "国家电网",
]

_SYSTEM = """\
你是专业HR数据工程师，负责生成高质量技术岗位招聘数据集。
严格按JSON数组输出，每个元素包含且仅包含以下字段：
{
  "id": <整数>,
  "company": <公司名称>,
  "title": <职位名称，含具体产品线/业务方向，体现差异化>,
  "location": <"城市·类型"，如"北京·实习"、"深圳·校招"、"上海·社招">,
  "salary": <薪资字符串>,
  "type": <"实习"|"校招"|"社招" 三选一>,
  "tags": <3-5个技术标签的字符串数组>,
  "description": <60-100字，具体描述核心工作职责，不要泛泛>,
  "keywords": <10-15个小写英文/中文技术关键词数组，精确反映该岗位技术栈>
}

薪资格式规范：
- 实习："竞争性薪酬" 或 "300-400元/天"
- 校招："N+2薪+RSU" 或 "25-50K·15薪"
- 社招："20-50K·14薪" 或 "30-80K·16薪"（根据岗位级别）

额外要求：
- 只输出JSON数组，不含任何说明文字、代码块标记（```）或注释
- 20个岗位的公司必须多样，同一公司不超过2次
- 每个岗位的keywords要与该岗具体技术栈精确对应，岗位间keywords有明显差异
- 职位title要体现具体方向（如"推荐算法工程师-抖音"而非"算法工程师"）
"""


async def gen_batch(
    cat: str, kw_hint: str, job_type: str,
    id_start: int, companies: list[str],
) -> list[dict]:
    prompt = (
        f"生成20个「{cat}」方向的「{job_type}」岗位。\n"
        f"岗位ID从 {id_start} 开始连续编号（{id_start}到{id_start+19}）。\n"
        f"参考技术关键词（请根据各岗位具体方向细化）：{kw_hint}\n\n"
        f"从以下公司列表选取，确保多样性：\n"
        + json.dumps(companies, ensure_ascii=False)
    )
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user",   "content": prompt},
                ],
                "max_tokens": 8000,
                "temperature": 0.85,
            },
        )
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:]).rsplit("```", 1)[0].strip()

    jobs: list[dict] = json.loads(raw)

    # Enforce correct IDs and type field
    for i, j in enumerate(jobs):
        j["id"]   = id_start + i
        j["type"] = job_type
        # Ensure required fields have defaults
        j.setdefault("salary", "竞争性薪酬" if job_type == "实习" else "N+2薪+RSU")
        j.setdefault("url", "")
        j.setdefault("platform", "")
        j.setdefault("source_type", "preset")

    return jobs


async def main() -> None:
    with open(SEED_PATH, encoding="utf-8") as f:
        existing: list[dict] = json.load(f)

    # Build id→job map for incremental merging
    by_id: dict[int, dict] = {j["id"]: j for j in existing}
    next_id = max(by_id) + 1

    total   = len(CATEGORIES) * len(JOB_TYPES)
    done    = 0
    new_cnt = 0

    for cat_name, kw_hint in CATEGORIES:
        for job_type in JOB_TYPES:
            done += 1
            id_from = next_id
            print(f"\n[{done:02d}/{total}] {cat_name} × {job_type}  "
                  f"(IDs {id_from}–{id_from + 19})", flush=True)

            for attempt in range(3):
                try:
                    batch = await gen_batch(
                        cat_name, kw_hint, job_type, id_from, COMPANIES
                    )
                    if len(batch) < 10:
                        raise ValueError(f"Only {len(batch)} jobs returned (expected ≥10)")

                    for j in batch:
                        by_id[j["id"]] = j
                    next_id += len(batch)
                    new_cnt += len(batch)

                    # Incremental save — sorted by id
                    ordered = sorted(by_id.values(), key=lambda x: x["id"])
                    with open(SEED_PATH, "w", encoding="utf-8") as f:
                        json.dump(ordered, f, ensure_ascii=False, indent=2)

                    print(f"  OK {len(batch)} jobs saved  "
                          f"(seed total = {len(ordered)})", flush=True)
                    break

                except Exception as exc:
                    print(f"  attempt {attempt + 1}/3 failed: {exc!r}", flush=True)
                    if attempt < 2:
                        await asyncio.sleep(6)
                    else:
                        print("  SKIPPED after 3 failures — continuing.", flush=True)

            await asyncio.sleep(2.5)   # be gentle with the API

    final_count = len(by_id)
    print(f"\n{'='*60}")
    print(f"Done!  Total seed jobs: {final_count}  (+{new_cnt} new)")
    print(f"File:  {SEED_PATH.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
