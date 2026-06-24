<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import ProductCard from "../components/ProductCard.vue";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const products = ref([]);
const banks = ref([]);
const loading = ref(false);
const error = ref("");
const viewMode = ref("bank");
const focusedBank = ref("");
const filters = reactive({ q: "", bank: "", sort: "rate" });

const joinedProductIds = computed(() => new Set((auth.user?.joined_products || []).map(product => Number(product.id))));
const joinedCount = computed(() => joinedProductIds.value.size);

const groupedProducts = computed(() => {
  const groups = new Map();
  const groupByBank = viewMode.value === "bank";

  const visibleProducts = focusedBank.value && groupByBank
    ? products.value.filter(product => product.bank_name === focusedBank.value)
    : products.value;

  visibleProducts.forEach(product => {
    const key = groupByBank ? (product.bank_name || "기타 금융기관") : (product.product_type_label || product.product_type || "기타 상품");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(product);
  });

  return [...groups.entries()].map(([name, items]) => ({ name, items }));
});

const isBankFocused = computed(() => viewMode.value === "bank" && Boolean(focusedBank.value || filters.bank));

const productTypeCounts = computed(() => {
  const counts = new Map();
  products.value.forEach(product => {
    const name = product.product_type_label || product.product_type || "기타 상품";
    counts.set(name, (counts.get(name) || 0) + 1);
  });
  return [...counts.entries()].map(([name, count]) => ({ name, count }));
});

function groupIcon(name) {
  if (name.includes("적금")) return "♧";
  if (name.includes("예금")) return "◈";
  return name.slice(0, 1);
}

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

function resetFilters() {
  filters.q = "";
  filters.bank = "";
  filters.sort = "rate";
  focusedBank.value = "";
  loadProducts();
}

function toggleBankFocus(bankName) {
  if (isBankFocused.value) {
    focusedBank.value = "";
    if (filters.bank) {
      filters.bank = "";
      loadProducts();
    }
    return;
  }
  focusedBank.value = bankName;
}

onMounted(async () => {
  banks.value = await apiFetch("/products/banks/");
  await loadProducts();
});
</script>

<template>
  <main class="container products-page-local">
    <header class="products-hero-local">
      <div>
        <h1>예적금 상품</h1>
        <p>은행별 필터와 검색으로 상품을 비교합니다.</p>
      </div>
      <RouterLink class="interest-link-local" to="/favorites">
        <span aria-hidden="true">☆</span>
        관심 목록
        <b>{{ joinedCount }}</b>
      </RouterLink>
    </header>

    <form class="product-filter-local" @submit.prevent="loadProducts">
      <label class="product-search-local">
        <span aria-hidden="true">⌕</span>
        <input v-model="filters.q" placeholder="상품명 또는 은행명으로 검색하세요">
      </label>
      <label class="product-select-local">
        <span aria-hidden="true">♜</span>
        <select v-model="filters.bank" aria-label="은행 선택">
          <option value="">전체 은행</option>
          <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
        </select>
      </label>
      <label class="product-select-local">
        <span aria-hidden="true">↕</span>
        <select v-model="filters.sort" aria-label="정렬 기준">
          <option value="rate">금리순</option>
          <option value="name">이름순</option>
        </select>
      </label>
      <button class="btn primary product-search-submit" type="submit">검색하기</button>
    </form>

    <div class="products-page-local">
      <section class="products-content-local">
        <div class="view-tabs-local" role="tablist" aria-label="상품 보기 방식">
          <button type="button" :class="{ active: viewMode === 'bank' }" @click="viewMode = 'bank'">
            <span aria-hidden="true">♜</span> 은행별로 보기
          </button>
          <button type="button" :class="{ active: viewMode === 'type' }" @click="viewMode = 'type'">
            <span aria-hidden="true">◈</span> 상품 유형별 보기
          </button>
        </div>

        <StatusBlock :loading="loading" :error="error" />

        <section v-if="!loading && !error && groupedProducts.length" class="product-groups-local">
          <article v-for="group in groupedProducts" :key="group.name" class="product-group-local">
            <div class="product-group-head-local">
              <div class="group-name-local">
                <span class="group-icon-local" aria-hidden="true">{{ groupIcon(group.name) }}</span>
                <h2>{{ group.name }}</h2>
                <em>{{ group.items.length }}개 상품</em>
              </div>
              <button v-if="viewMode === 'bank'" class="group-more-local" type="button" @click="toggleBankFocus(group.name)">
                <template v-if="isBankFocused"><span aria-hidden="true">‹</span> 돌아가기</template>
                <template v-else>전체 보기 <span aria-hidden="true">›</span></template>
              </button>
            </div>
            <div class="product-card-grid-local">
              <ProductCard
                v-for="product in group.items"
                :key="product.id"
                :product="product"
                :is-joined="joinedProductIds.has(Number(product.id))"
              />
            </div>
          </article>
        </section>

        <section v-else-if="!loading && !error" class="product-empty-local">
          <span aria-hidden="true">⌕</span>
          <h2>조건에 맞는 상품이 없습니다.</h2>
          <p>검색어를 줄이거나 은행 필터를 전체로 변경해보세요.</p>
          <button class="btn ghost" type="button" @click="resetFilters">필터 초기화</button>
        </section>
      </section>

      <!-- <aside class="product-guide-local">
        <p class="guide-eyebrow-local">다른 방식으로도 살펴보세요!</p>
        <h2>상품 유형별로 정리하면<br>더 쉽게 비교할 수 있어요.</h2>
        <p>원하는 상품 유형만 골라 금리와 가입 조건을 빠르게 비교해보세요.</p>
        <div class="type-summary-local">
          <article v-for="type in productTypeCounts" :key="type.name">
            <span aria-hidden="true">{{ groupIcon(type.name) }}</span>
            <strong>{{ type.name }}</strong>
            <em>{{ type.count }}개 상품</em>
          </article>
        </div>
        <button class="btn ghost guide-button-local" type="button" @click="viewMode = 'type'">상품 유형별 보기로 이동 →</button>
      </aside> -->
    </div>
  </main>
</template>

<style scoped>
.products-page-local { min-height: calc(100vh - 72px); padding-top: 2.8rem; padding-bottom: 4rem; }
.products-hero-local { display: flex; align-items: start; justify-content: space-between; gap: 1rem; margin-bottom: 1.45rem; }
.products-hero-local h1 { margin: 0; color: #102a4b; font-size: 2rem; letter-spacing: -.045em; }
.products-hero-local p { margin: .42rem 0 0; color: var(--muted); }
.interest-link-local { display: inline-flex; align-items: center; gap: .5rem; min-height: 46px; border: 1px solid #dce6f2; border-radius: 12px; background: #fff; box-shadow: 0 7px 18px rgba(29, 55, 88, .06); color: #344b68; font-weight: 850; padding: 0 .9rem; text-decoration: none; }
.interest-link-local > span { color: #2b75ed; font-size: 1.25rem; }
.interest-link-local b { display: grid; min-width: 20px; height: 20px; place-items: center; border-radius: 50%; background: #216deb; color: #fff; font-size: .74rem; }
.product-filter-local { display: grid; grid-template-columns: minmax(260px, 1fr) minmax(150px, 230px) minmax(130px, 180px) auto; gap: .8rem; align-items: center; border: 1px solid #dbe6f3; border-radius: 16px; background: #fff; box-shadow: 0 10px 25px rgba(29, 55, 88, .06); margin-bottom: 1.4rem; padding: 1rem; }
.product-search-local, .product-select-local { display: flex; align-items: center; gap: .65rem; min-height: 48px; border: 1px solid #d7e3f1; border-radius: 11px; background: #fbfdff; color: #466078; padding: 0 .85rem; }
.product-search-local > span, .product-select-local > span { color: #3577e9; font-size: 1.25rem; font-weight: 900; }
.product-search-local input, .product-select-local select { width: 100%; border: 0; outline: 0; background: transparent; color: #1d3657; font: inherit; font-weight: 750; }
.product-search-submit { min-height: 48px; border-radius: 11px; padding-inline: 1.2rem; }
.products-layout-local { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 1.6rem; align-items: start; }
.view-tabs-local { display: grid; grid-template-columns: repeat(2, 1fr); gap: .25rem; border-radius: 12px; background: #edf2f8; padding: .25rem; }
.view-tabs-local button { min-height: 46px; border: 1px solid transparent; border-radius: 9px; background: transparent; color: #526780; cursor: pointer; font-weight: 850; }
.view-tabs-local button.active { border-color: #9fc1ff; background: #fff; box-shadow: 0 4px 12px rgba(37, 99, 235, .08); color: #196ae9; }
.view-tabs-local button span { margin-right: .35rem; }
.product-groups-local { display: grid; gap: 1.55rem; margin-top: 1.25rem; }
.product-group-local { border-bottom: 1px solid #e0e8f2; padding-bottom: 1.45rem; }
.product-group-local:last-child { border-bottom: 0; }
.product-group-head-local { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: .75rem; }
.group-name-local { display: flex; align-items: center; gap: .65rem; }
.group-icon-local { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 50%; background: #edf5ff; color: #176bea; font-weight: 900; }
.group-name-local h2 { margin: 0; color: #183250; font-size: 1.22rem; letter-spacing: -.03em; }
.group-name-local em { border-radius: 999px; background: #edf2f7; color: #61748c; font-size: .76rem; font-style: normal; font-weight: 800; padding: .25rem .5rem; }
.group-more-local { border: 0; background: transparent; color: #246fe9; cursor: pointer; font-weight: 850; }
.group-more-local span { font-size: 1.2rem; }
.product-card-grid-local { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem; }
.product-guide-local { position: sticky; top: 92px; border: 1px solid #d8e5f3; border-radius: 16px; background: linear-gradient(145deg, #fff, #f3f8ff); box-shadow: 0 10px 24px rgba(29, 55, 88, .05); padding: 1.2rem; }
.guide-eyebrow-local { margin: 0; color: #176bea; font-size: .82rem; font-weight: 900; }
.product-guide-local h2 { margin: .5rem 0; color: #183250; font-size: 1.12rem; line-height: 1.45; letter-spacing: -.025em; }
.product-guide-local > p:not(.guide-eyebrow-local) { color: #6b7d93; font-size: .83rem; line-height: 1.6; }
.type-summary-local { display: grid; gap: .65rem; margin: 1rem 0; }
.type-summary-local article { display: grid; grid-template-columns: 28px 1fr auto; align-items: center; gap: .5rem; border: 1px solid #dbe6f3; border-radius: 10px; background: rgba(255,255,255,.82); padding: .7rem; }
.type-summary-local span { display: grid; width: 28px; height: 28px; place-items: center; border-radius: 50%; background: #dcf5ed; color: #158662; font-weight: 900; }
.type-summary-local strong { color: #31506c; font-size: .9rem; }
.type-summary-local em { color: #6a7c92; font-size: .73rem; font-style: normal; }
.guide-button-local { width: 100%; border-radius: 10px; color: #1b6ce9; font-size: .82rem; }
.product-empty-local { display: grid; justify-items: center; gap: .5rem; border: 1px dashed #c9d9ec; border-radius: 16px; background: #fff; color: #657991; margin-top: 1.25rem; padding: 3rem 1rem; text-align: center; }
.product-empty-local > span { color: #2d76ec; font-size: 2rem; }
.product-empty-local h2 { margin: 0; color: #1d3858; font-size: 1.2rem; }
.product-empty-local p { margin: 0; }
@media (max-width: 980px) { .products-layout-local { grid-template-columns: 1fr; } .product-guide-local { position: static; } }
@media (max-width: 720px) { .products-page-local { padding-top: 1.75rem; } .products-hero-local { align-items: stretch; flex-direction: column; } .interest-link-local { align-self: flex-start; } .product-filter-local { grid-template-columns: 1fr; } .product-card-grid-local { grid-template-columns: 1fr; } .product-group-head-local { align-items: start; } }
</style>
