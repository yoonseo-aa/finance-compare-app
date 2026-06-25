from django.contrib.auth.models import AbstractUser
from django.db import models


class FinancialProduct(models.Model):
    PRODUCT_TYPES = (
        ("deposit", "정기예금"),
        ("saving", "적금"),
    )

    product_code = models.CharField(max_length=80, unique=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    bank_name = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200, blank=True)
    join_member = models.CharField(max_length=200, blank=True)
    special_condition = models.TextField(blank=True)
    etc_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bank_name", "name"]

    def __str__(self):
        return f"{self.bank_name} - {self.name}"

    @property
    def best_rate(self):
        option = self.options.order_by("-intr_rate2", "-intr_rate").first()
        return option.intr_rate2 if option else 0


class RateOption(models.Model):
    product = models.ForeignKey(FinancialProduct, related_name="options", on_delete=models.CASCADE)
    save_term = models.PositiveIntegerField(default=12)
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rate_type = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["save_term"]
        unique_together = ("product", "save_term", "rate_type")

    def __str__(self):
        return f"{self.product.name} {self.save_term}개월 {self.intr_rate2}%"


class User(AbstractUser):
    RISK_CHOICES = (
        ("stable", "안정형"),
        ("balanced", "균형형"),
        ("aggressive", "수익형"),
    )
    AGE_GROUP_CHOICES = (
        ("", "선택 안 함"),
        ("child", "어린이"),
        ("youth", "청년"),
        ("middle", "중장년"),
        ("senior", "시니어"),
    )
    MARITAL_CHOICES = (
        ("", "선택 안 함"),
        ("single", "미혼"),
        ("married", "기혼"),
    )
    INCOME_CHOICES = (
        ("", "선택 안 함"),
        ("low", "낮음"),
        ("middle", "보통"),
        ("high", "높음"),
    )
    ASSET_CHOICES = (
        ("", "선택 안 함"),
        ("low", "적음"),
        ("middle", "보통"),
        ("high", "많음"),
    )
    EMPLOYMENT_CHOICES = (
        ("", "선택 안 함"),
        ("student", "학생"),
        ("employee", "직장인"),
        ("self_employed", "자영업자"),
        ("retired", "은퇴/퇴직"),
    )
    SAVING_PURPOSE_CHOICES = (
        ("", "선택 안 함"),
        ("emergency", "비상금"),
        ("housing", "주거/내 집 마련"),
        ("education", "교육/자녀"),
        ("retirement", "노후 준비"),
        ("travel", "여행/목돈"),
    )

    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.FileField(upload_to="profiles/", blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, blank=True, default="")
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, blank=True, default="")
    has_children = models.BooleanField(null=True, blank=True)
    region = models.CharField(max_length=50, blank=True)
    income_level = models.CharField(max_length=20, choices=INCOME_CHOICES, blank=True, default="")
    asset_level = models.CharField(max_length=20, choices=ASSET_CHOICES, blank=True, default="")
    employment_status = models.CharField(max_length=30, choices=EMPLOYMENT_CHOICES, blank=True, default="")
    saving_purpose = models.CharField(max_length=30, choices=SAVING_PURPOSE_CHOICES, blank=True, default="")
    savings_goal = models.PositiveIntegerField(default=1000000)
    monthly_saving = models.PositiveIntegerField(default=400000)
    preferred_term = models.PositiveIntegerField(default=12)
    risk_tolerance = models.CharField(max_length=20, choices=RISK_CHOICES, default="stable", blank=True)
    joined_products = models.ManyToManyField(FinancialProduct, blank=True, related_name="joined_users")

    def display_name(self):
        return self.nickname or self.username

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author}: {self.content[:20]}"


