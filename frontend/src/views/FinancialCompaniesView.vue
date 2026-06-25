<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { apiFetch } from "../api/client";
import PageHeader from "../components/PageHeader.vue";
import StatusBlock from "../components/StatusBlock.vue";

const overview = ref(null);
const loading = ref(false);
const error = ref("");

const summary = computed(() => overview.value?.summary || {});
const banks = computed(() => overview.value?.banks || []);
const topProducts = computed(() => overview.value?.top_products || []);

function formatNumber(value) {
  if (value === undefined || value === null || value === "" || Number.isNaN(Number(value))) return "-";
  return Number(value).toLocaleString("ko-KR");
}

function formatRate(value) {
  if (value === undefined || value === null || value === "" || Number.isNaN(Number(value))) return "-";
  return `${Number(value).toFixed(2)}%`;
}

async function loadOverview() {
  loading.value = true;
  error.value = "";
  try {
    overview.value = await apiFetch("/companies/overview/");
  } catch (err) {
    error.value = err.message || "금융상품 개요 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadOverview);
</script>

<template>
  <main class="container companies-overview-page">
    <PageHeader
      title="금융상품 개요"
      description="FinPick에 저장된 예적금 상품 데이터를 은행별, 유형별로 요약해 보여드립니다."
    />

    <StatusBlock :loading="loading" :error="error" />

    <template v-if="overview">
      <section class="overview-hero-card">
        <div>
          <p>데이터 기준</p>
          <h2>은행별 예적금 상품 현황</h2>
          <span>금융감독원 금융상품 데이터를 DB에 저장한 뒤, FinPick 추천과 비교 화면에서 함께 사용합니다.</span>
        </div>
        <RouterLink class="btn primary" to="/products">상품 비교하기</RouterLink>
      </section>

      <section class="overview-stat-grid">
        <article class="overview-stat-card">
          <span>등록 상품</span>
          <strong>{{ formatNumber(summary.products) }}개</strong>
          <small>예금 {{ formatNumber(summary.deposit_products) }} · 적금 {{ formatNumber(summary.saving_products) }}</small>
        </article>
        <article class="overview-stat-card">
          <span>금융회사</span>
          <strong>{{ formatNumber(summary.banks) }}곳</strong>
          <small>상품이 등록된 은행 기준</small>
        </article>
        <article class="overview-stat-card accent">
          <span>최고 우대금리</span>
          <strong>{{ formatRate(summary.highest_rate) }}</strong>
          <small>현재 DB 상품 옵션 기준</small>
        </article>
      </section>

      <section class="overview-layout">
        <article class="overview-panel">
          <div class="section-head compact-head">
            <h2>은행별 상품 현황</h2>
            <p>등록 상품 수와 은행별 최고 우대금리를 함께 확인합니다.</p>
          </div>
          <div class="bank-overview-list">
            <div v-for="bank in banks" :key="bank.bank_name" class="bank-overview-row">
              <div>
                <strong>{{ bank.bank_name }}</strong>
                <span>예금 {{ bank.deposit_count }} · 적금 {{ bank.saving_count }}</span>
              </div>
              <div class="bank-rate-box">
                <small>{{ bank.product_count }}개</small>
                <b>{{ formatRate(bank.best_rate) }}</b>
              </div>
            </div>
          </div>
        </article>

        <aside class="overview-panel top-product-panel">
          <div class="section-head compact-head">
            <h2>고금리 상품 TOP 5</h2>
            <p>우대금리 기준으로 정렬했습니다.</p>
          </div>
          <RouterLink
            v-for="product in topProducts"
            :key="product.id"
            class="top-product-row"
            :to="`/products/${product.id}`"
          >
            <div>
              <span>{{ product.bank_name }}</span>
              <strong>{{ product.name }}</strong>
              <small>{{ product.product_type_label }}</small>
            </div>
            <b>{{ formatRate(product.best_rate) }}</b>
          </RouterLink>
        </aside>
      </section>
    </template>
  </main>
</template>
