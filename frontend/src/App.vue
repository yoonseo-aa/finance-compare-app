<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";

import ChatbotWidget from "./components/chatbot/ChatbotWidget.vue";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const mobileOpen = ref(false);
const openMenuKey = ref(null);

const menuItems = [
  {
    label: "상품",
    children: [
      { label: "예적금", path: "/products" },
      { label: "대출", path: "/products/loans" },
      { label: "연금저축", path: "/products/pension-savings" }
    ]
  },
  {
    label: "금융상품",
    children: [
      { label: "금융회사 개요", path: "/companies" },
      { label: "은행찾기", path: "/banks" }
    ]
  },
  { label: "마이금융", path: "/dashboard" },
  { label: "금은시세", path: "/gold-silver" },
  { label: "커뮤니티", path: "/community" }
];

const currentPath = computed(() => route.path);
const hasOpenDropdown = computed(() => openMenuKey.value !== null);

onMounted(() => auth.bootstrap());

function isActivePath(path) {
  if (!path) return false;
  if (path === "/products") return currentPath.value === "/products" || currentPath.value.startsWith("/products/");
  return currentPath.value === path || currentPath.value.startsWith(`${path}/`);
}

function isActiveMenu(item) {
  if (item.path) return isActivePath(item.path) || (item.path === "/gold-silver" && currentPath.value === "/spot");
  return item.children?.some(child => isActivePath(child.path));
}

function openDropdown(key) {
  openMenuKey.value = key;
}

function closeDropdown() {
  openMenuKey.value = null;
}

function toggleDropdown(key) {
  openMenuKey.value = openMenuKey.value === key ? null : key;
}

function handleNavFocusout(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) {
    closeDropdown();
  }
}

function closeMobileNav() {
  mobileOpen.value = false;
  closeDropdown();
}

async function logout() {
  await auth.logout();
  closeMobileNav();
  router.push("/");
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar finpick-topbar" @mouseleave="closeDropdown">
      <div class="header-inner">
        <RouterLink class="brand header-brand" to="/" @click="closeMobileNav">
          <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
          <span>FinPick</span>
        </RouterLink>

        <button class="mobile-menu-button" type="button" :aria-expanded="mobileOpen" aria-label="메뉴 열기" @click="mobileOpen = !mobileOpen">
          <span></span><span></span><span></span>
        </button>

        <nav class="finpick-nav" :class="{ open: mobileOpen, 'has-open-dropdown': hasOpenDropdown }" aria-label="주요 메뉴" @focusout="handleNavFocusout">
          <div
            v-for="item in menuItems"
            :key="item.label"
            class="nav-item"
            :class="{ active: isActiveMenu(item), 'has-dropdown': item.children, open: openMenuKey === item.label }"
            @mouseenter="item.children && openDropdown(item.label)"
          >
            <RouterLink v-if="item.path" class="nav-link" :to="item.path" @click="closeMobileNav">
              {{ item.label }}
            </RouterLink>
            <button
              v-else
              class="nav-link nav-trigger"
              type="button"
              :aria-expanded="openMenuKey === item.label"
              @click="toggleDropdown(item.label)"
              @focus="openDropdown(item.label)"
            >
              {{ item.label }}
            </button>
            <div v-if="item.children" class="nav-dropdown" @mouseenter="openDropdown(item.label)">
              <RouterLink v-for="child in item.children" :key="child.path" :to="child.path" @click="closeMobileNav">
                {{ child.label }}
              </RouterLink>
            </div>
          </div>
        </nav>

        <div class="header-actions finpick-header-actions">
          <RouterLink class="header-search-button" to="/videos" aria-label="검색" @click="closeMobileNav">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="10.5" cy="10.5" r="6.5"></circle>
              <path d="M16 16l5 5"></path>
            </svg>
          </RouterLink>
          <template v-if="auth.isAuthenticated">
            <RouterLink class="btn header-login-btn ghost" to="/mypage" @click="closeMobileNav">마이페이지</RouterLink>
            <button class="btn header-login-btn" type="button" @click="logout">로그아웃</button>
          </template>
          <template v-else>
            <RouterLink class="btn header-login-btn ghost" to="/login" @click="closeMobileNav">로그인</RouterLink>
            <RouterLink class="btn header-login-btn primary" to="/signup" @click="closeMobileNav">회원가입</RouterLink>
          </template>
        </div>
      </div>
    </header>

    <RouterView />
    <ChatbotWidget />
  </div>
</template>
