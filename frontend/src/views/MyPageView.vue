<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { useAuthStore } from "../stores/auth";
import PageHeader from "../components/PageHeader.vue";

const auth = useAuthStore();
const imageInput = ref(null);
const selectedImage = ref(null);
const imagePreview = ref("");
const imageSaving = ref(false);

const purposeLabels = {
  emergency: "비상금 준비형",
  housing: "주거/내 집 마련형",
  education: "교육/자녀 준비형",
  retirement: "노후 준비형",
  travel: "여행/목돈 마련형"
};
const riskLabels = { stable: "안정형", balanced: "균형형", aggressive: "수익형" };
const ageLabels = { child: "어린이", youth: "청년", middle: "중장년", senior: "시니어" };
const employmentLabels = {
  student: "학생",
  employee: "직장인",
  salary: "직장인",
  self_employed: "자영업자",
  retired: "은퇴/퇴직"
};

const menuItems = [
  { to: "/profile", icon: "👤", label: "정보 관리", title: "계정 정보 수정", description: "닉네임과 프로필 이미지를 관리합니다." },
  { to: "/recommend-profile", icon: "🧭", label: "추천", title: "추천 프로필 입력", description: "나에게 맞는 추천 조건을 설정합니다." },
  { to: "/recommendations", icon: "🏦", label: "추천 결과", title: "맞춤 추천 결과", description: "추천받은 예적금 상품을 확인합니다." },
  { to: "/dashboard", icon: "📊", label: "분석", title: "내 금융 분석", description: "목표 달성 가능성과 예상 금액을 확인합니다." },
  { to: "/favorites", icon: "♥", label: "관심 상품", title: "관심 상품", description: "저장한 상품을 다시 비교합니다." }
];

const user = computed(() => auth.user || {});
const displayName = computed(() => user.value.display_name || user.value.nickname || user.value.username || "FinPick 사용자");
const profileImage = computed(() => imagePreview.value || user.value.profile_image || user.value.profileImage || user.value.avatar_url || user.value.avatar || "");
const profileInitial = computed(() => displayName.value.charAt(0));
const favoriteCount = computed(() => user.value.joined_products?.length || 0);
const recommendationComplete = computed(() => Boolean(user.value.saving_purpose && user.value.risk_tolerance));
const recommendationProfile = computed(() => labelFor(user.value.saving_purpose, purposeLabels, "입력 전"));
const riskType = computed(() => labelFor(user.value.risk_tolerance, riskLabels, "미설정"));
const userTags = computed(() => [
  labelFor(user.value.age_group, ageLabels, ""),
  labelFor(user.value.employment_status, employmentLabels, ""),
  riskType.value !== "미설정" ? riskType.value : ""
].filter(Boolean).slice(0, 3));
const summaryCards = computed(() => [
  { label: "관심 상품", value: `${favoriteCount.value}개`, to: "/favorites" },
  { label: "추천 진단", value: recommendationComplete.value ? "완료" : "입력 전", to: "/recommend-profile" },
  { label: "추천 프로필", value: recommendationProfile.value, to: "/recommend-profile" }
]);

function labelFor(value, labels, fallback = "입력 전") {
  if (value === null || value === undefined || value === "") return fallback;
  return labels[value] || String(value);
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

async function saveProfileImage() {
  if (!selectedImage.value) return;
  imageSaving.value = true;
  try {
    const formData = new FormData();
    formData.append("profile_image", selectedImage.value);
    await auth.updateProfile(formData);
    selectedImage.value = null;
    if (imagePreview.value) URL.revokeObjectURL(imagePreview.value);
    imagePreview.value = "";
    alert("프로필 이미지가 저장되었습니다.");
  } catch (err) {
    alert(err.message || "프로필 이미지를 저장하지 못했습니다.");
  } finally {
    imageSaving.value = false;
  }
}

onMounted(() => auth.bootstrap());
onBeforeUnmount(() => {
  if (imagePreview.value) URL.revokeObjectURL(imagePreview.value);
});
</script>

<template>
  <main class="mypage-page-local">
    <section class="container mypage-container-local">
      <PageHeader
        eyebrow="MY FINPICK"
        title="마이페이지"
        description="내 정보와 추천 진단, 관심 상품을 한곳에서 관리합니다."
      />

      <section v-if="auth.user" class="profile-card-local">
        <div class="profile-main-local">
          <div class="profile-avatar-wrap-local">
            <button class="profile-avatar-local" type="button" @click="openImagePicker">
              <img v-if="profileImage" :src="profileImage" alt="프로필 이미지">
              <span v-else>{{ profileInitial }}</span>
              <em>이미지 변경</em>
            </button>
            <input ref="imageInput" class="sr-only-local" type="file" accept="image/*" @change="handleImageChange">
            <button
              v-if="selectedImage"
              class="btn primary image-save-local"
              type="button"
              :disabled="imageSaving"
              @click="saveProfileImage"
            >
              {{ imageSaving ? "저장 중" : "이미지 저장" }}
            </button>
          </div>

          <div class="profile-copy-local">
            <span class="profile-kicker-local">내 정보</span>
            <h2>{{ displayName }}</h2>
            <div class="profile-tags-local">
              <span v-for="tag in userTags" :key="tag">{{ tag }}</span>
              <span v-if="!userTags.length">추천 정보 입력 전</span>
            </div>
            <p>추천 프로필 <strong>{{ recommendationProfile }}</strong></p>
            <RouterLink v-if="!recommendationComplete" class="btn primary recommend-cta-local" to="/recommend-profile">
              추천 프로필 입력하기
            </RouterLink>
          </div>

          <RouterLink class="btn ghost edit-profile-btn-local" to="/profile">수정하기</RouterLink>
        </div>

        <div class="profile-summary-grid-local">
          <RouterLink v-for="card in summaryCards" :key="card.label" :to="card.to" class="summary-card-local">
            <span>{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
          </RouterLink>
        </div>
      </section>

      <section v-if="auth.user" class="mypage-menu-section-local">
        <div class="section-title-local">
          <h2>서비스 메뉴</h2>
          <p>필요한 금융 기능으로 바로 이동하세요.</p>
        </div>

        <div class="mypage-menu-grid-local">
          <RouterLink v-for="item in menuItems" :key="item.to" class="mypage-menu-card-local" :to="item.to">
            <span class="menu-icon-local" aria-hidden="true">{{ item.icon }}</span>
            <span class="menu-copy-local">
              <em>{{ item.label }}</em>
              <strong>{{ item.title }}</strong>
              <small>{{ item.description }}</small>
            </span>
            <b aria-hidden="true">›</b>
          </RouterLink>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.mypage-page-local {
  --my-ink: #10233f;
  --my-muted: #6b7a90;
  --my-line: #dbe7f5;
  --my-blue: #2f80ed;
  --my-soft: #f3f8fd;
  min-height: calc(100vh - 72px);
  background: var(--my-soft);
}

.mypage-container-local {
  padding-top: 2.8rem;
  padding-bottom: 4rem;
}

.mypage-hero-local {
  display: grid;
  gap: .45rem;
  margin-bottom: 1.35rem;
}

.mypage-hero-local > span,
.profile-kicker-local {
  color: #0785c8;
  font-size: .84rem;
  font-weight: 900;
}

.mypage-hero-local h1 {
  margin: 0;
  color: var(--my-ink);
  font-size: clamp(2rem, 4.6vw, 3.35rem);
  line-height: 1.12;
}

.mypage-hero-local p {
  margin: 0;
  color: var(--my-muted);
  font-weight: 700;
}

.profile-card-local {
  display: grid;
  gap: 1.15rem;
  border: 1px solid var(--my-line);
  border-radius: 22px;
  background: #fff;
  padding: clamp(1.25rem, 3vw, 2rem);
  box-shadow: 0 18px 42px rgba(29, 68, 120, .08);
}

.profile-main-local {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr) auto;
  gap: 1.25rem;
  align-items: center;
}

.profile-avatar-wrap-local {
  display: grid;
  gap: .65rem;
  justify-items: center;
}

.profile-avatar-local {
  position: relative;
  display: grid;
  place-items: center;
  width: 112px;
  height: 112px;
  border: 1px solid #cfe0f4;
  border-radius: 34px;
  background: #eaf3ff;
  color: var(--my-blue);
  font-size: 2.4rem;
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
  padding: .45rem .2rem;
  background: rgba(16, 35, 63, .72);
  color: #fff;
  font-size: .78rem;
  font-style: normal;
  opacity: 0;
  transition: opacity .16s ease;
}

.profile-avatar-local:hover em {
  opacity: 1;
}

.image-save-local {
  min-height: 34px;
  border-radius: 10px;
  font-size: .84rem;
}

.sr-only-local {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.profile-copy-local {
  display: grid;
  gap: .55rem;
  min-width: 0;
}

.profile-copy-local h2 {
  margin: 0;
  color: var(--my-ink);
  font-size: clamp(1.55rem, 3vw, 2.2rem);
  line-height: 1.2;
}

.profile-tags-local {
  display: flex;
  flex-wrap: wrap;
  gap: .45rem;
}

.profile-tags-local span {
  border-radius: 999px;
  background: #edf5ff;
  color: #2368c9;
  padding: .32rem .65rem;
  font-size: .84rem;
  font-weight: 900;
}

.profile-copy-local p {
  margin: 0;
  color: var(--my-muted);
  font-weight: 800;
}

.profile-copy-local p strong {
  color: var(--my-ink);
}

.edit-profile-btn-local,
.recommend-cta-local {
  border-radius: 12px;
}

.edit-profile-btn-local {
  align-self: start;
  background: #fff;
}

.recommend-cta-local {
  width: fit-content;
  min-height: 42px;
}

.profile-summary-grid-local {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .75rem;
}

.summary-card-local {
  display: grid;
  gap: .3rem;
  border: 1px solid #e5eef8;
  border-radius: 16px;
  background: #fbfdff;
  padding: .95rem;
  color: inherit;
  text-decoration: none;
}

.summary-card-local span {
  color: var(--my-muted);
  font-size: .84rem;
  font-weight: 800;
}

.summary-card-local strong {
  color: var(--my-ink);
  font-size: 1.08rem;
  line-height: 1.35;
}

.mypage-menu-section-local {
  display: grid;
  gap: 1rem;
  margin-top: 1.5rem;
}

.section-title-local {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
}

.section-title-local h2 {
  margin: 0;
  color: var(--my-ink);
  font-size: 1.45rem;
}

.section-title-local p {
  margin: 0;
  color: var(--my-muted);
  font-weight: 700;
}

.mypage-menu-grid-local {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .9rem;
}

.mypage-menu-card-local {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: .85rem;
  align-items: center;
  border: 1px solid var(--my-line);
  border-radius: 18px;
  background: #fff;
  padding: 1rem;
  color: inherit;
  text-decoration: none;
  box-shadow: 0 10px 28px rgba(31, 44, 71, .055);
  transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
}

.mypage-menu-card-local:hover {
  transform: translateY(-3px);
  border-color: rgba(47, 128, 237, .32);
  box-shadow: 0 18px 38px rgba(31, 44, 71, .12);
}

.menu-icon-local {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: #edf5ff;
  color: var(--my-blue);
  font-size: 1.25rem;
}

.menu-copy-local {
  display: grid;
  gap: .18rem;
  min-width: 0;
}

.menu-copy-local em {
  color: #0785c8;
  font-size: .8rem;
  font-style: normal;
  font-weight: 900;
}

.menu-copy-local strong {
  color: var(--my-ink);
  font-size: 1.04rem;
}

.menu-copy-local small {
  color: var(--my-muted);
  line-height: 1.45;
  font-weight: 700;
}

.mypage-menu-card-local b {
  color: #9aa7b8;
  font-size: 1.6rem;
  line-height: 1;
}

@media (max-width: 920px) {
  .profile-main-local,
  .section-title-local,
  .mypage-menu-grid-local {
    grid-template-columns: 1fr;
  }

  .edit-profile-btn-local {
    width: fit-content;
  }
}

@media (max-width: 640px) {
  .mypage-container-local {
    padding-top: 1.8rem;
  }

  .profile-summary-grid-local {
    grid-template-columns: 1fr;
  }

  .mypage-menu-card-local {
    grid-template-columns: 42px minmax(0, 1fr) auto;
    padding: .9rem;
  }

  .menu-icon-local {
    width: 42px;
    height: 42px;
    border-radius: 14px;
  }
}
</style>
