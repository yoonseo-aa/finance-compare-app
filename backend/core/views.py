import os
from datetime import datetime

import requests

from django.db.models import Max, Q
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, FinancialProduct, Post
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
from .services import FinlifeAPIError, fetch_finlife_products, load_spot_price_data, naver_news_search, recommend_news_with_ai, seed_demo_products, youtube_search
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
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})



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
        return Response({"token": token.key, "user": UserSerializer(user).data})

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


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
        return Response(UserSerializer(user).data)


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
        return Response(UserSerializer(request.user).data)


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








