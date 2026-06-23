from decimal import Decimal

from .models import FinancialProduct


KEYWORDS = {
    "child": ["아이", "키즈", "주니어", "어린이", "자녀", "청소년"],
    "youth": ["청년", "Youth", "MZ", "2030", "첫거래", "학생"],
    "middle": ["가족", "주거", "내집", "직장", "급여", "파트너"],
    "senior": ["시니어", "연금", "퇴직", "은퇴", "든든"],
    "housing": ["주택", "청약", "내집", "주거", "전세", "부동산"],
    "education": ["교육", "자녀", "아이", "키즈", "주니어"],
    "retirement": ["연금", "노후", "시니어", "퇴직", "은퇴"],
    "travel": ["여행", "목돈", "자유", "플러스"],
    "employee": ["급여", "직장", "재직", "월급", "첫거래"],
    "self_employed": ["사업", "소상공", "사장", "자영", "파트너"],
    "student": ["학생", "청년", "Youth", "주니어"],
    "retired": ["연금", "시니어", "퇴직", "은퇴"],
}


def product_text(product):
    return " ".join(
        [
            product.bank_name or "",
            product.name or "",
            product.join_way or "",
            product.join_member or "",
            product.special_condition or "",
            product.etc_note or "",
        ]
    )


def has_keyword(text, key):
    return any(word.lower() in text.lower() for word in KEYWORDS.get(key, []))


def add_bonus(score, reasons, amount, reason):
    return score + amount, reasons + [reason]


def profile_match_score(product, option, user):
    text = product_text(product)
    score = 0
    reasons = []

    age_group = user.age_group or ""
    if age_group and has_keyword(text, age_group):
        score, reasons = add_bonus(score, reasons, 18, f"{user.get_age_group_display()} 대상 조건과 잘 맞아요")
    elif age_group == "child" and product.product_type == "saving":
        score, reasons = add_bonus(score, reasons, 8, "어린이 목돈 마련에 적합한 적금 상품이에요")
    elif age_group in {"middle", "senior"} and product.product_type == "deposit":
        score, reasons = add_bonus(score, reasons, 7, "안정적인 예치에 어울리는 예금 상품이에요")

    if user.marital_status == "married" and any(word in text for word in ["가족", "주거", "내집", "파트너"]):
        score, reasons = add_bonus(score, reasons, 8, "가족/주거 관련 우대 조건이 보여요")

    if user.has_children and has_keyword(text, "education"):
        score, reasons = add_bonus(score, reasons, 16, "자녀/교육 목적에 맞는 상품명이 포함돼요")

    if user.region and user.region.strip() and user.region.strip() in text:
        score, reasons = add_bonus(score, reasons, 7, f"{user.region.strip()} 지역 조건과 연결돼요")

    if user.income_level == "low" and product.product_type == "saving":
        score, reasons = add_bonus(score, reasons, 6, "소액부터 꾸준히 모으기 좋은 적금이에요")
    elif user.income_level == "high" and product.product_type == "deposit":
        score, reasons = add_bonus(score, reasons, 6, "여유 자금을 안정적으로 굴리기 좋은 예금이에요")

    if user.asset_level == "low" and option.save_term <= 12:
        score, reasons = add_bonus(score, reasons, 5, "짧은 기간으로 부담을 낮출 수 있어요")
    elif user.asset_level == "high" and product.product_type == "deposit":
        score, reasons = add_bonus(score, reasons, 5, "보유 자산을 안정적으로 예치하기 좋아요")

    if user.employment_status and has_keyword(text, user.employment_status):
        score, reasons = add_bonus(score, reasons, 9, f"{user.get_employment_status_display()}에게 맞는 키워드가 있어요")

    purpose = user.saving_purpose or ""
    if purpose and has_keyword(text, purpose):
        score, reasons = add_bonus(score, reasons, 13, f"{user.get_saving_purpose_display()} 목적과 잘 맞아요")
    elif purpose == "emergency" and option.save_term <= 12:
        score, reasons = add_bonus(score, reasons, 8, "비상금처럼 짧게 운용하기 좋은 기간이에요")
    elif purpose in {"education", "travel"} and product.product_type == "saving":
        score, reasons = add_bonus(score, reasons, 7, "목표 금액을 꾸준히 모으는 적금 성격과 맞아요")
    elif purpose == "retirement" and product.product_type == "deposit":
        score, reasons = add_bonus(score, reasons, 7, "노후 자금을 안정적으로 운용하기 좋아요")

    if user.risk_tolerance == "stable" and product.product_type == "deposit":
        score, reasons = add_bonus(score, reasons, 10, "안정형 성향에 맞는 예금 상품이에요")
    elif user.risk_tolerance == "balanced":
        score, reasons = add_bonus(score, reasons, 5, "균형형 성향에 무난한 금리 상품이에요")
    elif user.risk_tolerance == "aggressive" and product.product_type == "saving":
        score, reasons = add_bonus(score, reasons, 8, "수익형 성향에 맞춰 높은 우대금리를 노려볼 수 있어요")

    return score, reasons


def recommend_products(user, limit=3):
    scored = []
    products = FinancialProduct.objects.prefetch_related("options").all()

    for product in products:
        options = list(product.options.all())
        if not options:
            continue

        best_option = max(options, key=lambda option: (option.intr_rate2, option.intr_rate))
        term_gap = abs(best_option.save_term - user.preferred_term)
        rate_score = Decimal(best_option.intr_rate2) * Decimal("10")
        term_score = max(0, 24 - term_gap)
        profile_score, profile_reasons = profile_match_score(product, best_option, user)
        score = float(rate_score) + term_score + profile_score

        reasons = [
            f"최고 우대금리 {best_option.intr_rate2}%",
            f"희망 기간 {user.preferred_term}개월과 {term_gap}개월 차이",
            *profile_reasons[:3],
        ]

        scored.append(
            {
                "product": product,
                "option": best_option,
                "score": round(score, 1),
                "reasons": reasons,
            }
        )

    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]
