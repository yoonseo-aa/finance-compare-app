<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const error = ref("");

const form = reactive({
  username: "",
  password: "",
  email: "",
  nickname: ""
});

function cleanPayload() {
  const payload = { ...form };
  Object.keys(payload).forEach(key => {
    if (payload[key] === "" || payload[key] === null) delete payload[key];
  });
  return payload;
}

async function submit() {
  error.value = "";
  try {
    await auth.signup(cleanPayload());
    router.push("/recommend-profile");
  } catch (err) {
    error.value = err.message;
  }
}
</script>

<template>
  <main class="auth-page">
    <form class="form-panel wide auth-card" @submit.prevent="submit">
      <h1>회원가입</h1>

      <div class="form-grid signup-simple-grid">
        <label>아이디<input v-model="form.username" required></label>
        <label>비밀번호<input v-model="form.password" type="password" required minlength="8"></label>
        <label>이메일<input v-model="form.email" type="email"></label>
        <label>닉네임<input v-model="form.nickname"></label>
      </div>

      <p v-if="error" class="form-error">{{ error }}</p>
      <button class="btn primary full" type="submit">가입하고 추천 진단하기</button>
    </form>
  </main>
</template>
