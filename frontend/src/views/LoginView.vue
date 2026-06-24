<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const form = reactive({ username: "", password: "" });
const error = ref("");
const socialLoading = ref("");

async function submit() {
  error.value = "";
  try {
    await auth.login(form);
    router.push(route.query.next || "/");
  } catch (err) {
    error.value = err.message;
  }
}

async function socialLogin(provider) {
  error.value = "";
  socialLoading.value = provider;
  try {
    await auth.loginWithSocial(provider);
  } catch (err) {
    error.value = err.message;
    socialLoading.value = "";
  }
}
</script>

<template>
  <main class="auth-page">
    <form class="form-panel" @submit.prevent="submit">
      <h1>로그인</h1>
      <label>아이디<input v-model="form.username" required></label>
      <label>비밀번호<input v-model="form.password" type="password" required></label>
      <p v-if="error" class="form-error">{{ error }}</p>
      <button class="btn primary full" type="submit">로그인</button>

      <div class="social-divider"><span>또는 소셜 계정으로 계속하기</span></div>
      <div class="social-buttons">
        <button class="social-btn kakao" type="button" :disabled="Boolean(socialLoading)" @click="socialLogin('kakao')">
          Kakao
        </button>
        <button class="social-btn google" type="button" :disabled="Boolean(socialLoading)" @click="socialLogin('google')">
          Google
        </button>
        <button class="social-btn naver" type="button" :disabled="Boolean(socialLoading)" @click="socialLogin('naver')">
          Naver
        </button>
      </div>

      <p class="muted">계정이 없다면 <RouterLink to="/signup">회원가입</RouterLink></p>
    </form>
  </main>
</template>
