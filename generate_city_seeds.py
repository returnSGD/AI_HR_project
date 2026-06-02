#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_city_seeds.py -- Generate geographically diverse job data.
Covers provincial capitals + major cities + HK/MO districts.
Includes service industry / frontline jobs suitable for 专科生.
Run:  python generate_city_seeds.py
"""
import asyncio, json, os, sys
from pathlib import Path
from datetime import datetime
import httpx
from dotenv import load_dotenv
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
load_dotenv()

LLM_API_KEY  = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL    = os.getenv("LLM_MODEL",    "deepseek-chat")
SEED_PATH    = Path("backend/data/seed_jobs.json")
TODAY        = datetime.now().strftime("%Y-%m-%d")

if not LLM_API_KEY:
    sys.exit("ERROR: LLM_API_KEY not set.")

# ── City batches ──────────────────────────────────────────────────────
# Each entry: (city_name, province, industry_focus, job_count)
CITY_BATCHES = [
    # 二线科技重镇 — 以科技岗为主
    ("成都",   "四川",     "互联网/科技/游戏",       8),
    ("武汉",   "湖北",     "互联网/光电/智能制造",    8),
    ("南京",   "江苏",     "软件/半导体/研究院",      8),
    ("西安",   "陕西",     "军工/航天/半导体/互联网",  8),
    ("合肥",   "安徽",     "芯片/新能源/科技",        8),
    ("苏州",   "江苏",     "半导体/制造/外资科技",    8),
    ("无锡",   "江苏",     "半导体/物联网/制造",      6),
    ("郑州",   "河南",     "互联网/物流/制造",        6),
    ("长沙",   "湖南",     "工程机械/互联网/媒体",    6),
    ("福州",   "福建",     "互联网/金融科技",         6),
    ("厦门",   "福建",     "互联网/跨境电商/金融",    6),
    ("青岛",   "山东",     "海洋/制造/互联网",        6),
    ("济南",   "山东",     "政务信息化/互联网/制造",  6),
    ("沈阳",   "辽宁",     "装备制造/互联网/汽车",    6),
    ("大连",   "辽宁",     "软件/航运/制造",          6),
    ("哈尔滨", "黑龙江",   "装备/农业科技/互联网",    5),
    ("长春",   "吉林",     "汽车/轨交/互联网",        5),
    ("贵阳",   "贵州",     "大数据/云计算/互联网",    5),
    ("昆明",   "云南",     "旅游科技/互联网/新能源",  5),
    ("南昌",   "江西",     "VR/航空/互联网",          5),
    ("南宁",   "广西",     "互联网/金融/物流",        5),
    ("太原",   "山西",     "能源/互联网/制造",        5),
    ("兰州",   "甘肃",     "能源/互联网/制造",        4),
    ("西宁",   "青海",     "新能源/互联网",           4),
    ("银川",   "宁夏",     "互联网/制造/农业科技",    4),
    ("呼和浩特","内蒙古",  "能源/互联网/制造",        4),
    ("拉萨",   "西藏",     "旅游/互联网/政务",        3),
    ("乌鲁木齐","新疆",    "能源/互联网/物流",        4),
    ("海口",   "海南",     "旅游科技/金融/互联网",    4),
    ("三亚",   "海南",     "旅游/零售/服务业",        3),
    # 广东重要城市
    ("佛山",   "广东",     "制造/工业互联网/陶瓷",   5),
    ("东莞",   "广东",     "制造/智能硬件/互联网",   5),
    ("珠海",   "广东",     "高新技术/航空/软件",     5),
    # 珠三角/长三角其他城市
    ("宁波",   "浙江",     "制造/港口物流/互联网",   5),
    ("温州",   "浙江",     "制造/互联网/金融",       4),
    ("扬州",   "江苏",     "制造/旅游/互联网",       4),
    # 服务业为主的城市 (专科友好)
    ("桂林",   "广西",     "旅游/服务业/零售",        4),
    ("丽江",   "云南",     "旅游/酒店/服务业",        3),
    ("张家界", "湖南",     "旅游/服务业/互联网",      3),
]

# Hong Kong districts — finance/tech/service focus
HK_DISTRICTS = [
    ("中西区",  "金融/律所/跨国企业总部"),
    ("湾仔区",  "会展/咨询/科技公司"),
    ("东区",    "科技/零售/服务"),
    ("南区",    "海洋科技/服务"),
    ("九龙城区","零售/餐饮/服务"),
    ("观塘区",  "工业/科技/初创企业"),
    ("深水埗区","零售/科技/文创"),
    ("黄大仙区","零售/医疗/服务"),
    ("油尖旺区","零售/旅游/酒店"),
    ("葵青区",  "物流/制造/服务"),
    ("荃湾区",  "制造/物流/零售"),
    ("屯门区",  "制造/服务/医疗"),
    ("元朗区",  "零售/物流/服务"),
    ("北区",    "跨境贸易/农业/服务"),
    ("大埔区",  "工业/科技/服务"),
    ("沙田区",  "大学/科技/零售"),
    ("西贡区",  "旅游/服务/科技"),
    ("离岛区",  "机场/物流/旅游"),
]

MO_DISTRICTS = [
    ("花地玛堂区", "博彩/酒店/科技"),
    ("大堂区",     "博彩/金融/零售"),
    ("风顺堂区",   "旅游/博彩/服务"),
    ("嘉模堂区",   "博彩/物流/服务"),
    ("圣方济各堂区","博彩/建筑/服务"),
    ("路凼区",     "博彩度假区/酒店/科技"),
]

_SYS = """\
你是专业HR数据工程师，生成特定城市的招聘信息数据集。
严格按JSON数组输出，每个元素包含且仅包含：
{
  "id": <整数>,
  "company": <本地企业或该城市有分部的企业名>,
  "title": <职位名称，含具体方向>,
  "location": <"城市名·类型"，如"成都·校招">,
  "salary": <薪资>,
  "type": <"实习"|"校招"|"社招">,
  "tags": <3-5个标签字符串数组>,
  "description": <50-80字职责描述>,
  "keywords": <8-12个小写技术/行业关键词数组>,
  "source_type": "preset",
  "created_at": "<today_date>"
}
输出规则：
- 只输出JSON数组，不含任何说明或代码块标记
- 岗位要真实反映该城市的产业特色
- 岗位类型要多样：实习/校招/社招各占约1/3
- 薪资：实习"300-500元/天"或"竞争性薪酬"；校招"N+2薪"格式；社招"K范围·薪"格式
- 专科生可接受的一线/服务业岗位（如客服/零售督导/运营专员/销售/仓储物流）可适当加入
"""


async def gen(city: str, province: str, industry: str, count: int,
              id_start: int, today: str) -> list[dict]:
    prompt = (
        f"为{province}{city}生成{count}个招聘岗位（聚焦{industry}产业）。\n"
        f"岗位ID从{id_start}开始，created_at填\"{today}\"。\n"
        f"location格式为\"{city}·类型\"（类型：实习/校招/社招之一）。\n"
        f"公司使用{city}本地企业或在{city}有重要业务的企业。"
    )
    async with httpx.AsyncClient(timeout=120.0) as c:
        r = await c.post(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY.strip()}",
                     "Content-Type": "application/json"},
            json={"model": LLM_MODEL, "messages": [
                    {"role": "system", "content": _SYS},
                    {"role": "user",   "content": prompt}],
                  "max_tokens": 4000, "temperature": 0.85},
        )
        r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:]).rsplit("```", 1)[0].strip()
    jobs = json.loads(raw)
    for i, j in enumerate(jobs):
        j["id"] = id_start + i
        j.setdefault("source_type", "preset")
        j.setdefault("created_at",  today)
        j.setdefault("is_active",   1)
        j.setdefault("url",         "")
        j.setdefault("platform",    "")
    return jobs


async def main():
    with open(SEED_PATH, encoding="utf-8") as f:
        existing = json.load(f)
    by_id = {j["id"]: j for j in existing}
    next_id = max(by_id) + 1

    batches = (
        [(city, prov, ind, cnt) for city, prov, ind, cnt in CITY_BATCHES]
        + [(dist, "香港", ind, 4) for dist, ind in HK_DISTRICTS]
        + [(dist, "澳门", ind, 3) for dist, ind in MO_DISTRICTS]
    )
    total = len(batches)

    for idx, (city, prov, industry, count) in enumerate(batches, 1):
        print(f"[{idx:03d}/{total}] {prov} · {city}  (IDs {next_id}–{next_id+count-1})", flush=True)
        for attempt in range(3):
            try:
                batch = await gen(city, prov, industry, count, next_id, TODAY)
                if len(batch) < max(2, count // 2):
                    raise ValueError(f"only {len(batch)} returned")
                for j in batch:
                    by_id[j["id"]] = j
                next_id += len(batch)
                ordered = sorted(by_id.values(), key=lambda x: x["id"])
                with open(SEED_PATH, "w", encoding="utf-8") as f:
                    json.dump(ordered, f, ensure_ascii=False, indent=2)
                print(f"  OK {len(batch)} saved (total={len(ordered)})", flush=True)
                break
            except Exception as e:
                print(f"  attempt {attempt+1}/3 failed: {e!r}", flush=True)
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    print("  SKIPPED.", flush=True)
        await asyncio.sleep(2)

    print(f"\nDone. Seed total: {len(by_id)}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
