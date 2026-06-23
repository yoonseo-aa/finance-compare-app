from decimal import Decimal, ROUND_HALF_UP

from .models import FinancialProduct
from .recommendation import recommend_products
from .serializers import ProductListSerializer


def money(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def best_option(product, preferred_term=None):
    options = list(product.options.all())
    if not options:
        return None
    if preferred_term:
        return sorted(options, key=lambda option: (abs(option.save_term - preferred_term), -option.intr_rate2))[0]
    return max(options, key=lambda option: (option.intr_rate2, option.intr_rate))


def expected_maturity_amount(monthly_saving, term, annual_rate):
    principal = Decimal(monthly_saving) * Decimal(term)
    monthly_rate = Decimal(annual_rate) / Decimal("100") / Decimal("12")
    interest = Decimal("0")
    for month in range(term):
        remaining_months = term - month
        interest += Decimal(monthly_saving) * monthly_rate * Decimal(remaining_months)
    return money(principal + interest)


def condition_ease(product):
    text = f"{product.special_condition} {product.etc_note}".strip()
    if not text:
        return 88
    hard_words = ["급여", "카드", "첫거래", "마케팅", "자동이체", "앱", "청약"]
    hits = sum(1 for word in hard_words if word in text)
    return max(45, 95 - hits * 10)


def product_projection(product, user):
    option = best_option(product, user.preferred_term)
    if not option:
        return None
    expected = expected_maturity_amount(user.monthly_saving, user.preferred_term, option.intr_rate2)
    principal = user.monthly_saving * user.preferred_term
    return {
        "product": ProductListSerializer(product).data,
        "option": {
            "save_term": option.save_term,
            "intr_rate2": option.intr_rate2,
        },
        "expected_amount": expected,
        "expected_interest": max(0, expected - principal),
        "condition_ease": condition_ease(product),
    }


def build_dashboard(user):
    products = list(FinancialProduct.objects.prefetch_related("options").all())
    projections = [product_projection(product, user) for product in products]
    projections = [item for item in projections if item]
    principal = user.monthly_saving * user.preferred_term

    best_expected = max([item["expected_amount"] for item in projections], default=principal)
    goal_progress = min(100, round((best_expected / user.savings_goal) * 100, 1)) if user.savings_goal else 100
    monthly_needed = max(0, money(Decimal(user.savings_goal) / Decimal(max(1, user.preferred_term))))
    gap_monthly = max(0, monthly_needed - user.monthly_saving)

    stable = recommend_products(user, limit=3)
    high_rate = sorted(projections, key=lambda item: item["option"]["intr_rate2"], reverse=True)[:3]
    easy_conditions = sorted(projections, key=lambda item: item["condition_ease"], reverse=True)[:3]

    recommendation_groups = {
        "stable": [
            {
                "product": ProductListSerializer(item["product"]).data,
                "score": item["score"],
                "reasons": item["reasons"],
            }
            for item in stable
        ],
        "high_rate": high_rate,
        "easy_conditions": easy_conditions,
    }

    top_for_chart = sorted(projections, key=lambda item: item["expected_amount"], reverse=True)[:6]
    rate_for_chart = sorted(projections, key=lambda item: item["option"]["intr_rate2"], reverse=True)[:6]
    condition_for_chart = sorted(projections, key=lambda item: item["condition_ease"], reverse=True)[:6]
    asset_capacity = round((user.monthly_saving / monthly_needed) * 100, 1) if monthly_needed else 100
    asset_capacity = min(100, max(0, asset_capacity))
    expected_interest = max(0, best_expected - principal)

    return {
        "asset_status": {
            "income_level": user.get_income_level_display() if user.income_level else "미입력",
            "asset_level": user.get_asset_level_display() if user.asset_level else "미입력",
            "employment_status": user.get_employment_status_display() if user.employment_status else "미입력",
            "saving_purpose": user.get_saving_purpose_display() if user.saving_purpose else "미입력",
            "principal": principal,
            "expected_interest": expected_interest,
            "best_expected_amount": best_expected,
            "monthly_capacity_rate": asset_capacity,
        },
        "goal": {
            "target_amount": user.savings_goal,
            "target_months": user.preferred_term,
            "monthly_saving": user.monthly_saving,
            "principal": principal,
            "best_expected_amount": best_expected,
            "goal_progress": goal_progress,
            "success_probability": min(99, max(50, round(goal_progress + 4, 1))),
            "monthly_needed": monthly_needed,
            "gap_monthly": gap_monthly,
        },
        "recommendation_groups": recommendation_groups,
        "charts": {
            "goal_progress": {
                "labels": ["Achievable", "Remaining"],
                "data": [goal_progress, max(0, round(100 - goal_progress, 1))],
            },
            "maturity_amounts": {
                "labels": [item["product"]["name"] for item in top_for_chart],
                "data": [item["expected_amount"] for item in top_for_chart],
            },
            "rate_compare": {
                "labels": [item["product"]["name"] for item in rate_for_chart],
                "data": [item["option"]["intr_rate2"] for item in rate_for_chart],
            },
            "condition_ease": {
                "labels": [item["product"]["name"] for item in condition_for_chart],
                "data": [item["condition_ease"] for item in condition_for_chart],
            },
        },
    }


