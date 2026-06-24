<script setup>
import { onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import ProductCard from "../components/ProductCard.vue";
import StatusBlock from "../components/StatusBlock.vue";

const products = ref([]);
const banks = ref([]);
const loading = ref(false);
const error = ref("");
const filters = reactive({ q: "", bank: "", sort: "rate" });

async function loadProducts() {
  loading.value = true;
  error.value = "";
  try {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => value && params.set(key, value));
    products.value = await apiFetch(`/products/?${params.toString()}`);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  banks.value = await apiFetch("/products/banks/");
  await loadProducts();
});
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>예적금 상품</h1>
      <p>은행별 필터와 검색으로 상품을 비교합니다.</p>
    </div>

    <form class="filter-bar" @submit.prevent="loadProducts">
      <input v-model="filters.q" placeholder="상품명 또는 은행명">
      <select v-model="filters.bank">
        <option value="">전체 은행</option>
        <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
      </select>
      <select v-model="filters.sort">
        <option value="rate">금리순</option>
        <option value="name">이름순</option>
      </select>
      <button class="btn primary" type="submit">검색</button>
    </form>

    <StatusBlock :loading="loading" :error="error" :empty="!loading && !products.length ? '조건에 맞는 상품이 없습니다.' : ''" />
    <div class="card-grid">
      <ProductCard v-for="product in products" :key="product.id" :product="product" />
    </div>
  </main>
</template>
