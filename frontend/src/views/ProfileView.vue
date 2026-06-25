<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const saving = ref(false);
const changingPassword = ref(false);
const infoMessage = ref("");
const passwordMessage = ref("");
const error = ref("");
const imageInput = ref(null);
const selectedImage = ref(null);
const imagePreview = ref("");

const form = reactive({ email: "", nickname: "" });
const passwordForm = reactive({ currentPassword: "", newPassword: "", confirmPassword: "" });
const canChangePassword = computed(() => auth.user?.has_usable_password === true);
const isSocialLogin = computed(() => auth.user?.has_usable_password === false);
const displayName = computed(() => auth.user?.display_name || auth.user?.nickname || auth.user?.username || "FinPick 사용자");
const profileImage = computed(() => imagePreview.value || auth.user?.profile_image || auth.user?.profileImage || auth.user?.avatar_url || auth.user?.avatar || "");
const profileInitial = computed(() => displayName.value.charAt(0));
const loginProvider = computed(() => {
  const username = auth.user?.username || "";
  if (username.startsWith("google_")) return "Google";
  if (username.startsWith("kakao_")) return "Kakao";
  if (username.startsWith("naver_")) return "Naver";
  return isSocialLogin.value ? "소셜" : "FinPick";
});

function syncForm() {
  form.email = auth.user?.email || "";
  form.nickname = auth.user?.nickname || "";
}

function openImagePicker() {
  imageInput.value?.click();
}

function handleImageChange(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    alert("이미지 파일만 업로드할 수 있습니다.");
    return;
  }
  selectedImage.value = file;
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value);
  imagePreview.value = URL.createObjectURL(file);
}

async function saveBasicInfo() {
  saving.value = true;
  error.value = "";
  infoMessage.value = "";
  try {
    if (selectedImage.value) {
      const formData = new FormData();
      formData.append("nickname", form.nickname);
      if (!isSocialLogin.value) formData.append("email", form.email);
      formData.append("profile_image", selectedImage.value);
      await auth.updateProfile(formData);
    } else {
      await auth.updateProfile({
        nickname: form.nickname,
        ...(isSocialLogin.value ? {} : { email: form.email })
      });
    }
    syncForm();
    selectedImage.value = null;
    if (imagePreview.value) URL.revokeObjectURL(imagePreview.value);
    imagePreview.value = "";
    infoMessage.value = "계정 정보가 저장되었습니다.";
    alert("계정 정보가 저장되었습니다.");
  } catch (err) {
    error.value = err.message || "계정 정보를 저장하지 못했습니다.";
    alert(error.value);
  } finally {
    saving.value = false;
  }
}

async function changePassword() {
  error.value = "";
  passwordMessage.value = "";
  if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    error.value = "모든 비밀번호 항목을 입력해주세요.";
    alert(error.value);
    return;
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    error.value = "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.";
    alert(error.value);
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
    alert("비밀번호가 변경되었습니다.");
  } catch (err) {
    error.value = err.message || "비밀번호를 변경하지 못했습니다.";
    alert(error.value);
  } finally {
    changingPassword.value = false;
  }
}

onMounted(async () => {
  if (!auth.user) await auth.bootstrap();
  syncForm();
});

onBeforeUnmount(() => {
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value);
});
</script>

<template>
  <main class="account-page-local">
    <section class="container account-container-local">
      <header class="account-hero-local">
        <span>MY FINPICK</span>
        <h1>계정 정보 수정</h1>
        <p>프로필 이미지, 닉네임, 이메일과 로그인 정보를 관리합니다.</p>
      </header>

      <p v-if="error" class="account-message-local error">{{ error }}</p>

      <section v-if="auth.user" class="account-layout-local">
        <form class="account-card-local profile-edit-card-local" @submit.prevent="saveBasicInfo">
          <div class="account-card-head-local">
            <span aria-hidden="true">👤</span>
            <div>
              <h2>기본 정보</h2>
              <p>서비스에 표시되는 계정 정보를 수정합니다.</p>
            </div>
          </div>

          <div class="profile-image-editor-local">
            <button class="profile-avatar-local" type="button" @click="openImagePicker">
              <img v-if="profileImage" :src="profileImage" alt="프로필 이미지">
              <span v-else>{{ profileInitial }}</span>
              <em>이미지 변경</em>
            </button>
            <div>
              <strong>{{ displayName }}</strong>
              <p>이미지를 선택하면 저장 전 미리보기가 표시됩니다.</p>
              <button class="btn ghost small" type="button" @click="openImagePicker">이미지 선택</button>
            </div>
            <input ref="imageInput" class="sr-only-local" type="file" accept="image/*" @change="handleImageChange">
          </div>

          <label>아이디<input :value="auth.user.username" disabled></label>
          <label>
            이메일
            <input v-model="form.email" type="email" autocomplete="email" :disabled="isSocialLogin">
          </label>
          <label>닉네임<input v-model="form.nickname" maxlength="30" autocomplete="nickname"></label>
          <p v-if="isSocialLogin" class="account-help-local">소셜 로그인 계정은 아이디와 이메일을 읽기 전용으로 유지합니다.</p>
          <p v-if="infoMessage" class="account-message-local success">{{ infoMessage }}</p>

          <div class="form-actions">
            <button class="btn primary" type="submit" :disabled="saving">
              {{ saving ? "저장 중" : "저장" }}
            </button>
            <button class="btn ghost" type="button" @click="$router.back()">돌아가기</button>
          </div>
        </form>

        <form v-if="canChangePassword" class="account-card-local" @submit.prevent="changePassword">
          <div class="account-card-head-local">
            <span aria-hidden="true">🔒</span>
            <div>
              <h2>비밀번호 변경</h2>
              <p>보안을 위해 현재 비밀번호를 확인합니다.</p>
            </div>
          </div>
          <label>현재 비밀번호<input v-model="passwordForm.currentPassword" type="password" autocomplete="current-password"></label>
          <label>새 비밀번호<input v-model="passwordForm.newPassword" type="password" autocomplete="new-password"></label>
          <label>새 비밀번호 확인<input v-model="passwordForm.confirmPassword" type="password" autocomplete="new-password"></label>
          <p v-if="passwordMessage" class="account-message-local success">{{ passwordMessage }}</p>
          <button class="btn primary" type="submit" :disabled="changingPassword">
            {{ changingPassword ? "변경 중" : "비밀번호 변경" }}
          </button>
        </form>

        <article v-else class="account-card-local social-notice-local">
          <div class="account-card-head-local">
            <span aria-hidden="true">🔗</span>
            <div>
              <h2>소셜 로그인 계정</h2>
              <p>{{ loginProvider }} 계정으로 로그인 중입니다.</p>
            </div>
          </div>
          <p>{{ loginProvider }} 계정으로 로그인 중입니다. FinPick에서는 비밀번호를 변경할 수 없습니다.</p>
        </article>
      </section>
    </section>
  </main>
</template>

<style scoped>
.account-page-local {
  --account-ink: #10233f;
  --account-muted: #6b7a90;
  --account-line: #dbe7f5;
  --account-blue: #2f80ed;
  min-height: calc(100vh - 72px);
  background: #f3f8fd;
}

.account-container-local {
  padding-top: 2.8rem;
  padding-bottom: 4rem;
}

.account-hero-local {
  margin-bottom: 1.5rem;
}

.account-hero-local > span {
  color: #0785c8;
  font-size: .82rem;
  font-weight: 900;
}

.account-hero-local h1 {
  color: var(--account-ink);
  font-size: clamp(2rem, 4vw, 3rem);
  margin: .38rem 0;
}

.account-hero-local p {
  color: var(--account-muted);
  margin: 0;
  font-weight: 700;
}

.account-layout-local {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr);
  gap: 1rem;
  align-items: start;
}

.account-card-local {
  display: grid;
  gap: .9rem;
  border: 1px solid var(--account-line);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(29, 55, 88, .065);
  padding: 1.35rem;
}

.account-card-head-local {
  display: flex;
  align-items: start;
  gap: .75rem;
  margin-bottom: .2rem;
}

.account-card-head-local > span {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 12px;
  background: #eaf3ff;
  color: var(--account-blue);
  font-weight: 900;
}

.account-card-head-local h2 {
  color: var(--account-ink);
  font-size: 1.18rem;
  margin: 0;
}

.account-card-head-local p,
.social-notice-local > p,
.account-help-local {
  color: var(--account-muted);
  font-size: .86rem;
  line-height: 1.5;
  margin: .28rem 0 0;
}

.profile-image-editor-local {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
  border: 1px solid #e6edf6;
  border-radius: 16px;
  background: #fbfdff;
  padding: .9rem;
}

.profile-avatar-local {
  position: relative;
  display: grid;
  place-items: center;
  width: 96px;
  height: 96px;
  border: 1px solid #cfe0f4;
  border-radius: 28px;
  background: #eaf3ff;
  color: var(--account-blue);
  font-size: 2rem;
  font-weight: 900;
  overflow: hidden;
  cursor: pointer;
}

.profile-avatar-local img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-local em {
  position: absolute;
  inset: auto 0 0;
  padding: .4rem .2rem;
  background: rgba(16, 35, 63, .72);
  color: #fff;
  font-size: .75rem;
  font-style: normal;
  opacity: 0;
  transition: opacity .16s ease;
}

.profile-avatar-local:hover em {
  opacity: 1;
}

.profile-image-editor-local strong {
  color: var(--account-ink);
  font-size: 1.08rem;
}

.profile-image-editor-local p {
  color: var(--account-muted);
  margin: .25rem 0 .55rem;
  font-size: .86rem;
  font-weight: 700;
}

.sr-only-local {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.account-card-local label {
  display: grid;
  gap: .45rem;
  color: #40566f;
  font-size: .86rem;
  font-weight: 850;
}

.account-card-local input {
  border: 1px solid #d8e4f1;
  border-radius: 10px;
  background: #fbfdff;
  color: var(--account-ink);
  font: inherit;
  padding: .72rem .78rem;
}

.account-card-local input:disabled {
  background: #f1f5f9;
  color: #718198;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: .7rem;
  margin-top: .3rem;
}

.account-message-local {
  border-radius: 10px;
  font-size: .86rem;
  margin: 0;
  padding: .75rem .85rem;
  font-weight: 800;
}

.account-message-local.success {
  background: #edf9f4;
  color: #168260;
}

.account-message-local.error {
  background: #fff3f3;
  color: #ae3b3b;
  margin-bottom: 1rem;
}

.social-notice-local {
  min-height: 180px;
}

@media (max-width: 820px) {
  .account-layout-local,
  .profile-image-editor-local {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .account-container-local {
    padding-top: 1.8rem;
  }

  .form-actions {
    display: grid;
  }
}
</style>
