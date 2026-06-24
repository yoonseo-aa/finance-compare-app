<script setup>
import { Chart } from "chart.js/auto";
import { nextTick, onMounted, reactive, ref, watch } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const chartCanvas = ref(null);
const saved = ref(false);
let chart = null;

const form = reactive({
  email: "",
  nickname: "",
  age: null,
  age_group: "",
  marital_status: "",
  has_children: null,
  region: "",
  income_level: "",
  asset_level: "",
  employment_status: "",
  saving_purpose: "",
  savings_goal: 1000000,
  monthly_saving: 400000,
  preferred_term: 12,
  risk_tolerance: "stable"
});

function syncForm() {
  if (!auth.user) return;
  Object.assign(form, {
    email: auth.user.email || "",
    nickname: auth.user.nickname || "",
    age: auth.user.age,
    age_group: auth.user.age_group || "",
    marital_status: auth.user.marital_status || "",
    has_children: auth.user.has_children,
    region: auth.user.region || "",
    income_level: auth.user.income_level || "",
    asset_level: auth.user.asset_level || "",
    employment_status: auth.user.employment_status || "",
    saving_purpose: auth.user.saving_purpose || "",
    savings_goal: auth.user.savings_goal,
    monthly_saving: auth.user.monthly_saving,
    preferred_term: auth.user.preferred_term,
    risk_tolerance: auth.user.risk_tolerance || "stable"
  });
}

function renderChart() {
  if (!chartCanvas.value || !auth.user) return;
  chart?.destroy();
  const joined = auth.user.joined_products || [];
  chart = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels: joined.map(product => product.name),
      datasets: [{ label: "최고 우대금리", data: joined.map(product => product.best_rate), backgroundColor: "#2563eb" }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
  });
}

async function submit() {
  await auth.updateProfile(form);
  saved.value = true;
  await nextTick();
  renderChart();
}

onMounted(async () => {
  if (!auth.user) await auth.bootstrap();
  syncForm();
  await nextTick();
  renderChart();
});

watch(() => auth.user, syncForm);
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>프로필</h1>
      <p>추천에 사용할 금융 프로필과 대시보드 기준을 관리합니다.</p>
    </div>

    <section class="detail-layout" v-if="auth.user">
      <form class="content-panel stack-form" @submit.prevent="submit">
        <h2>추천 프로필</h2>
        <label>이메일<input v-model="form.email" type="email"></label>
        <label>닉네임<input v-model="form.nickname"></label>

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

        <h2>대시보드 기준</h2>
        <label>목표 금액<input v-model.number="form.savings_goal" type="number" min="0"></label>
        <label>월 저축 가능 금액<input v-model.number="form.monthly_saving" type="number" min="0"></label>
        <label>선호 기간<input v-model.number="form.preferred_term" type="number" min="1"></label>

        <button class="btn primary" type="submit">수정</button>
        <p v-if="saved" class="success-text">저장되었습니다.</p>
      </form>

      <div class="content-panel">
        <h2>가입 상품</h2>
        <div class="chart-panel compact"><canvas ref="chartCanvas"></canvas></div>
        <ul class="plain-list">
          <li v-for="product in auth.user.joined_products" :key="product.id">
            {{ product.bank_name }} · {{ product.name }} <strong>{{ product.best_rate }}%</strong>
          </li>
          <li v-if="!auth.user.joined_products.length" class="muted">가입한 상품이 없습니다.</li>
        </ul>
      </div>
    </section>
  </main>
</template>