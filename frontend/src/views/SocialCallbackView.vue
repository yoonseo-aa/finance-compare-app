<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const message = ref("소셜 로그인 처리 중입니다.");
const error = ref("");

onMounted(async () => {
  const provider = route.params.provider;
  const code = route.query.code;
  const state = route.query.state;
  const providerError = route.query.error;

  if (providerError) {
    error.value = `소셜 로그인 요청이 취소되었습니다. (${providerError})`;
    return;
  }

  if (!code) {
    error.value = "인증 코드가 없습니다.";
    return;
  }

  const savedState = sessionStorage.getItem(`finpick-social-state-${provider}`);
  if (savedState && state && savedState !== state) {
    error.value = "소셜 로그인 상태 값이 일치하지 않습니다.";
    return;
  }

  try {
    await auth.completeSocialLogin(provider, { code, state });
    sessionStorage.removeItem(`finpick-social-state-${provider}`);
    message.value = "로그인되었습니다.";
    router.replace(route.query.next || "/dashboard");
  } catch (err) {
    error.value = err.message;
  }
});
</script>

<template>
  <main class="auth-page">
    <section class="form-panel">
      <h1>소셜 로그인</h1>
      <p v-if="!error" class="muted">{{ message }}</p>
      <p v-else class="form-error">{{ error }}</p>
      <RouterLink v-if="error" class="btn primary full" to="/login">로그인으로 돌아가기</RouterLink>
    </section>
  </main>
</template>
