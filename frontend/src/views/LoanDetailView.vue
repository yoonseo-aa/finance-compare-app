<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const loan = ref(null);
const loading = ref(true);
const favoriteLoading = ref(false);
const error = ref("");
const favoriteMessage = ref("");
const favoriteError = ref("");

const loanType = computed(() => String(route.params.type || ""));
const loanCode = computed(() => String(route.params.code || ""));
const favoriteKey = computed(() => `loan:${loanType.value}:${loanCode.value}`);
const isJoined = computed(() => (
  auth.user?.joined_loans || []
).some(item => item.favorite_key === favoriteKey.value || (
  item.loan_type === loanType.value && String(item.product_code) === loanCode.value
)));

function value(item) {
  return item || "정보 없음";
}

function rateText(rate) {
  return rate || rate === 0 ? `${Number(rate).toFixed(2)}%` : "정보 없음";
}

async function toggleFavorite() {
  if (!auth.isAuthenticated) {
    router.push({ name: "login", query: { next: route.fullPath } });
    return;
  }
  if (!loan.value || favoriteLoading.value) return;

  favoriteLoading.value = true;
  favoriteMessage.value = "";
  favoriteError.value = "";
  try {
    const user = await apiFetch(`/loans/${encodeURIComponent(loanType.value)}/${encodeURIComponent(loanCode.value)}/join/`, {
      method: isJoined.value ? "DELETE" : "POST",
      body: isJoined.value ? undefined : JSON.stringify({
        name: loan.value.name,
        bank_name: loan.value.bank_name,
        loan_type_label: loan.value.loan_type_label,
        rate_min: loan.value.rate_min,
        loan_limit: loan.value.loan_limit,
        repay_type: loan.value.repay_type,
        join_member: loan.value.join_member
      })
    });
    auth.setUser(user);
    favoriteMessage.value = isJoined.value ? "관심 목록에 추가되었습니다." : "관심 목록에서 삭제되었습니다.";
  } catch (err) {
    favoriteError.value = err.message || "관심 목록을 변경하지 못했습니다.";
  } finally {
    favoriteLoading.value = false;
  }
}

onMounted(async () => {
  try {
    if (!auth.user) await auth.bootstrap();
    const data = await apiFetch(`/loans/?type=${encodeURIComponent(loanType.value)}&code=${encodeURIComponent(loanCode.value)}`);
    loan.value = (data.results || [])[0] || null;
    if (!loan.value) error.value = "대출 상품 정보를 찾을 수 없습니다.";
  } catch (err) {
    error.value = err.message || "대출 상품 정보를 찾을 수 없습니다.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="container loan-detail-page">
    <StatusBlock :loading="loading" :error="error" />

    <section v-if="loan" class="detail-layout">
      <article class="content-panel">
        <span class="badge">{{ loan.loan_type_label }}</span>
        <h1>{{ loan.name }}</h1>
        <p class="muted">{{ loan.bank_name }}</p>

        <dl class="info-list">
          <dt>가입 방법</dt><dd>{{ value(loan.join_way) }}</dd>
          <dt>대출 대상</dt><dd>{{ value(loan.join_member) }}</dd>
          <dt>대출 유형</dt><dd>{{ value(loan.loan_product_type) }}</dd>
          <dt>신용평가회사</dt><dd>{{ value(loan.cb_name) }}</dd>
          <dt>대출 한도</dt><dd>{{ value(loan.loan_limit) }}</dd>
          <dt>상환 방식</dt><dd>{{ value(loan.repay_type) }}</dd>
          <dt>공시월</dt><dd>{{ value(loan.dcls_month) }}</dd>
          <dt>공시 시작일</dt><dd>{{ value(loan.dcls_start_day) }}</dd>
          <dt>공시 종료일</dt><dd>{{ value(loan.dcls_end_day) }}</dd>
          <dt>금융회사 제출일</dt><dd>{{ value(loan.fin_co_submit_day) }}</dd>
          <dt>기타 안내</dt><dd>{{ value(loan.loan_inci_expn || loan.early_rpay_fee) }}</dd>
        </dl>

        <p v-if="favoriteMessage" class="favorite-feedback success">{{ favoriteMessage }}</p>
        <p v-if="favoriteError" class="favorite-feedback error">{{ favoriteError }}</p>

        <div class="detail-actions">
          <button class="btn primary" type="button" :disabled="favoriteLoading" @click="toggleFavorite">
            <template v-if="favoriteLoading">처리 중...</template>
            <template v-else>{{ isJoined ? "관심 목록에서 삭제" : "관심 목록에 추가" }}</template>
          </button>
          <button class="btn ghost large" type="button" @click="router.back()">돌아가기</button>
        </div>
      </article>

      <aside class="content-panel">
        <h2>금리 옵션 및 대출 조건</h2>
        <table v-if="loan.options?.length">
          <thead>
            <tr>
              <th>상환 방식</th>
              <th>금리 구분</th>
              <th>최저 금리</th>
              <th>최고 금리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(option, index) in loan.options" :key="option.id || index">
              <td>{{ value(option.rpay_type_nm) }}</td>
              <td>{{ value(option.lend_rate_type_nm) }}</td>
              <td>{{ rateText(option.lend_rate_min) }}</td>
              <td><strong>{{ rateText(option.lend_rate_max) }}</strong></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="loan-empty">상세 조건은 금융회사 상품 안내에서 확인해주세요.</p>
      </aside>
    </section>

    <section v-else-if="!loading" class="loan-not-found">
      <h1>대출 상품 정보를 찾을 수 없습니다.</h1>
      <button class="btn primary" type="button" @click="router.push('/products?group=loan')">목록으로 돌아가기</button>
    </section>
  </main>
</template>

<style scoped>
.loan-detail-page { padding-top: 3rem; padding-bottom: 4rem; }
.detail-actions { display: flex; align-items: center; gap: 12px; margin-top: 24px; flex-wrap: wrap; }
.detail-actions .btn { width: auto; }
.favorite-feedback { border-radius: 10px; font-size: .9rem; font-weight: 800; margin: 1rem 0 0; padding: .75rem .9rem; }
.favorite-feedback.success { background: #edf7ff; border: 1px solid #bfd8ff; color: #1d62d7; }
.favorite-feedback.error { background: #fff6f6; border: 1px solid #f1c6c6; color: #af3737; }
.loan-empty,
.loan-not-found { background: #fff; border: 1px dashed #cad9eb; border-radius: 16px; color: #657991; padding: 2rem; text-align: center; }
.loan-not-found { display: grid; gap: 1rem; justify-items: center; margin-top: 2rem; }
.loan-not-found h1 { color: #1a3656; font-size: 1.25rem; margin: 0; }
@media (max-width: 720px) { .loan-detail-page { padding-top: 1.75rem; } }
</style>
