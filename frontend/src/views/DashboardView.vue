<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const dashboard = ref(null);
const loans = ref([]);
const savings = ref([]);
const loading = ref(true);
const error = ref("");
const recommendGroup = ref("deposit");
const showAllRecommendations = ref(false);
const favoriteLoadingKey = ref("");

const recommendTabs = [
  { key: "deposit", label: "예적금" },
  { key: "loan", label: "대출" },
  { key: "savings", label: "저축" }
];

const donutSegments = [
  { label: "추천 원금", value: 45, color: "#176be9", className: "label-45" },
  { label: "예상 이자", value: 30, color: "#14b8a6", className: "label-30" },
  { label: "저축 여력", value: 15, color: "#8b5cf6", className: "label-15" },
  { label: "안전 여유", value: 10, color: "#cbd5e1", className: "label-10" }
];

const assetStatus = computed(() => dashboard.value?.asset_status || {});
const goal = computed(() => dashboard.value?.goal || {});
const topRecommendations = computed(() => dashboard.value?.recommendation_groups?.stable || []);

const maturityAssetAmount = computed(() => (
  Number(assetStatus.value.best_expected_amount || goal.value.best_expected_amount || 0)
));

const donutStyle = computed(() => {
  let cursor = 0;
  const stops = donutSegments.map(segment => {
    const start = cursor;
    cursor += segment.value;
    return `${segment.color} ${start}% ${cursor}%`;
  });
  return { background: `conic-gradient(${stops.join(", ")})` };
});

const assetInfoCards = computed(() => [
  { icon: "💳", label: "소득", value: assetStatus.value.income_level || "미입력" },
  { icon: "🏠", label: "재산", value: assetStatus.value.asset_level || "미입력" },
  { icon: "💼", label: "직업/상태", value: assetStatus.value.employment_status || "미입력" },
  { icon: "🎯", label: "저축 목적", value: assetStatus.value.saving_purpose || "미입력" },
  { icon: "🪙", label: "예상 원금", value: formatMoney(assetStatus.value.principal) },
  { icon: "₩", label: "예상 이자", value: formatMoney(assetStatus.value.expected_interest) },
  { icon: "📈", label: "목표 대비 월 저축 여력", value: formatPercent(assetStatus.value.monthly_capacity_rate) },
  { icon: "🐷", label: "예상 만기 자산", value: formatMoney(assetStatus.value.best_expected_amount || goal.value.best_expected_amount) }
]);

const depositRecommendations = computed(() => topRecommendations.value.map((item, index) => {
  const product = item.product || {};
  const rate = product.max_rate ?? product.best_rate ?? product.intr_rate2 ?? 0;
  const reasons = item.reasons || [];

  return {
    group: "deposit",
    favoriteKey: `deposit:${product.id}`,
    id: product.id,
    to: `/products/${product.id}`,
    bankName: product.bank_name || "금융회사",
    name: product.name || "추천 상품",
    typeLabel: product.product_type_label || product.product_type || "예적금",
    logoText: getLogoText(product.bank_name),
    summary: `최고 우대금리 ${formatRate(rate)} · ${reasons[0] || "추천 조건과 잘 맞는 상품입니다."}`,
    badges: [reasons[1] || "조건 적합", index === 0 ? "금리 우수" : "안정성 높음"],
    score: Number(item.score || 0),
    rate
  };
}));

const loanRecommendations = computed(() => loans.value
  .slice()
  .sort((a, b) => Number(a.rate_min || 99) - Number(b.rate_min || 99))
  .slice(0, 8)
  .map((loan, index) => {
    const monthlyPayment = estimateMonthlyLoanPayment(loan);
    const rate = Number(loan.rate_min || 0);

    return {
      group: "loan",
      favoriteKey: `loan:${loan.loan_type}:${loan.product_code}`,
      loan_type: loan.loan_type,
      product_code: loan.product_code,
      to: { name: "loan-detail", params: { type: loan.loan_type, code: loan.product_code } },
      bankName: loan.bank_name || "금융기관",
      name: loan.name || "대출 상품",
      typeLabel: loan.loan_type_label || "대출",
      logoText: getLogoText(loan.bank_name),
      summary: `최저 금리 ${formatRate(rate)} · 예상 월 상환액 ${formatMoney(monthlyPayment)}`,
      badges: [index === 0 ? "금리 우수" : "조건 적합", loan.repay_type || "상환 조건 확인"],
      score: Math.max(62, Math.round((96 - rate * 5) * 10) / 10),
      rate_min: loan.rate_min,
      loan_limit: loan.loan_limit,
      repay_type: loan.repay_type,
      join_member: loan.join_member
    };
  }));

const savingsRecommendations = computed(() => savings.value
  .slice()
  .sort((a, b) => Number(b.rate_value || 0) - Number(a.rate_value || 0))
  .slice(0, 8)
  .map((item, index) => {
    const rate = Number(item.rate_value || 0);

    return {
      group: "savings",
      favoriteKey: `savings:${item.product_code}`,
      product_code: item.product_code,
      to: { name: "savings-detail", params: { code: item.product_code } },
      bankName: item.bank_name || "금융회사",
      name: item.name || "저축 상품",
      typeLabel: item.product_type_label || item.product_subtype || "저축",
      logoText: getLogoText(item.bank_name),
      summary: `${item.product_subtype || "저축 상품"} · 목표 금액에 적합`,
      badges: [index === 0 ? "수익률 우수" : "조건 적합", item.join_way || "가입방법 확인"],
      score: Math.min(96, Math.round((70 + rate * 5) * 10) / 10),
      rate_value: item.rate_value,
      rate_label: item.rate_label,
      product_type_label: item.product_type_label,
      product_subtype: item.product_subtype,
      join_way: item.join_way,
      join_member: item.join_member,
      special_condition: item.special_condition,
      etc_note: item.etc_note
    };
  }));

const activeRecommendations = computed(() => {
  if (recommendGroup.value === "loan") return loanRecommendations.value;
  if (recommendGroup.value === "savings") return savingsRecommendations.value;
  return depositRecommendations.value;
});

const visibleRecommendations = computed(() => (
  showAllRecommendations.value ? activeRecommendations.value : activeRecommendations.value.slice(0, 3)
));

const hasExpandableRecommendations = computed(() => activeRecommendations.value.length > 3);

function formatMoney(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

function formatPercent(value) {
  return `${Number(value || 0).toLocaleString("ko-KR", { maximumFractionDigits: 1 })}%`;
}

function formatRate(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function formatScore(value) {
  const score = Number(value || 0);
  return `${Number.isInteger(score) ? score : score.toFixed(1)}점`;
}

function getLogoText(name) {
  return String(name || "F").trim().slice(0, 1);
}

function normalizeResults(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function selectRecommendGroup(key) {
  recommendGroup.value = key;
  showAllRecommendations.value = false;
}

function estimateMonthlyLoanPayment(loan) {
  const principal = Number(goal.value.target_amount || 200000000);
  const yearlyRate = Number(loan.rate_min || 3.5) / 100;
  const months = Number(goal.value.target_months || 360);
  const monthlyRate = yearlyRate / 12;

  if (!months) return 0;
  if (!monthlyRate) return Math.round(principal / months);

  return Math.round(principal * monthlyRate * ((1 + monthlyRate) ** months) / (((1 + monthlyRate) ** months) - 1));
}

function isFavorite(item) {
  if (item.group === "deposit") {
    return (auth.user?.joined_products || []).some(product => Number(product.id) === Number(item.id));
  }
  if (item.group === "loan") {
    return (auth.user?.joined_loans || []).some(loan => (
      loan.favorite_key === item.favoriteKey ||
      (loan.loan_type === item.loan_type && String(loan.product_code) === String(item.product_code))
    ));
  }
  return (auth.user?.joined_savings || []).some(product => (
    product.favorite_key === item.favoriteKey ||
    String(product.product_code) === String(item.product_code)
  ));
}

function favoriteButtonText(item) {
  if (favoriteLoadingKey.value === item.favoriteKey) return "처리 중...";
  return isFavorite(item) ? "관심목록에서 삭제" : "관심목록 추가";
}

async function toggleFavorite(item) {
  if (!auth.isAuthenticated) {
    router.push({ name: "login", query: { next: route.fullPath } });
    return;
  }
  if (favoriteLoadingKey.value) return;

  favoriteLoadingKey.value = item.favoriteKey;
  try {
    let path = "";
    let payload = undefined;

    if (item.group === "deposit") {
      path = `/products/${item.id}/join/`;
    } else if (item.group === "loan") {
      path = `/loans/${encodeURIComponent(item.loan_type)}/${encodeURIComponent(item.product_code)}/join/`;
      payload = {
        name: item.name,
        bank_name: item.bankName,
        loan_type_label: item.typeLabel,
        rate_min: item.rate_min,
        loan_limit: item.loan_limit,
        repay_type: item.repay_type,
        join_member: item.join_member
      };
    } else {
      path = `/savings/${encodeURIComponent(item.product_code)}/join/`;
      payload = {
        name: item.name,
        bank_name: item.bankName,
        product_type_label: item.product_type_label || item.typeLabel,
        product_subtype: item.product_subtype,
        rate_value: item.rate_value,
        rate_label: item.rate_label,
        join_way: item.join_way,
        join_member: item.join_member,
        special_condition: item.special_condition,
        etc_note: item.etc_note
      };
    }

    const user = await apiFetch(path, {
      method: isFavorite(item) ? "DELETE" : "POST",
      body: isFavorite(item) || !payload ? undefined : JSON.stringify(payload)
    });
    auth.setUser(user);
  } catch (err) {
    error.value = err.message || "관심목록을 변경하지 못했습니다.";
  } finally {
    favoriteLoadingKey.value = "";
  }
}

async function loadDashboard() {
  loading.value = true;
  error.value = "";
  try {
    if (!auth.user) await auth.bootstrap();

    const [dashboardResult, loanResult, savingsResult] = await Promise.allSettled([
      apiFetch("/dashboard/"),
      apiFetch("/loans/?type=all"),
      apiFetch("/savings/")
    ]);

    if (dashboardResult.status === "rejected") throw dashboardResult.reason;
    dashboard.value = dashboardResult.value;
    loans.value = loanResult.status === "fulfilled" ? normalizeResults(loanResult.value) : [];
    savings.value = savingsResult.status === "fulfilled" ? normalizeResults(savingsResult.value) : [];
  } catch (err) {
    error.value = err.message || "대시보드 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <main class="container dashboard-page aligned-dashboard-page">
    <div class="section-head">
      <h1>개인화 대시보드</h1>
      <p>내 추천 프로필과 금융 API 상품 데이터를 바탕으로 목표 가능성, 재산현황, 추천 상품을 확인합니다.</p>
    </div>

    <div class="filter-bar dashboard-action-bar">
      <RouterLink class="btn primary" to="/recommend-profile">나의 정보 입력하기</RouterLink>
      <RouterLink class="btn ghost" to="/recommendations">추천 결과 보러가기</RouterLink>
    </div>

    <StatusBlock :loading="loading" :error="error" />

    <template v-if="dashboard">
      <section class="content-panel asset-status-panel dashboard-asset-panel">
        <div class="section-head compact-head">
          <h2>현재 재산현황</h2>
          <p>추천 진단에서 입력한 재산/소득 정보와 현재 저축 여력을 요약합니다.</p>
        </div>

        <div class="dashboard-asset-layout">
          <div class="asset-donut-area" aria-label="현재 재산현황 비율">
            <div class="asset-donut" :style="donutStyle">
              <div class="asset-donut-center">
                <span>총 예상 만기 자산</span>
                <strong>{{ formatMoney(maturityAssetAmount) }}</strong>
              </div>
            </div>

            <div class="donut-legend">
              <span v-for="segment in donutSegments" :key="segment.label">
                <i :style="{ backgroundColor: segment.color }"></i>
                {{ segment.label }} {{ segment.value }}%
              </span>
            </div>
          </div>

          <div class="dashboard-asset-info-grid">
            <article v-for="card in assetInfoCards" :key="card.label" class="dashboard-asset-info-card">
              <span class="asset-info-icon">{{ card.icon }}</span>
              <div>
                <p>{{ card.label }}</p>
                <strong>{{ card.value }}</strong>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="content-panel dashboard-recommend-panel refined-recommend-panel">
        <div class="recommend-panel-head">
          <div class="section-head compact-head recommend-title">
            <h2>맞춤 추천 상품</h2>
            <p>추천점수와 추천 이유가 높은 상품입니다.</p>
            <RouterLink class="favorite-list-link" to="/favorites">
              <span>☰</span>
              관심목록 보러가기
            </RouterLink>
          </div>

          <div class="recommend-tabs" role="tablist" aria-label="추천 상품군">
            <button
              v-for="tab in recommendTabs"
              :key="tab.key"
              type="button"
              :class="{ active: recommendGroup === tab.key }"
              @click="selectRecommendGroup(tab.key)"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div v-if="visibleRecommendations.length" class="dashboard-recommend-list refined-recommend-list">
          <RouterLink
            v-for="item in visibleRecommendations"
            :key="item.favoriteKey"
            class="dashboard-recommend-item refined-recommend-item"
            :to="item.to"
          >
            <div class="recommend-company-logo" aria-hidden="true">{{ item.logoText }}</div>

            <div class="recommend-product-info">
              <span>{{ item.bankName }}</span>
              <strong>{{ item.name }}</strong>
              <p>{{ item.summary }}</p>
              <div class="recommend-badges">
                <em v-for="badge in item.badges" :key="badge">{{ badge }}</em>
              </div>
            </div>

            <div class="recommend-row-actions">
              <button
                class="recommend-favorite-button"
                type="button"
                :class="{ joined: isFavorite(item) }"
                :disabled="favoriteLoadingKey === item.favoriteKey"
                @click.prevent.stop="toggleFavorite(item)"
              >
                ♡ {{ favoriteButtonText(item) }}
              </button>
              <strong class="recommend-score">{{ formatScore(item.score) }}</strong>
            </div>
          </RouterLink>
        </div>

        <div v-else class="dashboard-recommend-empty">
          <strong>표시할 추천 상품이 없습니다.</strong>
          <p>추천 진단을 완료하거나 상품 데이터를 다시 불러와 주세요.</p>
        </div>

        <div v-if="hasExpandableRecommendations" class="dashboard-more-wrap">
          <button
            class="recommend-more-button"
            type="button"
            @click="showAllRecommendations = !showAllRecommendations"
          >
            {{ showAllRecommendations ? "접기" : "더보기" }}
            
          </button>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.dashboard-asset-panel,
.refined-recommend-panel {
  overflow: hidden;
}

.dashboard-asset-layout {
  align-items: center;
  display: grid;
  gap: 28px;
  grid-template-columns: 250px minmax(0, 1fr);
}

.asset-donut-area {
  align-items: center;
  display: flex;
  flex-direction: column;
  gap: 14px;
  justify-content: center;
  min-width: 0;
}

.asset-donut {
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  flex: 0 0 auto;
  height: auto;
  isolation: isolate;
  position: relative;
  width: 210px;
}

.asset-donut::before {
  border: 1px solid rgba(15, 39, 69, .06);
  border-radius: 50%;
  content: "";
  inset: 0;
  position: absolute;
  z-index: 1;
}

.asset-donut::after {
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 8px 20px rgba(21, 50, 92, .08), inset 0 0 0 1px rgba(214, 226, 241, .95);
  content: "";
  inset: 52px;
  position: absolute;
  z-index: 2;
}

.asset-donut-center {
  align-items: center;
  color: #0f2745;
  display: flex;
  flex-direction: column;
  inset: 52px;
  justify-content: center;
  line-height: 1.25;
  position: absolute;
  text-align: center;
  z-index: 3;
}

.asset-donut-center span {
  color: #64748b;
  font-size: .72rem;
  font-weight: 800;
}

.asset-donut-center strong {
  font-size: 1.17rem;
  letter-spacing: -.045em;
  white-space: nowrap;
}

.donut-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 7px 10px;
  justify-content: center;
  max-width: 240px;
}

.donut-legend span {
  align-items: center;
  background: #f8fbff;
  border: 1px solid #e2eaf5;
  border-radius: 999px;
  color: #52657d;
  display: inline-flex;
  font-size: .72rem;
  font-weight: 850;
  gap: 5px;
  padding: 4px 8px;
}

.donut-legend i {
  border-radius: 50%;
  display: inline-block;
  height: 8px;
  width: 8px;
}

.dashboard-asset-info-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dashboard-asset-info-card {
  align-items: center;
  background: #fff;
  border: 1px solid #dce7f5;
  border-radius: 14px;
  display: flex;
  gap: 12px;
  min-height: 88px;
  padding: 15px;
}

.asset-info-icon {
  align-items: center;
  background: #eff6ff;
  border-radius: 14px;
  color: #176be9;
  display: inline-flex;
  flex: 0 0 36px;
  font-size: 1.1rem;
  height: 36px;
  justify-content: center;
  width: 36px;
}

.dashboard-asset-info-card p {
  color: #64748b;
  font-size: .82rem;
  font-weight: 850;
  margin: 0 0 7px;
}

.dashboard-asset-info-card strong {
  color: #0f2745;
  display: block;
  font-size: 1rem;
  letter-spacing: -.025em;
}

.recommend-panel-head {
  align-items: flex-start;
  display: flex;
  gap: 18px;
  justify-content: space-between;
  margin-bottom: 18px;
}

.recommend-title {
  margin: 0;
}

.favorite-list-link {
  align-items: center;
  background: #fff;
  border: 1px solid #b7d1ff;
  border-radius: 10px;
  color: #176be9;
  display: inline-flex;
  font-size: .9rem;
  font-weight: 900;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 14px;
  text-decoration: none;
  width: fit-content;
}

.recommend-tabs {
  background: #f4f8fd;
  border: 1px solid #d9e5f4;
  border-radius: 12px;
  display: flex;
  flex: 0 0 auto;
  gap: 6px;
  padding: 5px;
}

.recommend-tabs button {
  background: #fff;
  border: 1px solid transparent;
  border-radius: 9px;
  color: #50647d;
  cursor: pointer;
  font-weight: 900;
  min-width: 76px;
  padding: 9px 14px;
}

.recommend-tabs button.active {
  background: #176be9;
  border-color: #176be9;
  color: #fff;
  box-shadow: 0 10px 20px rgba(23, 107, 233, .18);
}

.refined-recommend-list {
  gap: 10px;
}

.refined-recommend-item {
  align-items: center;
  background: #fff;
  border: 1px solid #dce7f5;
  border-radius: 14px;
  color: inherit;
  display: grid;
  gap: 16px;
  grid-template-columns: 58px minmax(0, 1fr) auto;
  padding: 14px 16px;
  text-decoration: none;
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}

.refined-recommend-item:hover {
  border-color: #9fc5ff;
  box-shadow: 0 12px 26px rgba(35, 73, 125, .08);
  transform: translateY(-1px);
}

.recommend-company-logo {
  align-items: center;
  background: linear-gradient(135deg, #1d6ff2, #13b8a6);
  border-radius: 50%;
  color: #fff;
  display: inline-flex;
  font-size: 1.25rem;
  font-weight: 950;
  height: 48px;
  justify-content: center;
  width: 48px;
}

.recommend-product-info {
  min-width: 0;
}

.recommend-product-info span {
  color: #4f6580;
  display: block;
  font-size: .82rem;
  font-weight: 850;
  margin-bottom: 4px;
}

.recommend-product-info strong {
  color: #0f2745;
  display: block;
  font-size: 1rem;
  margin-bottom: 5px;
}

.recommend-product-info p {
  color: #66778d;
  font-size: .88rem;
  font-weight: 700;
  margin: 0;
}

.recommend-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.recommend-badges em {
  background: #eef5ff;
  border-radius: 999px;
  color: #3566a8;
  font-size: .72rem;
  font-style: normal;
  font-weight: 850;
  padding: 5px 8px;
}

.recommend-row-actions {
  align-items: center;
  display: flex;
  gap: 14px;
}

.recommend-favorite-button {
  background: #fff;
  border: 1px solid #b7d1ff;
  border-radius: 999px;
  color: #176be9;
  cursor: pointer;
  font-size: .78rem;
  font-weight: 900;
  padding: 8px 12px;
  white-space: nowrap;
}

.recommend-favorite-button.joined {
  background: #edf7ff;
}

.recommend-favorite-button:disabled {
  cursor: wait;
  opacity: .62;
}

.recommend-score {
  background: #edf4ff;
  border-radius: 999px;
  color: #176be9;
  font-size: 1rem;
  font-weight: 950;
  min-width: 72px;
  padding: 10px 14px;
  text-align: center;
}

.dashboard-recommend-empty {
  background: #f7fbff;
  border: 1px dashed #b9cce6;
  border-radius: 14px;
  color: #64748b;
  padding: 28px;
  text-align: center;
}

.dashboard-recommend-empty strong {
  color: #0f2745;
  display: block;
  margin-bottom: 6px;
}

.dashboard-more-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.recommend-more-button {
  align-items: center;
  background: #fff;
  border: 1px solid #c5d9f4;
  border-radius: 999px;
  color: #176be9;
  cursor: pointer;
  display: inline-flex;
  font-weight: 900;
  gap: 8px;
  justify-content: center;
  min-width: 120px;
  padding: 9px 18px;
}

@media (max-width: 1100px) {
  .dashboard-asset-layout {
    grid-template-columns: 1fr;
  }

  .dashboard-asset-info-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .recommend-panel-head {
    flex-direction: column;
  }

  .favorite-list-link,
  .recommend-tabs {
    justify-content: center;
  }

  .recommend-tabs {
    width: 100%;
  }

  .recommend-tabs button {
    flex: 1;
  }

  .refined-recommend-item {
    grid-template-columns: 48px minmax(0, 1fr);
  }

  .recommend-row-actions {
    grid-column: 1 / -1;
    justify-content: space-between;
  }
}

@media (max-width: 560px) {
  .asset-donut {
    width: 196px;
  }

  .asset-donut::after,
  .asset-donut-center {
    inset: 48px;
  }

  .dashboard-asset-info-grid {
    grid-template-columns: 1fr;
  }

  .recommend-tabs {
    overflow-x: auto;
  }

  .recommend-tabs button {
    flex: 1 0 auto;
  }
}
</style>
