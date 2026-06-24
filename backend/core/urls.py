from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("posts", views.PostViewSet, basename="posts")
router.register("comments", views.CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/signup/", views.SignupAPIView.as_view(), name="signup"),
    path("auth/login/", views.LoginAPIView.as_view(), name="login"),
    path("auth/logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("auth/social/<str:provider>/login/", views.SocialLoginURLAPIView.as_view(), name="social_login"),
    path("auth/social/<str:provider>/callback/", views.SocialCallbackAPIView.as_view(), name="social_callback"),
    path("auth/me/", views.MeAPIView.as_view(), name="me"),
    path("auth/password/", views.PasswordChangeAPIView.as_view(), name="password_change"),
    path("spot/", views.spot_prices, name="spot"),
    path("videos/", views.videos, name="videos"),
    path("search/news/", views.news_search, name="news_search"),
    path("map/config/", views.map_config, name="map_config"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("sync-finlife/", views.sync_finlife, name="sync_finlife"),
    path("stats/", views.stats, name="stats"),
    path("health/", views.health, name="health"),
]


