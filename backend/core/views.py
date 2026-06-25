import os
from datetime import datetime

import requests

from django.db.models import Count, Max, Q
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, FavoriteLoan, FavoriteSavings, FinancialProduct, Post
from .permissions import IsOwnerOrReadOnly
from .dashboard import build_dashboard
from .recommendation import recommend_products
from .serializers import (
    CommentSerializer,
    LoginSerializer,
    PostSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProfileUpdateSerializer,
    SignupSerializer,
    UserSerializer,
)
from .services import FinlifeAPIError, explain_recommendations_with_ai, fetch_finlife_loans, fetch_finlife_products, fetch_finlife_savings_products, load_spot_price_data, naver_news_search, recommend_news_with_ai, seed_demo_products, youtube_search
from .social_auth import authenticate_social, build_authorization_url


def ensure_demo_data():
    if not FinancialProduct.objects.exists():
        seed_demo_products()


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user, context={"request": request}).data}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user, context={"request": request}).data})



class SocialLoginURLAPIView(APIView):
    def get(self, request, provider):
        redirect_uri = request.query_params.get("redirect_uri")
        return Response(build_authorization_url(provider, redirect_uri))


class SocialCallbackAPIView(APIView):
    def post(self, request, provider):
        code = request.data.get("code")
        if not code:
            return Response({"detail": "Authorization code is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate_social(
            provider=provider,
            code=code,
            redirect_uri=request.data.get("redirect_uri"),
            state=request.data.get("state"),
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user, context={"request": request}).data})

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.has_usable_password():
            return Response(
                {"detail": "소셜 로그인 계정은 FinPick에서 비밀번호를 변경할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_password = request.data.get("current_password", "")
        new_password = request.data.get("new_password", "")
        if not current_password or not new_password:
            return Response({"detail": "현재 비밀번호와 새 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 8:
            return Response({"detail": "새 비밀번호는 8자 이상이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(current_password):
            return Response({"detail": "현재 비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(UserSerializer(user, context={"request": request}).data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialProduct.objects.prefetch_related("options").all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        ensure_demo_data()
        queryset = super().get_queryset().annotate(max_rate=Max("options__intr_rate2"))
        bank = self.request.query_params.get("bank")
        query = self.request.query_params.get("q")
        sort = self.request.query_params.get("sort", "rate")

        if bank:
            queryset = queryset.filter(bank_name=bank)
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(bank_name__icontains=query))
        if sort == "name":
            return queryset.order_by("name")
        return queryset.order_by("-max_rate", "bank_name")

    @action(detail=False)
    def banks(self, request):
        ensure_demo_data()
        banks = FinancialProduct.objects.values_list("bank_name", flat=True).distinct().order_by("bank_name")
        return Response(list(banks))

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        product = self.get_object()
        if request.method == "DELETE":
            request.user.joined_products.remove(product)
        else:
            request.user.joined_products.add(product)
        return Response(UserSerializer(request.user, context={"request": request}).data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("comments__author").all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permission() for permission in self.permission_classes]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)
        return Response(PostSerializer(post, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "post").all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(["GET"])
def spot_prices(request):
    asset = request.query_params.get("asset", "gold")
    if asset not in {"gold", "silver"}:
        asset = "gold"

    spot_data = load_spot_price_data(asset)
    rows = spot_data["rows"]
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    error = spot_data.get("error", "")

    try:
        if start:
            datetime.fromisoformat(start)
            rows = [row for row in rows if row["date"] >= start]
        if end:
            datetime.fromisoformat(end)
            rows = [row for row in rows if row["date"] <= end]
        if start and end and start > end:
            error = "시작일은 종료일보다 늦을 수 없습니다."
            rows = []
    except ValueError:
        error = "날짜 형식이 올바르지 않습니다."
        rows = []

    return Response({
        "asset": asset,
        "rows": rows,
        "error": error,
        "source": spot_data["source"],
        "symbol": spot_data["symbol"],
        "exchange_rate": spot_data.get("exchange_rate"),
        "currency": spot_data.get("currency", "KRW"),
        "unit": spot_data.get("unit", "원/g"),
        "units": spot_data.get("units", {"gram": "원/g", "don": "원/돈", "oz": "원/oz"}),
        "is_live": spot_data["is_live"],
    })


@api_view(["GET"])
def videos(request):
    query = request.query_params.get("q", "")
    try:
        results = youtube_search(query) if query else []
        return Response({"query": query, "results": results})
    except Exception:
        return Response(
            {
                "query": query,
                "results": [],
                "error": "Video search is temporarily unavailable. Please check the YouTube API key.",
            }
        )


@api_view(["GET"])
def news_search(request):
    query = request.query_params.get("query", "").strip()
    if not query:
        return Response({"query": query, "results": [], "articles": [], "used_ai": False})
    try:
        articles, used_ai = recommend_news_with_ai(query, naver_news_search(query))
        return Response({"query": query, "results": articles, "articles": articles, "used_ai": used_ai})
    except requests.RequestException:
        return Response({"query": query, "results": [], "articles": [], "used_ai": False, "error": "뉴스를 불러오지 못했습니다. 잠시 후 다시 시도해주세요."})


@api_view(["GET"])
def map_config(request):
    return Response({"kakao_js_key": os.getenv("KAKAO_JS_KEY", "")})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommendations(request):
    ensure_demo_data()
    items = recommend_products(request.user)
    data = [
        {
            "product": ProductListSerializer(item["product"]).data,
            "option": {
                "id": item["option"].id,
                "save_term": item["option"].save_term,
                "intr_rate": item["option"].intr_rate,
                "intr_rate2": item["option"].intr_rate2,
                "rate_type": item["option"].rate_type,
            },
            "score": item["score"],
            "reasons": item["reasons"],
        }
        for item in items
    ]
    return Response(data)


@api_view(["POST"])
def recommendation_ai_explain(request):
    recommendation_type = request.data.get("recommendation_type", "deposit")
    if recommendation_type not in {"deposit", "loan"}:
        return Response({"detail": "recommendation_type은 deposit 또는 loan이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

    recommendations = request.data.get("recommendations") or []
    if not isinstance(recommendations, list):
        return Response({"detail": "recommendations는 배열이어야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

    result = explain_recommendations_with_ai(
        recommendation_type=recommendation_type,
        user_conditions=request.data.get("user_conditions") or {},
        recommendations=recommendations[:5],
    )
    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    ensure_demo_data()
    return Response(build_dashboard(request.user))


@api_view(["POST"])
@permission_classes([IsAdminUser])
def sync_finlife(request):
    try:
        deposit_count = fetch_finlife_products("deposit")
        saving_count = fetch_finlife_products("saving")
    except FinlifeAPIError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"count": deposit_count + saving_count})



@api_view(["GET"])
def company_overview(request):
    ensure_demo_data()
    products = FinancialProduct.objects.prefetch_related("options").annotate(max_rate=Max("options__intr_rate2"))

    bank_rows = FinancialProduct.objects.values("bank_name").annotate(
        product_count=Count("id", distinct=True),
        deposit_count=Count("id", filter=Q(product_type="deposit"), distinct=True),
        saving_count=Count("id", filter=Q(product_type="saving"), distinct=True),
        best_rate=Max("options__intr_rate2"),
    ).order_by("-product_count", "bank_name")

    top_products = products.order_by("-max_rate", "bank_name", "name")[:5]
    highest_rate = products.aggregate(value=Max("options__intr_rate2"))["value"] or 0

    return Response({
        "summary": {
            "products": products.count(),
            "banks": bank_rows.count(),
            "deposit_products": products.filter(product_type="deposit").count(),
            "saving_products": products.filter(product_type="saving").count(),
            "highest_rate": highest_rate,
        },
        "banks": [
            {
                "bank_name": row["bank_name"],
                "product_count": row["product_count"],
                "deposit_count": row["deposit_count"],
                "saving_count": row["saving_count"],
                "best_rate": row["best_rate"] or 0,
            }
            for row in bank_rows[:8]
        ],
        "top_products": ProductListSerializer(top_products, many=True).data,
    })

@api_view(["GET"])
def loans(request):
    loan_type = request.query_params.get("type", "credit")
    try:
        loan_types = ("mortgage", "rent", "credit") if loan_type == "all" else (loan_type,)
        results = [item for current_type in loan_types for item in fetch_finlife_loans(current_type)]
        query = request.query_params.get("q", "").strip().lower()
        bank = request.query_params.get("bank", "").strip()
        code = request.query_params.get("code", "").strip()
        sort = request.query_params.get("sort", "rate")

        if query:
            results = [
                item for item in results
                if query in item["name"].lower() or query in item["bank_name"].lower()
            ]
        if bank:
            results = [item for item in results if item["bank_name"] == bank]
        if code:
            results = [item for item in results if item["product_code"] == code]

        if sort == "bank":
            results.sort(key=lambda item: (item["bank_name"], item["name"]))
        elif sort == "name":
            results.sort(key=lambda item: item["name"])
        else:
            results.sort(key=lambda item: item["rate_min"] if item["rate_min"] > 0 else float("inf"))

        return Response({"type": loan_type, "results": results})
    except FinlifeAPIError as exc:
        return Response({"type": loan_type, "results": [], "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except requests.RequestException:
        return Response({"type": loan_type, "results": [], "error": "대출 상품 정보를 불러오지 못했습니다."}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def loan_join(request, loan_type, code):
    if loan_type not in {"mortgage", "rent", "credit"}:
        return Response({"detail": "지원하지 않는 대출 유형입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        FavoriteLoan.objects.filter(user=request.user, loan_type=loan_type, product_code=code).delete()
        return Response(UserSerializer(request.user).data)

    loan_type_labels = {
        "mortgage": "주택담보대출",
        "rent": "전세자금대출",
        "credit": "개인신용대출",
    }
    payload = request.data or {}
    name = (payload.get("name") or "").strip()
    bank_name = (payload.get("bank_name") or "").strip()
    if not name or not bank_name:
        return Response({"detail": "대출 상품명과 금융회사명이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    rate_min = payload.get("rate_min")
    if rate_min in ("", None):
        rate_min = None

    FavoriteLoan.objects.update_or_create(
        user=request.user,
        loan_type=loan_type,
        product_code=code,
        defaults={
            "name": name,
            "bank_name": bank_name,
            "loan_type_label": payload.get("loan_type_label") or loan_type_labels[loan_type],
            "rate_min": rate_min,
            "loan_limit": payload.get("loan_limit") or "",
            "repay_type": payload.get("repay_type") or "",
            "join_member": payload.get("join_member") or "",
        },
    )
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
def savings(request):
    try:
        results = fetch_finlife_savings_products()
        query = request.query_params.get("q", "").strip().lower()
        bank = request.query_params.get("bank", "").strip()
        code = request.query_params.get("code", "").strip()
        sort = request.query_params.get("sort", "rate")

        if query:
            results = [
                item for item in results
                if query in item["name"].lower() or query in item["bank_name"].lower()
            ]
        if bank:
            results = [item for item in results if item["bank_name"] == bank]
        if code:
            results = [item for item in results if item["product_code"] == code]

        if sort == "bank":
            results.sort(key=lambda item: (item["bank_name"], item["name"]))
        elif sort == "name":
            results.sort(key=lambda item: item["name"])
        else:
            results.sort(key=lambda item: item["rate_value"], reverse=True)

        return Response({"results": results})
    except FinlifeAPIError as exc:
        return Response({"results": [], "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except requests.RequestException:
        return Response({"results": [], "error": "저축상품 정보를 불러오지 못했습니다."}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def savings_join(request, code):
    if request.method == "DELETE":
        FavoriteSavings.objects.filter(user=request.user, product_code=code).delete()
        return Response(UserSerializer(request.user).data)

    payload = request.data or {}
    name = (payload.get("name") or "").strip()
    bank_name = (payload.get("bank_name") or "").strip()
    if not name or not bank_name:
        return Response({"detail": "저축상품명과 금융회사명이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    rate_value = payload.get("rate_value")
    if rate_value in ("", None):
        rate_value = None

    FavoriteSavings.objects.update_or_create(
        user=request.user,
        product_code=code,
        defaults={
            "name": name,
            "bank_name": bank_name,
            "product_type_label": payload.get("product_type_label") or "저축상품",
            "product_subtype": payload.get("product_subtype") or "",
            "rate_value": rate_value,
            "rate_label": payload.get("rate_label") or "수익률",
            "join_way": payload.get("join_way") or "",
            "join_member": payload.get("join_member") or "",
            "special_condition": payload.get("special_condition") or "",
            "etc_note": payload.get("etc_note") or "",
        },
    )
    return Response(UserSerializer(request.user).data)


@api_view(["GET"])
def stats(request):
    ensure_demo_data()
    return Response(
        {
            "products": FinancialProduct.objects.count(),
            "banks": FinancialProduct.objects.values("bank_name").distinct().count(),
            "posts": Post.objects.count(),
            "featured": ProductListSerializer(
                FinancialProduct.objects.prefetch_related("options").annotate(max_rate=Max("options__intr_rate2")).order_by("-max_rate")[:3],
                many=True,
            ).data,
        }
    )


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
