<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const product = ref(null);
const loading = ref(true);
const favoriteLoading = ref(false);
const error = ref("");
const favoriteMessage = ref("");
const favoriteError = ref("");

const productCode = computed(() => String(route.params.code || ""));
const isJoined = computed(() => (
  auth.user?.joined_savings || []
).some(item => item.favorite_key === `savings:${productCode.value}` || item.product_code === productCode.value));

function value(item) {
  return item || "정보 없음";
}

async function toggleFavorite() {
  if (!auth.isAuthenticated) {
    router.push({ name: "login", query: { next: route.fullPath } });
    return;
  }
  if (!product.value || favoriteLoading.value) return;

  favoriteLoading.value = true;
  favoriteMessage.value = "";
  favoriteError.value = "";
  try {
    const user = await apiFetch(`/savings/${encodeURIComponent(productCode.value)}/join/`, {
      method: isJoined.value ? "DELETE" : "POST",
      body: isJoined.value ? undefined : JSON.stringify({
        name: product.value.name,
        bank_name: product.value.bank_name,
        product_type_label: product.value.product_type_label,
        product_subtype: product.value.product_subtype,
        rate_value: product.value.rate_value,
        rate_label: product.value.rate_label,
        join_way: product.value.join_way,
        join_member: product.value.join_member,
        special_condition: product.value.special_condition,
        etc_note: product.value.etc_note
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
    const data = await apiFetch(`/savings/?code=${encodeURIComponent(productCode.value)}`);
    product.value = (data.results || [])[0] || null;
    if (!product.value) error.value = "저축상품 정보를 찾을 수 없습니다.";
  } catch (err) {
    error.value = err.message || "저축상품 정보를 찾을 수 없습니다.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="container loan-detail-page">
    <StatusBlock :loading="loading" :error="error" />

    <section v-if="product" class="detail-layout">
      <article class="content-panel">
        <span class="badge">{{ product.product_type_label || "저축상품" }}</span>
        <h1>{{ product.name }}</h1>
        <p class="muted">{{ product.bank_name }}</p>

        <dl class="info-list">
          <dt>상품 유형</dt><dd>{{ value(product.product_subtype) }}</dd>
          <dt>가입 방법</dt><dd>{{ value(product.join_way) }}</dd>
          <dt>가입 대상</dt><dd>{{ value(product.join_member) }}</dd>
          <dt>우대 조건</dt><dd>{{ value(product.special_condition) }}</dd>
          <dt>기타 안내</dt><dd>{{ value(product.etc_note) }}</dd>
          <dt>공시월</dt><dd>{{ value(product.dcls_month) }}</dd>
          <dt>공시 시작일</dt><dd>{{ value(product.dcls_strt_day) }}</dd>
          <dt>공시 종료일</dt><dd>{{ value(product.dcls_end_day) }}</dd>
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
        <h2>{{ product.rate_label || "수익률" }}</h2>
        <div class="saving-rate-box">
          <span>공시 기준 최고</span>
          <strong>{{ product.rate_value ? `${Number(product.rate_value).toFixed(2)}%` : "정보 없음" }}</strong>
        </div>
        <p class="loan-empty">실제 수익률과 적용 조건은 금융회사 상품 설명서를 확인해주세요.</p>
      </aside>
    </section>

    <section v-else-if="!loading" class="loan-not-found">
      <h1>저축상품 정보를 찾을 수 없습니다.</h1>
      <button class="btn primary" type="button" @click="router.push('/products?group=savings')">목록으로 돌아가기</button>
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
.saving-rate-box { display: grid; gap: .35rem; border: 1px solid #dce7f5; border-radius: 16px; background: #f7fbff; margin: 1rem 0; padding: 1.25rem; }
.saving-rate-box span { color: #5d7088; font-weight: 850; }
.saving-rate-box strong { color: #176be9; font-size: 2rem; letter-spacing: -.045em; }
.loan-empty,
.loan-not-found { background: #fff; border: 1px dashed #cad9eb; border-radius: 16px; color: #657991; padding: 2rem; text-align: center; }
.loan-not-found { display: grid; gap: 1rem; justify-items: center; margin-top: 2rem; }
.loan-not-found h1 { color: #1a3656; font-size: 1.25rem; margin: 0; }
@media (max-width: 720px) { .loan-detail-page { padding-top: 1.75rem; } }
</style>
