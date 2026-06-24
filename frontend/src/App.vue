<script setup>
import { onMounted } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";

import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();
const router = useRouter();

onMounted(() => auth.bootstrap());

async function logout() {
  await auth.logout();
  router.push("/");
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar balanced-topbar">
      <RouterLink class="brand header-brand" to="/">FinPick</RouterLink>
      <nav class="nav-links header-menu">
        <RouterLink to="/products">예적금</RouterLink>
        <RouterLink to="/recommendations">추천진단</RouterLink>
        <RouterLink to="/dashboard">대시보드</RouterLink>
        <RouterLink to="/spot">현물</RouterLink>
        <RouterLink to="/videos">관심 종목</RouterLink>
        <RouterLink to="/banks">은행 찾기</RouterLink>
        <RouterLink to="/community">커뮤니티</RouterLink>
      </nav>
      <div class="header-auth">
        <RouterLink v-if="auth.isAuthenticated" class="btn header-login-btn ghost" to="/mypage">마이페이지</RouterLink>
        <button v-if="auth.isAuthenticated" class="btn header-login-btn" type="button" @click="logout">로그아웃</button>
        <RouterLink v-else class="btn header-login-btn" to="/login">로그인</RouterLink>
      </div>
    </header>

    <RouterView />
  </div>
</template>
