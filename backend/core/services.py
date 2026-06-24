import os
from datetime import datetime, timezone
import json
from functools import lru_cache
from time import time
from urllib.parse import quote

import requests
from .models import FinancialProduct, RateOption


DEMO_PRODUCTS = [
    {
        "code": "demo-deposit-001",
        "type": "deposit",
        "bank": "국민은행",
        "name": "KB 든든 정기예금",
        "options": [(6, 3.15, 3.35), (12, 3.25, 3.55), (24, 3.1, 3.4)],
    },
    {
        "code": "demo-saving-001",
        "type": "saving",
        "bank": "신한은행",
        "name": "신한 목표달성 적금",
        "options": [(6, 3.2, 3.7), (12, 3.4, 4.1), (24, 3.5, 4.2)],
    },
    {
        "code": "demo-deposit-002",
        "type": "deposit",
        "bank": "하나은행",
        "name": "하나 스마트 예금",
        "options": [(12, 3.3, 3.65), (24, 3.2, 3.5), (36, 3.1, 3.45)],
    },
    {
        "code": "demo-saving-002",
        "type": "saving",
        "bank": "우리은행",
        "name": "우리 청년 적금",
        "options": [(12, 3.6, 4.3), (24, 3.7, 4.45), (36, 3.8, 4.5)],
    },
]


def seed_demo_products():
    for item in DEMO_PRODUCTS:
        product, _ = FinancialProduct.objects.update_or_create(
            product_code=item["code"],
            defaults={
                "product_type": item["type"],
                "bank_name": item["bank"],
                "name": item["name"],
                "join_way": "영업점, 인터넷, 스마트폰",
                "join_member": "제한 없음",
                "special_condition": "급여이체, 자동이체, 마케팅 동의 등에 따라 우대금리가 적용됩니다.",
                "etc_note": "데모 데이터입니다. 금융감독원 API 키를 등록하면 실제 데이터로 갱신할 수 있습니다.",
            },
        )
        for term, rate, best_rate in item["options"]:
            RateOption.objects.update_or_create(
                product=product,
                save_term=term,
                rate_type="단리",
                defaults={"intr_rate": rate, "intr_rate2": best_rate},
            )


class FinlifeAPIError(Exception):
    pass


def fetch_finlife_products(product_type="deposit"):
    api_key = os.getenv("FINLIFE_API_KEY")
    if not api_key:
        raise FinlifeAPIError("FINLIFE_API_KEY가 설정되어 있지 않습니다.")

    endpoint = "depositProductsSearch" if product_type == "deposit" else "savingProductsSearch"
    response = requests.get(
        f"https://finlife.fss.or.kr/finlifeapi/{endpoint}.json",
        params={"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json().get("result", {})
    err_cd = payload.get("err_cd")
    if err_cd and err_cd != "000":
        raise FinlifeAPIError(f"금융 API 오류({err_cd}): {payload.get('err_msg', '알 수 없는 오류')}")

    products_by_code = {}

    for item in payload.get("baseList", []):
        code = item.get("fin_prdt_cd")
        product, _ = FinancialProduct.objects.update_or_create(
            product_code=f"{product_type}-{code}",
            defaults={
                "product_type": product_type,
                "bank_name": item.get("kor_co_nm", ""),
                "name": item.get("fin_prdt_nm", ""),
                "join_way": item.get("join_way", ""),
                "join_member": item.get("join_member", ""),
                "special_condition": item.get("spcl_cnd", ""),
                "etc_note": item.get("etc_note", ""),
            },
        )
        products_by_code[code] = product

    count = 0
    for option in payload.get("optionList", []):
        product = products_by_code.get(option.get("fin_prdt_cd"))
        if not product:
            continue
        RateOption.objects.update_or_create(
            product=product,
            save_term=int(option.get("save_trm") or 0),
            rate_type=option.get("intr_rate_type_nm", ""),
            defaults={
                "intr_rate": option.get("intr_rate") or 0,
                "intr_rate2": option.get("intr_rate2") or 0,
            },
        )
        count += 1
    return count


def fetch_finlife_loans(loan_type="credit", limit=50):
    api_key = os.getenv("FINLIFE_API_KEY")
    if not api_key:
        raise FinlifeAPIError("FINLIFE_API_KEY가 설정되어 있지 않습니다.")
    endpoints = {
        "credit": "creditLoanProductsSearch",
        "mortgage": "mortgageLoanProductsSearch",
        "rent": "rentHouseLoanProductsSearch",
    }
    if loan_type not in endpoints:
        raise FinlifeAPIError("지원하지 않는 대출 유형입니다.")
    response = requests.get(
        f"https://finlife.fss.or.kr/finlifeapi/{endpoints[loan_type]}.json",
        params={"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json().get("result", {})
    if payload.get("err_cd") and payload["err_cd"] != "000":
        raise FinlifeAPIError(f"금융 API 오류({payload['err_cd']}): {payload.get('err_msg', '알 수 없는 오류')}")
    type_labels = {"credit": "개인신용대출", "mortgage": "주택담보대출", "rent": "전세자금대출"}
    options_by_code = {}
    for option in payload.get("optionList", []):
        options_by_code.setdefault(option.get("fin_prdt_cd"), []).append(option)
    products = []
    for item in payload.get("baseList", [])[:limit]:
        product_code = item.get("fin_prdt_cd", "")
        options = options_by_code.get(product_code, [])
        products.append({
            "product_code": item.get("fin_prdt_cd", ""),
            "loan_type": loan_type,
            "loan_type_label": type_labels[loan_type],
            "bank_name": item.get("kor_co_nm", ""),
            "name": item.get("fin_prdt_nm", ""),
            "join_way": item.get("join_way", ""),
            "join_member": item.get("join_member", ""),
            "loan_inci_expn": item.get("loan_inci_expn", ""),
            "early_rpay_fee": item.get("erly_rpay_fee", ""),
            "loan_limit": item.get("loan_lmt", ""),
            "repay_type": item.get("rpay_type_nm", ""),
            "fin_co_no": item.get("fin_co_no", ""),
            "cb_name": item.get("cb_name", ""),
            "loan_product_type": item.get("crdt_prdt_type_nm", "") or item.get("mrtg_type_nm", "") or item.get("rent_type_nm", ""),
            "dcls_month": item.get("dcls_month", ""),
            "dcls_start_day": item.get("dcls_strt_day", ""),
            "dcls_end_day": item.get("dcls_end_day", ""),
            "fin_co_submit_day": item.get("fin_co_subm_day", ""),
            "options": options,
            "rate_min": min([float(option.get("lend_rate_min") or 0) for option in options if option.get("lend_rate_min") is not None] or [0]),
            "rate_max": max([float(option.get("lend_rate_max") or 0) for option in options if option.get("lend_rate_max") is not None] or [0]),
        })
    return products

SPOT_API_SYMBOLS = {
    "gold": "GC=F",
    "silver": "SI=F",
}
SPOT_API_SOURCE = "Yahoo Finance API"

def fetch_api_spot_prices(asset, cache_bucket):
    symbol = SPOT_API_SYMBOLS.get(asset, SPOT_API_SYMBOLS["gold"])
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}"
    response = requests.get(
        url,
        params={"range": "2y", "interval": "1d", "includePrePost": "false"},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=8,
    )
    response.raise_for_status()

    payload = response.json().get("chart", {})
    if payload.get("error"):
        raise requests.RequestException(payload["error"])

    result = (payload.get("result") or [None])[0]
    if not result:
        return []

    timestamps = result.get("timestamp") or []
    quote_data = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    closes = quote_data.get("close") or []
    opens = quote_data.get("open") or []
    highs = quote_data.get("high") or []
    lows = quote_data.get("low") or []
    volumes = quote_data.get("volume") or []

    rows = []
    for index, timestamp in enumerate(timestamps):
        close_price = closes[index] if index < len(closes) else None
        if close_price is None:
            continue

        row = {
            "date": datetime.fromtimestamp(timestamp, timezone.utc).date().isoformat(),
            "price": round(float(close_price), 3),
        }
        for source, target in ((opens, "open"), (highs, "high"), (lows, "low"), (volumes, "volume")):
            if index < len(source) and source[index] is not None:
                row[target] = round(float(source[index]), 3)
        rows.append(row)

    return rows


def load_spot_price_data(asset):
    cache_bucket = int(time() // 900)
    symbol = SPOT_API_SYMBOLS.get(asset, SPOT_API_SYMBOLS["gold"])
    try:
        rows = fetch_api_spot_prices(asset, cache_bucket)
        return {
            "rows": rows,
            "source": SPOT_API_SOURCE,
            "symbol": symbol,
            "is_live": bool(rows),
            "error": "" if rows else "API에서 시세 데이터를 가져오지 못했습니다.",
        }
    except requests.RequestException as exc:
        return {
            "rows": [],
            "source": SPOT_API_SOURCE,
            "symbol": symbol,
            "is_live": False,
            "error": "Yahoo Finance API에서 시세 데이터를 가져오지 못했습니다.",
        }


def load_spot_prices(asset):
    return load_spot_price_data(asset)["rows"]


def youtube_search(query):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not query:
        return []
    if not api_key:
        return demo_youtube_results(query)

    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"key": api_key, "part": "snippet", "q": query, "type": "video", "maxResults": 8},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return demo_youtube_results(query)

    videos = []
    for item in response.json().get("items", []):
        snippet = item["snippet"]
        videos.append(
            {
                "video_id": item["id"]["videoId"],
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "published_at": snippet["publishedAt"][:10],
                "thumbnail": snippet["thumbnails"]["medium"]["url"],
            }
        )
    return videos


def demo_youtube_results(query):
    return [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": f"{query} market analysis demo",
            "channel": "Finance Demo",
            "published_at": "2026-06-22",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        }
    ]


def naver_news_search(query):
    client_id = os.getenv("NAVER_NEWS_CLIENT_ID")
    client_secret = os.getenv("NAVER_NEWS_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []
    response = requests.get(
        "https://openapi.naver.com/v1/search/news.json",
        params={"query": query, "display": 10, "sort": "sim"},
        headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
        timeout=10,
    )
    response.raise_for_status()
    return [
        {
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "source": item.get("bloggername", "네이버 뉴스"),
            "published_at": item.get("pubDate", ""),
            "url": item.get("originallink") or item.get("link", ""),
            "reason": "검색어와의 관련성이 높아 추천",
        }
        for item in response.json().get("items", [])
    ]


def recommend_news_with_ai(query, articles):
    fallback = [{**article, "reason": article.get("reason") or "검색어와의 관련성이 높아 추천"} for article in articles[:4]]
    api_key = os.getenv("GMS_API_KEY")
    if not api_key or not articles:
        return fallback, False
    try:
        response = requests.post(
            f"{os.getenv('GMS_OPENAI_BASE_URL', 'https://gms.ssafy.io/gmsapi/api.openai.com/v1').rstrip('/')}/chat/completions",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            json={"model": os.getenv("GMS_OPENAI_MODEL", "gpt-5-mini"), "messages": [{"role": "developer", "content": "한국어 금융 뉴스 큐레이터입니다. 투자 조언 없이 관련도, 최신성, 정보성 기준으로 중복과 광고성 기사를 제외하세요."}, {"role": "user", "content": f"검색어: {query}\n후보: {json.dumps([{**item, 'index': i} for i, item in enumerate(articles)], ensure_ascii=False)}\n상위 4개를 JSON {{\"recommendations\":[{{\"index\":0,\"reason\":\"이유\"}}]}}으로 반환하세요."}], "response_format": {"type": "json_object"}},
            timeout=15,
        )
        response.raise_for_status()
        recommendations = json.loads(response.json()["choices"][0]["message"]["content"]).get("recommendations", [])
        selected = []
        for item in recommendations[:4]:
            index = item.get("index")
            if isinstance(index, int) and 0 <= index < len(articles): selected.append({**articles[index], "reason": item.get("reason") or "검색어와의 관련성이 높아 추천"})
        return (selected or fallback), bool(selected)
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return fallback, False










