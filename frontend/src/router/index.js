import { createRouter, createWebHistory } from "vue-router";

import { getToken } from "../api/client";
import BankSearchView from "../views/BankSearchView.vue";
import CommunityView from "../views/CommunityView.vue";
import CommunityWriteView from "../views/CommunityWriteView.vue";
import CommunityDetailView from "../views/CommunityDetailView.vue";
import DashboardView from "../views/DashboardView.vue";
import FavoritesView from "../views/FavoritesView.vue";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import LoanDetailView from "../views/LoanDetailView.vue";
import MyPageView from "../views/MyPageView.vue";
import ProductDetailView from "../views/ProductDetailView.vue";
import ProductsView from "../views/ProductsView.vue";
import ProfileView from "../views/ProfileView.vue";
import RecommendationProfileView from "../views/RecommendationProfileView.vue";
import RecommendationsView from "../views/RecommendationsView.vue";
import SearchResultsView from "../views/SearchResultsView.vue";
import SignupView from "../views/SignupView.vue";
import SocialCallbackView from "../views/SocialCallbackView.vue";
import SpotView from "../views/SpotView.vue";
import VideoDetailView from "../views/VideoDetailView.vue";
import VideosView from "../views/VideosView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/search", name: "search", component: SearchResultsView },
    { path: "/products", name: "products", component: ProductsView },
    { path: "/products/loan/:type/:code", name: "loan-detail", component: LoanDetailView },
    { path: "/products/:id", name: "product-detail", component: ProductDetailView },
    { path: "/favorites", name: "favorites", component: FavoritesView, meta: { requiresAuth: true } },
    { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { requiresAuth: true } },
    { path: "/spot", name: "spot", component: SpotView },
    { path: "/videos", name: "videos", component: VideosView },
    { path: "/videos/:id", name: "video-detail", component: VideoDetailView },
    { path: "/banks", name: "banks", component: BankSearchView },
    { path: "/community", name: "Community", component: CommunityView },
    { path: "/community/write", name: "CommunityWrite", component: CommunityWriteView },
    { path: "/community/:id", name: "CommunityDetail", component: CommunityDetailView },
    { path: "/login", name: "login", component: LoginView },
    { path: "/signup", name: "signup", component: SignupView },
    { path: "/social/callback/:provider", name: "social-callback", component: SocialCallbackView },
    { path: "/mypage", name: "mypage", component: MyPageView, meta: { requiresAuth: true } },
    { path: "/profile", name: "profile", component: ProfileView, meta: { requiresAuth: true } },
    { path: "/recommend-profile", name: "recommend-profile", component: RecommendationProfileView, meta: { requiresAuth: true } },
    { path: "/recommendations", name: "recommendations", component: RecommendationsView }
  ],
  scrollBehavior: () => ({ top: 0 })
});

router.beforeEach(to => {
  if (to.meta.requiresAuth && !getToken()) {
    return { name: "login", query: { next: to.fullPath } };
  }
  return true;
});

export default router;
