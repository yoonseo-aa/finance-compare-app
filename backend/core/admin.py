from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, FinancialProduct, Post, RateOption, User


class RateOptionInline(admin.TabularInline):
    model = RateOption
    extra = 1


@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "name", "product_type", "best_rate")
    list_filter = ("bank_name", "product_type")
    search_fields = ("bank_name", "name", "product_code")
    inlines = [RateOptionInline]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("금융 프로필", {"fields": ("nickname", "age", "savings_goal", "preferred_term", "risk_tolerance", "joined_products")}),
    )
    list_display = ("username", "email", "nickname", "risk_tolerance", "preferred_term", "is_staff")


admin.site.register(Post)
admin.site.register(Comment)
