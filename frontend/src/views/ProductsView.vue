<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import ProductCard from "../components/ProductCard.vue";
import PageHeader from "../components/PageHeader.vue";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const products = ref([]);
const banks = ref([]);
const loading = ref(false);
const error = ref("");
const viewMode = ref("bank");
const mainProductGroup = ref("deposit");
const loanType = ref("all");
const loans = ref([]);
const loanLoading = ref(false);
const loanViewMode = ref("bank");
const focusedLoanBank = ref("");
const focusedLoanType = ref("");
const focusedBank = ref("");
const filters = reactive({ q: "", bank: "", sort: "rate" });
const loanFilters = reactive({ q: "", bank: "", sort: "rate" });

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

<<<<<<< HEAD
const productTypeCounts = computed(() => {
  const counts = new Map();
  products.value.forEach(product => {
    const name = product.product_type_label || product.product_type || "기타 상품";
    counts.set(name, (counts.get(name) || 0) + 1);
  });
  return [...counts.entries()].map(([name, count]) => ({ name, count }));
});

const loanBanks = computed(() => [...new Set(loans.value.map(loan => loan.bank_name).filter(Boolean))].sort());
const groupedLoans = computed(() => {
  const groups = new Map();
  const focusedGroup = loanViewMode.value === "bank" ? focusedLoanBank.value : focusedLoanType.value;
  const visibleLoans = focusedGroup
    ? loans.value.filter(loan => (loanViewMode.value === "bank" ? loan.bank_name : loan.loan_type_label) === focusedGroup)
    : loans.value;
  visibleLoans.forEach(loan => {
    const key = loanViewMode.value === "bank" ? (loan.bank_name || "금융기관") : loan.loan_type_label;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(loan);
  });
  return [...groups.entries()].map(([name, items]) => ({ name, items }));
});
const isLoanGroupFocused = computed(() => Boolean(loanViewMode.value === "bank" ? focusedLoanBank.value : focusedLoanType.value));

=======
>>>>>>> cdd745b (1200)
function groupIcon(name) {
  if (name.includes("적금")) return "적";
  if (name.includes("예금")) return "예";
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

async function loadLoans() {
  loanLoading.value = true;
  error.value = "";
  try {
    const params = new URLSearchParams({ type: loanType.value });
    Object.entries(loanFilters).forEach(([key, value]) => value && params.set(key, value));
    const data = await apiFetch(`/loans/?${params.toString()}`);
    loans.value = data.results || [];
  } catch (err) {
    error.value = err.message || "대출 상품을 불러오지 못했습니다.";
  } finally {
    loanLoading.value = false;
  }
}

function visibleLoanItems(group) {
  return isLoanGroupFocused.value ? group.items : group.items.slice(0, 2);
}

function toggleLoanGroup(groupName) {
  if (isLoanGroupFocused.value) {
    focusedLoanBank.value = "";
    focusedLoanType.value = "";
    return;
  }
  if (loanViewMode.value === "bank") focusedLoanBank.value = groupName;
  else focusedLoanType.value = groupName;
}

function openLoanDetail(loan) {
  router.push({ name: "loan-detail", params: { type: loan.loan_type, code: loan.product_code } });
}

function resetLoanFilters() {
  loanFilters.q = "";
  loanFilters.bank = "";
  loanFilters.sort = "rate";
  focusedLoanBank.value = "";
  focusedLoanType.value = "";
  loadLoans();
}

function selectMainGroup(group) {
  mainProductGroup.value = group;
  if (group === "loan") loadLoans();
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
  const group = route.query.group;
  const query = typeof route.query.q === "string" ? route.query.q : "";
  if (group === "loan") {
    mainProductGroup.value = "loan";
    loanType.value = "all";
    loanFilters.q = query;
    await loadLoans();
    return;
  }
  filters.q = query;
  await loadProducts();
});
</script>

<template>
  <main class="container products-page-local">
    <header class="products-hero-local">
<<<<<<< HEAD
      <div>
        <h1>상품</h1>
        <p>은행별 필터와 검색으로 상품을 비교합니다.</p>
      </div>
=======
      <PageHeader
        eyebrow="FINPICK PRODUCT"
        title="예적금상품"
        description="은행별 예금과 적금 상품을 금리, 기간, 조건 기준으로 비교합니다."
      />
>>>>>>> cdd745b (1200)
      <RouterLink class="interest-link-local" to="/favorites">
        <span aria-hidden="true">☆</span>
        관심 목록
        <b>{{ joinedCount }}</b>
      </RouterLink>
    </header>

    <div class="main-product-tabs-local">
      <button type="button" :class="{ active: mainProductGroup === 'deposit' }" @click="selectMainGroup('deposit')">예적금</button>
      <button type="button" :class="{ active: mainProductGroup === 'loan' }" @click="selectMainGroup('loan')">대출</button>
    </div>

    <form v-if="mainProductGroup === 'deposit'" class="product-filter-local" @submit.prevent="loadProducts">
      <label class="product-search-local">
        <span aria-hidden="true">⌕</span>
        <input v-model="filters.q" placeholder="상품명 또는 은행명으로 검색하세요">
      </label>
      <label class="product-select-local">
        <span aria-hidden="true">▦</span>
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

    <div v-if="mainProductGroup === 'deposit'" class="products-page-local">
      <section class="products-content-local">
        <div class="view-tabs-local" role="tablist" aria-label="상품 보기 방식">
          <button type="button" :class="{ active: viewMode === 'bank' }" @click="viewMode = 'bank'">
            <span aria-hidden="true">▦</span> 은행별로 보기
          </button>
          <button type="button" :class="{ active: viewMode === 'type' }" @click="viewMode = 'type'">
            <span aria-hidden="true">◇</span> 상품 유형별 보기
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
                <template v-if="isBankFocused">돌아가기</template>
                <template v-else>전체 보기</template>
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
    </div>
    <section v-else class="loan-results-local">
      <form class="product-filter-local loan-filter-local" @submit.prevent="focusedLoanBank = ''; focusedLoanType = ''; loadLoans()">
        <label class="product-search-local"><span aria-hidden="true">⌕</span><input v-model="loanFilters.q" placeholder="상품명 또는 금융회사명으로 검색하세요"></label>
        <label class="product-select-local"><span aria-hidden="true">⌂</span><select v-model="loanFilters.bank"><option value="">전체 금융기관</option><option v-for="bank in loanBanks" :key="bank" :value="bank">{{ bank }}</option></select></label>
        <label class="product-select-local"><span aria-hidden="true">↕</span><select v-model="loanFilters.sort"><option value="rate">금리 낮은순</option><option value="bank">금융기관순</option><option value="name">상품명순</option></select></label>
        <button class="btn primary product-search-submit" type="submit">검색하기</button>
      </form>
      <div class="view-tabs-local loan-view-tabs-local" role="tablist" aria-label="대출 보기 방식">
        <button type="button" :class="{ active: loanViewMode === 'bank' }" @click="loanViewMode = 'bank'; focusedLoanBank = ''; focusedLoanType = ''">금융기관별 보기</button>
        <button type="button" :class="{ active: loanViewMode === 'type' }" @click="loanViewMode = 'type'; focusedLoanBank = ''; focusedLoanType = ''">대출 유형별 보기</button>
      </div>
      <p v-if="loanLoading" class="status-block">대출 상품을 불러오는 중입니다.</p>
      <p v-else-if="error" class="status-block warning">{{ error }}</p>
      <section v-else-if="groupedLoans.length" class="loan-groups-local">
        <article v-for="group in groupedLoans" :key="group.name" class="loan-group-local">
          <div class="product-group-head-local">
            <div class="group-name-local"><span class="group-icon-local" aria-hidden="true">⌂</span><h2>{{ group.name }}</h2><em>{{ group.items.length }}개 상품</em></div>
            <button v-if="isLoanGroupFocused || group.items.length > 2" class="group-more-local" type="button" @click="toggleLoanGroup(group.name)">{{ isLoanGroupFocused ? '‹ 돌아가기' : '전체 보기 ›' }}</button>
          </div>
          <div class="loan-grid-local">
            <article v-for="loan in visibleLoanItems(group)" :key="`${loan.loan_type}-${loan.product_code}`" class="loan-card-local" role="link" tabindex="0" @click="openLoanDetail(loan)" @keydown.enter="openLoanDetail(loan)">
              <div class="loan-card-top-local"><span>{{ loan.loan_type_label }}</span><strong>{{ loan.rate_min ? `최저 ${loan.rate_min.toFixed(2)}%` : '금리 정보 확인' }}</strong></div>
              <h3>{{ loan.name }}</h3><p>{{ loan.bank_name }}</p>
              <dl><div><dt>대출 한도</dt><dd>{{ loan.loan_limit || '상품별 상이' }}</dd></div><div><dt>상환 방식</dt><dd>{{ loan.repay_type || '상품별 상이' }}</dd></div><div><dt>가입 대상</dt><dd>{{ loan.join_member || '상세 조건 확인' }}</dd></div></dl>
              <p class="loan-card-note-local">{{ loan.loan_inci_expn || loan.early_rpay_fee || '세부 조건은 금융기관 상품 안내에서 확인해주세요.' }}</p><button class="loan-detail-link-local" type="button" @click.stop="openLoanDetail(loan)">상품 상세보기 ›</button>
            </article>
          </div>
        </article>
      </section>
      <section v-else class="product-empty-local"><h2>조건에 맞는 대출 상품이 없습니다.</h2><p>검색어를 줄이거나 금융기관 필터를 전체로 변경해보세요.</p><button class="btn ghost" type="button" @click="resetLoanFilters">필터 초기화</button></section>
    </section>
  </main>
</template>

<style scoped>
.products-page-local { min-height: calc(100vh - 72px); padding-top: 2.8rem; padding-bottom: 4rem; }
.products-hero-local { display: flex; align-items: start; justify-content: space-between; gap: 1rem; margin-bottom: 1.45rem; }
<<<<<<< HEAD
.main-product-tabs-local { display: grid; grid-template-columns: repeat(2, 1fr); gap: .25rem; background: #edf2f8; border-radius: 12px; margin-bottom: .9rem; padding: .25rem; }.main-product-tabs-local button { min-height: 44px; border: 1px solid transparent; border-radius: 9px; background: transparent; color: #526780; cursor: pointer; font-weight: 850; }.main-product-tabs-local button.active { border-color: #9fc1ff; background: #fff; color: #196ae9; }.loan-groups-local { display:grid; gap:1.35rem; }.loan-group-local { border:1px solid #dce6f2; border-radius:18px; background:#f8fbff; padding:1rem; }.loan-grid-local { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }.loan-card-local { border:1px solid #dce6f2; border-radius:14px; background:#fff; cursor:pointer; padding:1rem; box-shadow:0 5px 16px rgba(29,55,88,.045); transition:.18s ease; }.loan-card-local:hover,.loan-card-local:focus-visible { border-color:#9bc0ff; box-shadow:0 12px 24px rgba(38,100,220,.1); outline:0; transform:translateY(-2px); }.loan-card-top-local { display:flex; justify-content:space-between; gap:.5rem; align-items:center; }.loan-card-top-local span { border-radius:999px; background:#e9f8f5; color:#16806f; padding:.28rem .52rem; font-size:.72rem; font-weight:900; }.loan-card-top-local strong { color:#1768e8; font-size:.9rem; }.loan-card-local h3 { color:#183250; font-size:1.05rem; line-height:1.4; margin:.75rem 0 .25rem; }.loan-card-local > p { color:#6b7d93; margin:0; }.loan-card-local dl { border-top:1px dashed #dce6f0; color:#64768e; font-size:.8rem; margin:1rem 0 0; padding-top:.7rem; }.loan-card-local dl div { display:flex; gap:.5rem; justify-content:space-between; margin-top:.35rem; }.loan-card-local dd { margin:0; max-width:62%; overflow:hidden; text-align:right; text-overflow:ellipsis; white-space:nowrap; }.loan-card-note-local { border-radius:8px; background:#f4f8fd; color:#58708a; font-size:.75rem; line-height:1.45; margin-top:.9rem !important; padding:.55rem .65rem; }.loan-detail-link-local { background:transparent; border:0; color:#1f6ee8; cursor:pointer; font-weight:850; margin-top:.8rem; padding:0; }.loan-view-tabs-local { margin-bottom:1rem; }
.products-hero-local h1 { margin: 0; color: #102a4b; font-size: 2rem; letter-spacing: -.045em; }
.products-hero-local p { margin: .42rem 0 0; color: var(--muted); }
=======
>>>>>>> cdd745b (1200)
.interest-link-local { display: inline-flex; align-items: center; gap: .5rem; min-height: 46px; border: 1px solid #dce6f2; border-radius: 12px; background: #fff; box-shadow: 0 7px 18px rgba(29, 55, 88, .06); color: #344b68; font-weight: 850; padding: 0 .9rem; text-decoration: none; }
.interest-link-local > span { color: #2b75ed; font-size: 1.25rem; }
.interest-link-local b { display: grid; min-width: 20px; height: 20px; place-items: center; border-radius: 50%; background: #216deb; color: #fff; font-size: .74rem; }
.product-filter-local { display: grid; grid-template-columns: minmax(260px, 1fr) minmax(150px, 230px) minmax(130px, 180px) auto; gap: .8rem; align-items: center; border: 1px solid #dbe6f3; border-radius: 16px; background: #fff; box-shadow: 0 10px 25px rgba(29, 55, 88, .06); margin-bottom: 1.4rem; padding: 1rem; }
.product-search-local, .product-select-local { display: flex; align-items: center; gap: .65rem; min-height: 48px; border: 1px solid #d7e3f1; border-radius: 11px; background: #fbfdff; color: #466078; padding: 0 .85rem; }
.product-search-local > span, .product-select-local > span { color: #3577e9; font-size: 1.25rem; font-weight: 900; }
.product-search-local input, .product-select-local select { width: 100%; border: 0; outline: 0; background: transparent; color: #1d3657; font: inherit; font-weight: 750; }
.product-search-submit { min-height: 48px; border-radius: 11px; padding-inline: 1.2rem; }
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
.product-card-grid-local { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem; }
.product-empty-local { display: grid; justify-items: center; gap: .5rem; border: 1px dashed #c9d9ec; border-radius: 16px; background: #fff; color: #657991; margin-top: 1.25rem; padding: 3rem 1rem; text-align: center; }
.product-empty-local > span { color: #2d76ec; font-size: 2rem; }
.product-empty-local h2 { margin: 0; color: #1d3858; font-size: 1.2rem; }
.product-empty-local p { margin: 0; }
<<<<<<< HEAD
@media (max-width: 980px) { .products-layout-local { grid-template-columns: 1fr; } .product-guide-local { position: static; } .loan-grid-local { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 720px) { .products-page-local { padding-top: 1.75rem; } .products-hero-local { align-items: stretch; flex-direction: column; } .interest-link-local { align-self: flex-start; } .product-filter-local { grid-template-columns: 1fr; } .product-card-grid-local, .loan-grid-local { grid-template-columns: 1fr; } .product-group-head-local { align-items: start; } .loan-type-tabs-local { display:grid; grid-template-columns:1fr; } }
=======
@media (max-width: 720px) { .products-page-local { padding-top: 1.75rem; } .products-hero-local { align-items: stretch; flex-direction: column; } .interest-link-local { align-self: flex-start; } .product-filter-local { grid-template-columns: 1fr; } .product-card-grid-local { grid-template-columns: 1fr; } .product-group-head-local { align-items: start; } }
>>>>>>> cdd745b (1200)
</style>
