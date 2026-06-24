<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const saving = ref(false);
const changingPassword = ref(false);
const infoMessage = ref("");
const passwordMessage = ref("");
const error = ref("");

const form = reactive({ email: "", nickname: "" });
const passwordForm = reactive({ currentPassword: "", newPassword: "", confirmPassword: "" });
const canChangePassword = computed(() => auth.user?.has_usable_password === true);

function syncForm() {
  form.email = auth.user?.email || "";
  form.nickname = auth.user?.nickname || "";
}

async function saveBasicInfo() {
  saving.value = true;
  error.value = "";
  infoMessage.value = "";
  try {
    await auth.updateProfile({ email: form.email, nickname: form.nickname });
    syncForm();
    infoMessage.value = "기본 정보가 저장되었습니다.";
  } catch (err) {
    error.value = err.message || "기본 정보를 저장하지 못했습니다.";
  } finally {
    saving.value = false;
  }
}

async function changePassword() {
  error.value = "";
  passwordMessage.value = "";
  if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    error.value = "모든 비밀번호 항목을 입력해주세요.";
    return;
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    error.value = "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.";
    return;
  }

  changingPassword.value = true;
  try {
    const user = await apiFetch("/auth/password/", {
      method: "POST",
      body: JSON.stringify({
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      })
    });
    auth.setUser(user);
    passwordForm.currentPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
    passwordMessage.value = "비밀번호가 변경되었습니다.";
  } catch (err) {
    error.value = err.message || "비밀번호를 변경하지 못했습니다.";
  } finally {
    changingPassword.value = false;
  }
}

onMounted(async () => {
  if (!auth.user) await auth.bootstrap();
  syncForm();
});
</script>

<template>
  <main class="container account-page-local">
    <section class="account-hero-local">
      <span>MY FINPICK</span>
      <h1>나의 정보 수정</h1>
      <p>닉네임, 이메일, 비밀번호 등 계정 정보를 관리합니다.</p>
    </section>

    <p v-if="error" class="account-message-local error">{{ error }}</p>

    <section v-if="auth.user" class="account-layout-local">
      <form class="account-card-local" @submit.prevent="saveBasicInfo">
        <div class="account-card-head-local">
          <span aria-hidden="true">◉</span>
          <div><h2>기본 정보</h2><p>서비스에서 표시되는 계정 정보를 수정합니다.</p></div>
        </div>
        <label>아이디<input :value="auth.user.username" disabled></label>
        <label>이메일<input v-model="form.email" type="email" autocomplete="email"></label>
        <label>닉네임<input v-model="form.nickname" maxlength="30" autocomplete="nickname"></label>
        <p v-if="infoMessage" class="account-message-local success">{{ infoMessage }}</p>
        <div class="form-actions">
  <button class="btn primary" type="submit" :disabled="saving">
    {{ saving ? "저장 중" : "저장" }}
  </button>

  <button class="btn ghost large back-btn" type="button" @click="$router.back()">
    돌아가기
  </button>
</div>
      </form>

      <form v-if="canChangePassword" class="account-card-local" @submit.prevent="changePassword">
        <div class="account-card-head-local">
          <span aria-hidden="true">⌑</span>
          <div><h2>비밀번호 변경</h2><p>안전을 위해 현재 비밀번호를 확인합니다.</p></div>
        </div>
        <label>현재 비밀번호<input v-model="passwordForm.currentPassword" type="password" autocomplete="current-password"></label>
        <label>새 비밀번호<input v-model="passwordForm.newPassword" type="password" autocomplete="new-password"></label>
        <label>새 비밀번호 확인<input v-model="passwordForm.confirmPassword" type="password" autocomplete="new-password"></label>
        <p v-if="passwordMessage" class="account-message-local success">{{ passwordMessage }}</p>
        <button class="btn primary" type="submit" :disabled="changingPassword">{{ changingPassword ? "변경 중" : "비밀번호 변경" }}</button>
      </form>

      <article v-else class="account-card-local social-notice-local">
        <div class="account-card-head-local">
          <span aria-hidden="true">◌</span>
          <div><h2>소셜 로그인 계정</h2><p>비밀번호는 연결된 소셜 계정에서 관리합니다.</p></div>
        </div>
        <p>소셜 로그인 계정은 FinPick에서 비밀번호를 변경할 수 없습니다.</p>
      </article>
    </section>
  </main>
</template>

<style scoped>
.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}

.form-actions .btn {
  width: auto;
}

.account-page-local { min-height: calc(100vh - 72px); padding-top: 2.8rem; padding-bottom: 4rem; }
.account-hero-local { margin-bottom: 1.5rem; }
.account-hero-local > span { color: #129f9a; font-size: .82rem; font-weight: 900; letter-spacing: .04em; }
.account-hero-local h1 { color: #102a4b; font-size: 2rem; letter-spacing: -.045em; margin: .38rem 0; }
.account-hero-local p { color: var(--muted); margin: 0; }
.account-layout-local { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; align-items: start; }
.account-card-local { display: grid; gap: .85rem; border: 1px solid #dce6f2; border-radius: 16px; background: #fff; box-shadow: 0 8px 20px rgba(29,55,88,.05); padding: 1.35rem; }
.account-card-head-local { display: flex; align-items: start; gap: .75rem; margin-bottom: .2rem; }
.account-card-head-local > span { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 10px; background: #eaf3ff; color: #1d6dea; font-weight: 900; }
.account-card-head-local h2 { color: #183250; font-size: 1.15rem; margin: 0; }
.account-card-head-local p, .social-notice-local > p { color: #6b7d93; font-size: .84rem; line-height: 1.5; margin: .28rem 0 0; }
.account-card-local label { display: grid; gap: .45rem; color: #40566f; font-size: .85rem; font-weight: 850; }
.account-card-local input { border: 1px solid #d8e4f1; border-radius: 9px; background: #fbfdff; color: #183250; font: inherit; padding: .7rem .75rem; }
.account-card-local input:disabled { background: #f1f5f9; color: #718198; }
.account-card-local .btn { justify-self: start; margin-top: .25rem; }
.account-message-local { border-radius: 9px; font-size: .84rem; margin: 0; padding: .7rem .8rem; }
.account-message-local.success { background: #edf9f4; color: #168260; }
.account-message-local.error { background: #fff3f3; color: #ae3b3b; margin-bottom: 1rem; }
.social-notice-local { min-height: 170px; }
@media (max-width: 760px) { .account-page-local { padding-top: 1.75rem; } .account-layout-local { grid-template-columns: 1fr; } }
</style>
