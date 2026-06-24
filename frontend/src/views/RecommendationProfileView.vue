<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const error = ref("");
const saving = ref(false);

const form = reactive({
  age_group: auth.user?.age_group || "",
  marital_status: auth.user?.marital_status || "",
  has_children: auth.user?.has_children ?? null,
  region: auth.user?.region || "",
  income_level: auth.user?.income_level || "",
  asset_level: auth.user?.asset_level || "",
  employment_status: auth.user?.employment_status || "",
  saving_purpose: auth.user?.saving_purpose || "",
  risk_tolerance: auth.user?.risk_tolerance || "stable",
  savings_goal: auth.user?.savings_goal || 1000000,
  monthly_saving: auth.user?.monthly_saving || 400000,
  preferred_term: auth.user?.preferred_term || 12
});

async function submit() {
  error.value = "";
  saving.value = true;
  try {
    await auth.updateProfile(form);
    router.push("/recommendations");
  } catch (err) {
    error.value = err.message;
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <main class="container recommend-flow-page">
    <section class="flow-hero">
      <div>
        <span class="form-eyebrow">STEP 2</span>
        <h1>예적금 추천 진단</h1>
        <p>현재 상황을 입력하면 금리, 기간, 생애주기, 목적을 함께 계산해 추천 점수와 이유를 보여드립니다.</p>
      </div>
      <RouterLink class="btn ghost" to="/recommendations">결과 먼저 보기</RouterLink>
    </section>

    <form class="content-panel recommend-profile-form" @submit.prevent="submit">
      <section>
        <h2>나의 현재 상황</h2>
        <div class="form-grid signup-simple-grid">
          <label>나이대
            <select v-model="form.age_group">
              <option value="">선택 안 함</option>
              <option value="child">어린이</option>
              <option value="youth">청년</option>
              <option value="middle">중장년</option>
              <option value="senior">시니어</option>
            </select>
          </label>
          <label>결혼 유무
            <select v-model="form.marital_status">
              <option value="">선택 안 함</option>
              <option value="single">미혼</option>
              <option value="married">기혼</option>
            </select>
          </label>
          <label>자녀 유무
            <select v-model="form.has_children">
              <option :value="null">선택 안 함</option>
              <option :value="true">있음</option>
              <option :value="false">없음</option>
            </select>
          </label>
          <label>지역<input v-model="form.region" placeholder="예: 서울, 부산, 경남"></label>
          <label>소득
            <select v-model="form.income_level">
              <option value="">선택 안 함</option>
              <option value="low">낮음</option>
              <option value="middle">보통</option>
              <option value="high">높음</option>
            </select>
          </label>
          <label>재산
            <select v-model="form.asset_level">
              <option value="">선택 안 함</option>
              <option value="low">적음</option>
              <option value="middle">보통</option>
              <option value="high">많음</option>
            </select>
          </label>
          <label>직업/상태
            <select v-model="form.employment_status">
              <option value="">선택 안 함</option>
              <option value="student">학생</option>
              <option value="employee">직장인</option>
              <option value="self_employed">자영업자</option>
              <option value="retired">은퇴/퇴직</option>
            </select>
          </label>
          <label>저축 목적
            <select v-model="form.saving_purpose">
              <option value="">선택 안 함</option>
              <option value="emergency">비상금</option>
              <option value="housing">주거/내 집 마련</option>
              <option value="education">교육/자녀</option>
              <option value="retirement">노후 준비</option>
              <option value="travel">여행/목돈</option>
            </select>
          </label>
          <label>성향
            <select v-model="form.risk_tolerance">
              <option value="stable">안정형</option>
              <option value="balanced">균형형</option>
              <option value="aggressive">수익형</option>
            </select>
          </label>
        </div>
      </section>

      <section>
        <h2>저축 기준</h2>
        <div class="form-grid signup-simple-grid">
          <label>목표 금액<input v-model.number="form.savings_goal" type="number" min="0"></label>
          <label>월 저축 가능 금액<input v-model.number="form.monthly_saving" type="number" min="0"></label>
          <label>선호 기간<input v-model.number="form.preferred_term" type="number" min="1"></label>
        </div>
      </section>

      <p v-if="error" class="form-error">{{ error }}</p>
      <div class="form-actions-row">
        <button class="btn primary large" type="submit" :disabled="saving">추천 점수 계산하기</button>
        <RouterLink class="btn ghost large" to="/mypage">마이페이지로</RouterLink>
      </div>
    </form>
  </main>
</template>
