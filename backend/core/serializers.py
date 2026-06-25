from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Comment, FavoriteLoan, FavoriteSavings, FinancialProduct, Post, RateOption, User


class RateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateOption
        fields = ("id", "save_term", "intr_rate", "intr_rate2", "rate_type")


class ProductListSerializer(serializers.ModelSerializer):
    best_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    product_type_label = serializers.CharField(source="get_product_type_display", read_only=True)

    class Meta:
        model = FinancialProduct
        fields = ("id", "product_code", "product_type", "product_type_label", "bank_name", "name", "best_rate")


class ProductDetailSerializer(ProductListSerializer):
    options = RateOptionSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "join_way",
            "join_member",
            "special_condition",
            "etc_note",
            "options",
        )


class FavoriteLoanSerializer(serializers.ModelSerializer):
    favorite_key = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteLoan
        fields = (
            "id",
            "favorite_key",
            "loan_type",
            "product_code",
            "name",
            "bank_name",
            "loan_type_label",
            "rate_min",
            "loan_limit",
            "repay_type",
            "join_member",
        )

    def get_favorite_key(self, obj):
        return f"loan:{obj.loan_type}:{obj.product_code}"


class FavoriteSavingsSerializer(serializers.ModelSerializer):
    favorite_key = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteSavings
        fields = (
            "id",
            "favorite_key",
            "product_code",
            "product_type_label",
            "product_subtype",
            "name",
            "bank_name",
            "rate_value",
            "rate_label",
            "join_way",
            "join_member",
            "special_condition",
            "etc_note",
        )

    def get_favorite_key(self, obj):
        return f"savings:{obj.product_code}"


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    has_usable_password = serializers.SerializerMethodField()
    joined_products = ProductListSerializer(many=True, read_only=True)
    joined_loans = FavoriteLoanSerializer(many=True, read_only=True)
    joined_savings = FavoriteSavingsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "nickname",
            "display_name",
            "has_usable_password",
            "age",
            "age_group",
            "marital_status",
            "has_children",
            "region",
            "income_level",
            "asset_level",
            "employment_status",
            "saving_purpose",
            "savings_goal",
            "monthly_saving",
            "preferred_term",
            "risk_tolerance",
            "joined_products",
            "joined_loans",
            "joined_savings",
        )

    def get_has_usable_password(self, obj):
        return obj.has_usable_password()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "nickname",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
        attrs["user"] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "nickname",
            "age",
            "age_group",
            "marital_status",
            "has_children",
            "region",
            "income_level",
            "asset_level",
            "employment_status",
            "saving_purpose",
            "savings_goal",
            "monthly_saving",
            "preferred_term",
            "risk_tolerance",
        )


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "author", "author_name", "content", "created_at", "updated_at", "is_owner")
        read_only_fields = ("author", "created_at", "updated_at")

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_name",
            "title",
            "content",
            "created_at",
            "updated_at",
            "comments_count",
            "comments",
            "is_owner",
        )
        read_only_fields = ("author", "created_at", "updated_at")

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.author_id == request.user.id)



