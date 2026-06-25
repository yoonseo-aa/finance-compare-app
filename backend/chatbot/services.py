import requests
from django.conf import settings


class ChatbotServiceError(Exception):
    pass


SYSTEM_PROMPT = """
너는 FinPick 금융상품 비교 서비스의 AI 상담 챗봇이다.
사용자의 금융상품 비교, 예적금 추천, 대출비교, 연금저축, 금은시세, 관심상품, 마이금융 사용을 도와준다.
답변은 한국어로 쉽고 짧게 설명한다.
금융상품 가입을 확정적으로 권유하지 않는다.
금리, 수익률, 대출 조건은 변동될 수 있으므로 공식 금융회사 정보와 약관 확인이 필요하다고 안내한다.
사용자의 개인정보를 답변에 노출하지 않는다.
모르는 내용은 추측하지 말고 확인이 필요하다고 말한다.
FinPick 내부 데이터에 없는 상품 정보는 임의로 지어내지 않는다.
투자, 대출, 예금 가입 판단은 참고용 정보로만 안내한다.
""".strip()

SERVICE_GUIDE = """
FinPick 주요 메뉴 안내:
- 예적금상품: 은행별 예금/적금 상품을 금리, 기간, 우대조건 기준으로 비교합니다.
- 추천진단: 나이대, 소득, 재산, 저축 목적, 성향, 목표 금액 등을 입력해 추천 조건을 저장합니다.
- 추천 결과: 입력한 조건과 상품 데이터를 기준으로 추천 점수와 이유를 보여줍니다.
- 개인화 대시보드: 목표 달성 가능성, 예상 만기 금액, 현재 재산현황을 요약합니다.
- 금은시세: 금과 은 가격을 원화 기준으로 확인하고 변동 추이를 봅니다.
- 관심상품: 저장한 상품을 마이페이지에서 다시 확인하고 비교합니다.
- 은행찾기: 현재 위치 또는 검색어 기준으로 가까운 은행 지점을 지도에서 확인합니다.
""".strip()

LABELS = {
    "stable": "안정형",
    "balanced": "균형형",
    "aggressive": "수익형",
    "child": "어린이",
    "youth": "청년",
    "middle": "중장년",
    "senior": "시니어",
    "single": "미혼",
    "married": "기혼",
    "low": "낮음",
    "high": "높음",
    "student": "학생",
    "employee": "직장인",
    "self_employed": "자영업자",
    "retired": "은퇴/퇴직",
    "emergency": "비상금 준비형",
    "housing": "주거/내 집 마련형",
    "education": "교육/자녀 준비형",
    "retirement": "노후 준비형",
    "travel": "목돈 마련형",
}

QUICK_CONTEXT_TYPES = {"spot", "loan", "pension", "favorite", "product", "general"}
PERSONALIZED_HINTS = ("내추천", "내조건", "내상품", "나의", "추천결과", "왜", "점수", "진단", "맞춤")


def label(value, fallback="입력 전"):
    if value is True:
        return "자녀 있음"
    if value is False:
        return "자녀 없음"
    if value in (None, ""):
        return fallback
    return LABELS.get(value, str(value))


def format_money(value):
    try:
        return f"{int(value):,}원"
    except (TypeError, ValueError):
        return "입력 전"


def build_user_context(user, context_type=""):
    if not user:
        return "로그인하지 않은 사용자입니다. 일반적인 FinPick 사용 방법 위주로 안내하세요."

    if context_type != "recommendation":
        return "로그인 사용자입니다. 계정 식별 정보는 사용하지 말고 일반적인 서비스 안내 위주로 답변하세요."

    context = {
        "추천 프로필 유형": label(user.saving_purpose),
        "저축 성향": label(user.risk_tolerance),
        "나이대": label(user.age_group),
        "소득 수준": label(user.income_level),
        "재산 수준": label(user.asset_level),
        "목표 금액": format_money(user.savings_goal),
        "월 저축 가능 금액": format_money(user.monthly_saving),
        "선호 기간": f"{user.preferred_term}개월" if user.preferred_term else "입력 전",
        "관심상품 수": f"{user.joined_products.count()}개",
    }

    lines = ["로그인 사용자의 비식별 추천 컨텍스트입니다. 이메일, 아이디, 소셜 제공자는 포함하지 않습니다."]
    lines.extend(f"- {key}: {value}" for key, value in context.items())
    return "\n".join(lines)


def build_local_fallback_answer(message, context_type, user_context):
    if "관심" in message:
        answer = (
            "관심상품은 상품 카드나 상세 화면에서 저장한 뒤 마이페이지의 관심 상품 메뉴에서 다시 확인할 수 있어요. "
            "저장한 상품은 나중에 금리와 조건을 비교할 때 참고용으로 활용하면 좋습니다."
        )
    elif "예적금" in message or "예금" in message or "적금" in message:
        answer = (
            "예적금은 금리만 보지 말고 기간, 우대조건, 가입대상, 납입 방식까지 함께 비교하는 게 좋아요. "
            "FinPick의 금융상품 메뉴에서 은행별 상품을 보고, 추천 결과에서는 내 조건에 맞는 점수와 이유를 확인할 수 있습니다."
        )
    elif "추천" in message:
        answer = (
            "추천 결과는 저축 목적, 성향, 목표 금액, 월 저축 가능 금액, 선호 기간 같은 정보를 바탕으로 계산됩니다. "
            "점수가 높다는 것은 현재 입력한 조건과 상품 조건이 비교적 잘 맞는다는 의미예요."
        )
    elif "금" in message or "은" in message or "시세" in message:
        answer = (
            "금은시세 메뉴에서 금과 은의 현재 시세와 변동 추이를 원화 기준으로 볼 수 있어요. "
            "그래프와 일별 시세를 함께 보면 최근 흐름을 빠르게 확인할 수 있습니다."
        )
    elif "대출" in message:
        answer = (
            "대출비교는 금리, 상환 방식, 한도, 중도상환수수료, 우대조건을 함께 봐야 합니다. "
            "실제 대출 가능 조건은 개인 신용도와 금융회사 심사에 따라 달라질 수 있어요."
        )
    elif "연금" in message:
        answer = (
            "연금저축은 장기 노후 준비와 세액공제 관점에서 확인하는 상품입니다. "
            "납입 기간, 수수료, 운용 방식, 중도 해지 시 불이익을 함께 확인하는 것이 좋아요."
        )
    else:
        answer = (
            "FinPick에서는 예적금상품 비교, 추천진단, 추천 결과, 개인화 대시보드, 금은시세, 은행찾기 기능을 사용할 수 있어요. "
            "궁금한 메뉴명을 함께 질문하면 더 구체적으로 안내해드릴게요."
        )

    return f"{answer}\n\n참고용 안내이므로 가입 전에는 반드시 공식 금융회사 정보와 약관을 확인해주세요."


def should_use_quick_answer(message, context_type):
    compact = message.replace(" ", "")
    if context_type == "recommendation":
        return False
    if any(hint in compact for hint in PERSONALIZED_HINTS):
        return False
    if context_type in QUICK_CONTEXT_TYPES and len(message) <= 80:
        return True
    return any(keyword in message for keyword in ("어디", "어떻게", "방법", "메뉴", "사용", "저장", "비교")) and len(message) <= 80


def build_messages(message, context_type, user_context):
    return [
        {"role": "developer", "content": SYSTEM_PROMPT},
        {"role": "developer", "content": SERVICE_GUIDE},
        {"role": "developer", "content": user_context},
        {
            "role": "user",
            "content": f"질문 유형: {context_type or 'general'}\n사용자 질문: {message}\n답변은 5문장 이내로 간결하게 작성하세요.",
        },
    ]


def call_chat_completion(model, messages):
    api_key = (getattr(settings, "OPENAI_API_KEY", "") or getattr(settings, "GMS_API_KEY", "")).strip()
    if not api_key:
        raise ChatbotServiceError("GMS_API_KEY 또는 OPENAI_API_KEY가 설정되어 있지 않습니다.")

    base_url = ((getattr(settings, "OPENAI_BASE_URL", "") or getattr(settings, "GMS_OPENAI_BASE_URL", "https://gms.ssafy.io/gmsapi/api.openai.com/v1")).strip()).rstrip("/")
    timeout = int(getattr(settings, "CHATBOT_TIMEOUT_SECONDS", 8) or 8)
    max_tokens = int(getattr(settings, "CHATBOT_MAX_TOKENS", 420) or 420)
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def generate_chatbot_answer(message, user=None, context_type=""):
    context_type = context_type or "general"
    user_context = build_user_context(user, context_type)

    if should_use_quick_answer(message, context_type):
        return {"answer": build_local_fallback_answer(message, context_type, user_context), "model": "finpick-fast-guide"}

    model = (getattr(settings, "OPENAI_CHAT_MODEL", "") or getattr(settings, "GMS_OPENAI_MODEL", "gpt-5.4-mini")).strip()
    fallback_model = (getattr(settings, "OPENAI_CHAT_FALLBACK_MODEL", "") or "gpt-5.4-nano").strip()
    if context_type != "recommendation" and fallback_model:
        model = fallback_model

    messages = build_messages(message, context_type, user_context)

    try:
        answer = call_chat_completion(model, messages)
        used_model = model
    except ChatbotServiceError:
        return {"answer": build_local_fallback_answer(message, context_type, user_context), "model": "finpick-local-guide"}
    except requests.RequestException:
        if fallback_model and fallback_model != model:
            try:
                answer = call_chat_completion(fallback_model, messages)
                used_model = fallback_model
            except (requests.RequestException, ChatbotServiceError):
                return {"answer": build_local_fallback_answer(message, context_type, user_context), "model": "finpick-local-guide"}
        else:
            return {"answer": build_local_fallback_answer(message, context_type, user_context), "model": "finpick-local-guide"}

    if "공식 금융회사" not in answer and "약관" not in answer:
        answer = f"{answer}\n\n참고용 안내이므로 가입 전에는 반드시 공식 금융회사 정보와 약관을 확인해주세요."

    return {"answer": answer, "model": used_model}
