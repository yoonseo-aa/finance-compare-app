<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFetch, getToken } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const usingPublicData = ref(false);
const items = ref([]);
const resultMode = ref("score");

const form = reactive({
  direction: "forward",
  productType: "all",
  audience: "all",
  monthlySaving: 300000,
  depositAmount: 5000000,
  targetAmount: 10000000,
  preferredTerm: 24,
  riskTolerance: "balanced",
  purpose: "목돈 마련"
});

const productTypes = [
  { label: "전체", value: "all", description: "예금과 적금을 함께 비교합니다." },
  { label: "정기예금", value: "deposit", description: "목돈을 한 번에 예치하는 상품을 봅니다." },
  { label: "적금", value: "saving", description: "매월 저축하는 상품을 봅니다." }
];

const audiences = [
  {
    label: "전체",
    value: "all",
    count: 212,
    title: "전체 예적금 추천 서비스",
    description: "기간, 금리, 예상 수령액을 기준으로 모든 상품을 비교합니다."
  },
  {
    label: "청년",
    value: "youth",
    count: 22,
    title: "청년 추천용 예적금 서비스",
    description: "첫 거래, 비대면, 급여이체 조건이 맞는 상품을 우선 확인합니다."
  },
  {
    label: "신혼/부부",
    value: "couple",
    count: 8,
    title: "신혼/부부 목적자금 추천",
    description: "결혼자금, 주거자금처럼 목표 기간이 뚜렷한 상품을 강조합니다."
  },
  {
    label: "시니어",
    value: "senior",
    count: 4,
    title: "시니어 안정형 예적금 추천",
    description: "안정성과 가입 조건이 단순한 상품을 우선 정렬합니다."
  },
  {
    label: "소상공인",
    value: "business",
    count: 2,
    title: "소상공인 현금흐름 추천",
    description: "짧은 기간과 월 저축 부담이 낮은 상품을 함께 비교합니다."
  }
];

const purposes = ["목돈 마련", "결혼자금", "차 구매", "여행", "학자금", "비상금"];

const activeAudience = computed(() => audiences.find(item => item.value === form.audience) || audiences[0]);

const joinedProductIds = computed(() => {
  const joined = auth.user?.joined_products || [];
  return new Set(joined.map(product => Number(product.id)));
});

const visibleItems = computed(() => {
  const filtered = items.value.filter(item => {
    if (form.productType !== "all" && item.product.product_type !== form.productType) return false;
    return true;
  });

  return [...filtered].sort((a, b) => {
    if (resultMode.value === "rate") return Number(b.option.intr_rate2) - Number(a.option.intr_rate2);
    if (resultMode.value === "maturity") return estimateMaturity(b) - estimateMaturity(a);
    if (resultMode.value === "easy") return conditionEaseScore(b) - conditionEaseScore(a);
    return recommendationScore(b) - recommendationScore(a);
  });
});

const favoriteItems = computed(() => visibleItems.value.filter(item => joinedProductIds.value.has(Number(item.product.id))));

const summary = computed(() => {
  const list = visibleItems.value;
  const top = list[0];
  const rates = list.map(item => Number(item.option.intr_rate2 || 0)).filter(Boolean);
  const averageRate = rates.length ? rates.reduce((total, rate) => total + rate, 0) / rates.length : 0;

  return {
    count: list.length,
    topRate: top ? Number(top.option.intr_rate2 || 0) : 0,
    averageRate,
    topMaturity: top ? estimateMaturity(top) : 0,
    favoriteCount: favoriteItems.value.length
  };
});

function productTypeLabel(type) {
  if (type === "deposit") return "정기예금";
  if (type === "saving") return "적금";
  return "금융상품";
}

function normalizeItem(raw) {
  const product = raw.product || raw;
  const option = raw.option || {};
  const bestRate = Number(option.intr_rate2 || product.best_rate || 0);

  return {
    product,
    option: {
      id: option.id || `${product.id}-best`,
      save_term: Number(option.save_term || form.preferredTerm || 12),
      intr_rate: Number(option.intr_rate || bestRate),
      intr_rate2: bestRate,
      rate_type: option.rate_type || "단리"
    },
    score: Number(raw.score || bestRate * 10),
    reasons: raw.reasons?.length
      ? raw.reasons.map(reason => cleanReason(reason))
      : [
          `최고 우대금리 ${bestRate.toFixed(2)}% 기준`,
          `${productTypeLabel(product.product_type)} 상품 중 금리 경쟁력이 높습니다.`
        ]
  };
}

function cleanReason(reason) {
  return String(reason)
    .replaceAll("score", "추천점수")
    .replaceAll("ease", "조건 충족률")
    .replaceAll("·", " ");
}

function bestOptionFromProduct(product) {
  const options = product.options || [];
  const matched = [...options].sort((a, b) => {
    const aGap = Math.abs(Number(a.save_term || 0) - form.preferredTerm);
    const bGap = Math.abs(Number(b.save_term || 0) - form.preferredTerm);
    if (aGap !== bGap) return aGap - bGap;
    return Number(b.intr_rate2 || 0) - Number(a.intr_rate2 || 0);
  })[0];

  return normalizeItem({
    product,
    option: matched || {
      save_term: form.preferredTerm,
      intr_rate: product.best_rate || 0,
      intr_rate2: product.best_rate || 0
    }
  });
}

function mergeItems(primary, fallback) {
  const seen = new Set();
  return [...primary, ...fallback].filter(item => {
    const key = Number(item.product.id);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function loadPublicItems(limit = 24) {
  const products = await apiFetch("/products/?sort=rate");
  const details = await Promise.all(
    products.slice(0, limit).map(product => apiFetch(`/products/${product.id}/`).catch(() => product))
  );
  return details.map(bestOptionFromProduct);
}

async function loadRecommendations() {
  loading.value = true;
  error.value = "";

  try {
    const publicItems = await loadPublicItems();
    if (getToken()) {
      const data = await apiFetch("/recommendations/");
      items.value = mergeItems(data.map(normalizeItem), publicItems);
      usingPublicData.value = data.length === 0;
    } else {
      items.value = publicItems;
      usingPublicData.value = true;
    }
  } catch (err) {
    try {
      items.value = await loadPublicItems();
      usingPublicData.value = true;
      error.value = "";
    } catch {
      error.value = err.message || "추천 데이터를 불러오지 못했습니다.";
    }
  } finally {
    loading.value = false;
  }
}

function formatMoney(value) {
  return `${Math.round(Number(value || 0)).toLocaleString("ko-KR")}원`;
}

function formatShortMoney(value) {
  const amount = Number(value || 0);
  if (amount >= 10000) return `${Math.round(amount / 10000).toLocaleString("ko-KR")}만원`;
  return formatMoney(amount);
}

function changeValue(field, amount, minimum) {
  form[field] = Math.max(minimum, Number(form[field] || 0) + amount);
}

function selectAudience(value) {
  form.audience = value;
  if (value === "youth") {
    form.riskTolerance = "balanced";
    form.purpose = "목돈 마련";
  }
  if (value === "couple") {
    form.purpose = "결혼자금";
    form.preferredTerm = Math.max(form.preferredTerm, 24);
  }
  if (value === "senior") {
    form.riskTolerance = "stable";
    form.productType = "deposit";
  }
  if (value === "business") {
    form.preferredTerm = Math.min(form.preferredTerm, 12);
    form.purpose = "비상금";
  }
}

function conditionText(item) {
  return `${item.product.name || ""} ${item.product.bank_name || ""} ${item.product.special_condition || ""} ${item.product.etc_note || ""} ${item.reasons.join(" ")}`;
}

function conditionEaseScore(item) {
  const text = conditionText(item);
  let score = 50;
  if (text.includes("비대면") || text.includes("인터넷") || text.includes("스마트")) score += 15;
  if (text.includes("자동이체")) score += 10;
  if (text.includes("급여")) score += 8;
  if (text.includes("첫") || text.includes("신규")) score += 6;
  return Math.min(score, 100);
}

function audienceScore(item) {
  const text = conditionText(item);
  if (form.audience === "all") return 0;
  if (form.audience === "youth") return text.includes("청년") || text.includes("첫") || text.includes("급여") ? 12 : 4;
  if (form.audience === "couple") return form.purpose === "결혼자금" || text.includes("주택") ? 10 : 4;
  if (form.audience === "senior") return item.product.product_type === "deposit" ? 12 : 3;
  if (form.audience === "business") return item.option.save_term <= 12 ? 8 : 2;
  return 0;
}

function recommendationScore(item) {
  const purposeBonus = form.purpose ? 3 : 0;
  const typeBonus = form.productType !== "all" && item.product.product_type === form.productType ? 5 : 0;
  const termGap = Math.abs(Number(item.option.save_term || 0) - form.preferredTerm);
  const termBonus = Math.max(0, 16 - termGap);
  const easyBonus = Math.round(conditionEaseScore(item) / 12);
  return Math.round(Number(item.score || 0) + audienceScore(item) + purposeBonus + typeBonus + termBonus + easyBonus);
}

function estimateMaturity(item) {
  const months = Number(item.option.save_term || form.preferredTerm || 12);
  const annualRate = Number(item.option.intr_rate2 || 0) / 100;

  if (item.product.product_type === "deposit") {
    const interest = form.depositAmount * annualRate * (months / 12);
    return form.depositAmount + interest * 0.846;
  }

  const principal = form.monthlySaving * months;
  const interest = form.monthlySaving * annualRate * ((months + 1) / 2);
  return principal + interest * 0.846;
}

function estimateInterest(item) {
  const months = Number(item.option.save_term || form.preferredTerm || 12);
  const principal = item.product.product_type === "deposit" ? form.depositAmount : form.monthlySaving * months;
  return Math.max(0, estimateMaturity(item) - principal);
}

async function applyDiagnosis() {
  saving.value = true;
  error.value = "";

  try {
    if (auth.user) {
      await auth.updateProfile({
        monthly_saving: form.monthlySaving,
        savings_goal: form.targetAmount,
        preferred_term: form.preferredTerm,
        risk_tolerance: form.riskTolerance
      });
    }
    await loadRecommendations();
  } catch (err) {
    error.value = err.message || "추천 조건을 반영하지 못했습니다.";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  if (getToken() && !auth.user) await auth.bootstrap();
  if (auth.user) {
    form.monthlySaving = auth.user.monthly_saving || form.monthlySaving;
    form.targetAmount = auth.user.savings_goal || form.targetAmount;
    form.preferredTerm = auth.user.preferred_term || form.preferredTerm;
    form.riskTolerance = auth.user.risk_tolerance || form.riskTolerance;
  }
  await loadRecommendations();
});
</script>

<template>
  <main class="recommend-page-local">
    <section class="container recommend-container-local">
      <div class="section-head recommend-head-local">
        <div>
          <p class="eyebrow">FinPick recommendation</p>
          <h1>예적금 추천</h1>
          <p>금리만 높은 상품이 아니라, 내 조건에서 실제로 유리한 예적금 상품을 비교합니다.</p>
        </div>
        <div class="head-actions-local">
          <RouterLink class="btn ghost" to="/products">전체 상품 보기</RouterLink>
          <RouterLink class="btn plain" to="/dashboard">대시보드</RouterLink>
        </div>
      </div>

      <StatusBlock :loading="loading" :error="error" />

      <section class="service-panel-local">
        <div>
          <span>선택한 추천 서비스</span>
          <h2>{{ activeAudience.title }}</h2>
          <p>{{ activeAudience.description }}</p>
        </div>
        <div class="service-stats-local">
          <article>
            <span>추천 대상</span>
            <strong>{{ summary.count }}개</strong>
          </article>
          <article>
            <span>최고 금리</span>
            <strong>{{ summary.topRate.toFixed(2) }}%</strong>
          </article>
          <article>
            <span>관심 상품</span>
            <strong>{{ summary.favoriteCount }}개</strong>
          </article>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="section-head">
          <h2>추천 조건</h2>
          <p>서비스 대상, 상품 유형, 저축 조건을 바꾸면 아래 추천 결과가 함께 바뀝니다.</p>
        </div>

        <div class="workspace-local">
          <article class="content-panel filter-panel-local">
            <div class="control-group-local">
              <h3>추천 서비스</h3>
              <div class="segment-grid-local audience">
                <button
                  v-for="audience in audiences"
                  :key="audience.value"
                  type="button"
                  :class="{ active: form.audience === audience.value }"
                  @click="selectAudience(audience.value)"
                >
                  <span>{{ audience.label }}</span>
                  <small>{{ audience.count }}개</small>
                </button>
              </div>
            </div>

            <div class="control-group-local">
              <h3>상품 유형</h3>
              <div class="segment-grid-local three">
                <button
                  v-for="type in productTypes"
                  :key="type.value"
                  type="button"
                  :class="{ active: form.productType === type.value }"
                  @click="form.productType = type.value"
                >
                  <span>{{ type.label }}</span>
                  <small>{{ type.description }}</small>
                </button>
              </div>
            </div>

            <div class="control-group-local">
              <h3>계산 방식</h3>
              <div class="segment-grid-local two">
                <button type="button" :class="{ active: form.direction === 'forward' }" @click="form.direction = 'forward'">
                  <span>정방향 계산</span>
                  <small>월 저축액으로 예상 수령액 계산</small>
                </button>
                <button type="button" :class="{ active: form.direction === 'target' }" @click="form.direction = 'target'">
                  <span>목표 역산</span>
                  <small>목표금액 기준으로 필요한 조건 확인</small>
                </button>
              </div>
            </div>

            <div class="input-grid-local">
              <article class="step-box-local">
                <span>{{ form.productType === "deposit" ? "예치 가능 금액" : "월 저축 가능 금액" }}</span>
                <div>
                  <button
                    type="button"
                    @click="changeValue(form.productType === 'deposit' ? 'depositAmount' : 'monthlySaving', form.productType === 'deposit' ? -1000000 : -100000, 0)"
                  >-</button>
                  <strong>{{ formatShortMoney(form.productType === "deposit" ? form.depositAmount : form.monthlySaving) }}</strong>
                  <button
                    type="button"
                    @click="changeValue(form.productType === 'deposit' ? 'depositAmount' : 'monthlySaving', form.productType === 'deposit' ? 1000000 : 100000, 0)"
                  >+</button>
                </div>
              </article>

              <article class="step-box-local">
                <span>{{ form.direction === "target" ? "목표 금액" : "희망 기간" }}</span>
                <div>
                  <button
                    type="button"
                    @click="changeValue(form.direction === 'target' ? 'targetAmount' : 'preferredTerm', form.direction === 'target' ? -1000000 : -6, form.direction === 'target' ? 1000000 : 6)"
                  >-</button>
                  <strong>{{ form.direction === "target" ? formatShortMoney(form.targetAmount) : `${form.preferredTerm}개월` }}</strong>
                  <button
                    type="button"
                    @click="changeValue(form.direction === 'target' ? 'targetAmount' : 'preferredTerm', form.direction === 'target' ? 1000000 : 6, form.direction === 'target' ? 1000000 : 6)"
                  >+</button>
                </div>
              </article>

              <label>
                <span>저축 목적</span>
                <select v-model="form.purpose">
                  <option v-for="purpose in purposes" :key="purpose" :value="purpose">{{ purpose }}</option>
                </select>
              </label>

              <label>
                <span>추천 성향</span>
                <select v-model="form.riskTolerance">
                  <option value="stable">안정형</option>
                  <option value="balanced">균형형</option>
                  <option value="aggressive">고금리형</option>
                </select>
              </label>
            </div>

            <div class="purpose-row-local">
              <button
                v-for="purpose in purposes"
                :key="purpose"
                type="button"
                :class="{ active: form.purpose === purpose }"
                @click="form.purpose = purpose"
              >
                {{ purpose }}
              </button>
            </div>

            <button class="btn primary full" type="button" :disabled="saving" @click="applyDiagnosis">
              {{ saving ? "조건 반영 중" : "내 조건으로 추천 보기" }}
            </button>
          </article>

          <aside class="content-panel summary-panel-local">
            <h3>추천 요약</h3>
            <div class="summary-list-local">
              <article>
                <span>평균 최고금리</span>
                <strong>{{ summary.averageRate.toFixed(2) }}%</strong>
              </article>
              <article>
                <span>1위 예상 수령액</span>
                <strong>{{ formatMoney(summary.topMaturity) }}</strong>
              </article>
              <article>
                <span>선택 조건</span>
                <strong>{{ activeAudience.label }} · {{ productTypes.find(type => type.value === form.productType)?.label }}</strong>
              </article>
            </div>
            <p v-if="usingPublicData" class="muted">로그인 전에는 공개 상품 데이터를 기준으로 추천 결과를 먼저 보여드립니다.</p>
            <p v-else class="muted">내 프로필과 추천점수를 함께 반영해 정렬했습니다.</p>
          </aside>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="result-head-local">
          <div class="section-head">
            <h2>추천 결과 TOP 5</h2>
            <p>추천점수, 만기 수령액, 금리, 우대조건 쉬운순으로 비교할 수 있습니다.</p>
          </div>
          <div class="sort-tabs-local">
            <button type="button" :class="{ active: resultMode === 'score' }" @click="resultMode = 'score'">추천순</button>
            <button type="button" :class="{ active: resultMode === 'maturity' }" @click="resultMode = 'maturity'">수령액순</button>
            <button type="button" :class="{ active: resultMode === 'rate' }" @click="resultMode = 'rate'">금리순</button>
            <button type="button" :class="{ active: resultMode === 'easy' }" @click="resultMode = 'easy'">조건 쉬운순</button>
          </div>
        </div>

        <div v-if="!loading && !visibleItems.length" class="status-block">조건에 맞는 상품이 없습니다.</div>

        <div class="result-list-local">
          <RouterLink
            v-for="(item, index) in visibleItems.slice(0, 5)"
            :key="`${item.product.id}-${item.option.id}`"
            class="result-card-local"
            :class="{ featured: index === 0 }"
            :to="`/products/${item.product.id}`"
          >
            <span class="rank-local">{{ index + 1 }}</span>
            <div class="product-main-local">
              <span>{{ item.product.bank_name }} · {{ productTypeLabel(item.product.product_type) }}</span>
              <h3>{{ item.product.name }}</h3>
              <p>{{ item.option.save_term }}개월 · 최고 {{ item.option.intr_rate2.toFixed(2) }}% · 추천점수 {{ recommendationScore(item) }}점</p>
              <div>
                <em v-for="reason in item.reasons.slice(0, 2)" :key="reason">{{ reason }}</em>
              </div>
            </div>
            <div class="result-money-local">
              <span>세후 예상 수령액</span>
              <strong>{{ formatMoney(estimateMaturity(item)) }}</strong>
              <small>예상 이자 + {{ formatMoney(estimateInterest(item)) }}</small>
            </div>
          </RouterLink>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.recommend-page-local {
  min-height: calc(100vh - 72px);
  background: #f5f7fb;
}

.recommend-container-local {
  padding-top: 2.4rem;
}

.recommend-head-local,
.result-head-local {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
}

.recommend-head-local h1 {
  font-size: clamp(2rem, 4.5vw, 3.4rem);
}

.head-actions-local,
.sort-tabs-local,
.purpose-row-local {
  display: flex;
  align-items: center;
  gap: .6rem;
  flex-wrap: wrap;
}

.service-panel-local {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, .85fr);
  gap: 1rem;
  align-items: stretch;
  margin-top: 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(120deg, #f6f9ff, #edf8f6);
  box-shadow: 0 8px 24px rgba(23, 32, 51, .05);
  padding: 1.25rem;
}

.service-panel-local > div > span,
.summary-panel-local h3,
.control-group-local h3 {
  color: var(--teal);
  font-weight: 900;
}

.service-panel-local h2 {
  margin: .35rem 0 .45rem;
  font-size: clamp(1.55rem, 3vw, 2.25rem);
  letter-spacing: 0;
}

.service-panel-local p,
.summary-panel-local p {
  margin: 0;
  color: var(--muted);
  line-height: 1.65;
}

.service-stats-local,
.summary-list-local {
  display: grid;
  gap: .75rem;
}

.service-stats-local {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.service-stats-local article,
.summary-list-local article {
  border: 1px solid #d7e4f5;
  border-radius: 8px;
  background: rgba(255, 255, 255, .82);
  padding: .95rem;
}

.service-stats-local span,
.summary-list-local span,
.step-box-local > span,
.input-grid-local label > span,
.result-money-local span {
  display: block;
  color: var(--muted);
  font-size: .88rem;
  font-weight: 900;
}

.service-stats-local strong,
.summary-list-local strong {
  display: block;
  margin-top: .35rem;
  color: var(--blue);
  font-size: 1.35rem;
}

.workspace-local {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, .6fr);
  gap: 1rem;
  align-items: start;
}

.filter-panel-local,
.summary-panel-local,
.control-group-local {
  display: grid;
  gap: 1rem;
}

.control-group-local h3,
.summary-panel-local h3 {
  margin: 0;
  font-size: 1rem;
}

.segment-grid-local {
  display: grid;
  gap: .6rem;
}

.segment-grid-local.audience {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.segment-grid-local.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.segment-grid-local.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.segment-grid-local button,
.purpose-row-local button,
.sort-tabs-local button {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
  font-weight: 900;
}

.segment-grid-local button {
  min-height: 76px;
  padding: .85rem;
  text-align: left;
}

.segment-grid-local button span,
.segment-grid-local button small {
  display: block;
}

.segment-grid-local button small {
  margin-top: .28rem;
  color: var(--muted);
  font-size: .78rem;
  font-weight: 800;
  line-height: 1.35;
}

.segment-grid-local button.active,
.purpose-row-local button.active,
.sort-tabs-local button.active {
  border-color: #9fc0ff;
  background: #eff6ff;
  color: var(--blue);
  box-shadow: 0 8px 18px rgba(37, 99, 235, .09);
}

.input-grid-local {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .8rem;
}

.step-box-local,
.input-grid-local label {
  display: grid;
  gap: .55rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 1rem;
}

.step-box-local div {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) 42px;
  gap: .6rem;
  align-items: center;
}

.step-box-local button {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 8px;
  background: #eef3f8;
  color: var(--ink);
  font-size: 1.2rem;
  font-weight: 900;
  cursor: pointer;
}

.step-box-local strong {
  overflow-wrap: anywhere;
  text-align: center;
  font-size: 1.35rem;
}

.purpose-row-local button,
.sort-tabs-local button {
  min-height: 38px;
  padding: .45rem .85rem;
}

.summary-panel-local {
  position: sticky;
  top: 92px;
}

.result-head-local {
  margin-bottom: 1rem;
}

.result-list-local {
  display: grid;
  gap: .85rem;
}

.result-card-local {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) minmax(220px, auto);
  gap: 1rem;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: inherit;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(23, 32, 51, .05);
  padding: 1rem;
}

.result-card-local.featured {
  border-color: #93c5fd;
  box-shadow: 0 12px 30px rgba(37, 99, 235, .1);
}

.rank-local {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: #eef3f8;
  color: var(--muted);
  font-weight: 900;
  font-size: 1.1rem;
}

.featured .rank-local {
  background: var(--blue);
  color: #fff;
}

.product-main-local > span {
  color: var(--muted);
  font-weight: 900;
}

.product-main-local h3 {
  margin: .25rem 0;
  font-size: 1.15rem;
}

.product-main-local p {
  margin: 0;
  color: var(--muted);
  font-weight: 800;
}

.product-main-local div {
  display: flex;
  flex-wrap: wrap;
  gap: .4rem;
  margin-top: .55rem;
}

.product-main-local em {
  padding: .28rem .55rem;
  border-radius: 999px;
  background: var(--soft);
  color: var(--muted);
  font-size: .78rem;
  font-style: normal;
  font-weight: 800;
}

.result-money-local {
  display: grid;
  justify-items: end;
  gap: .25rem;
}

.result-money-local strong {
  color: var(--blue);
  font-size: 1.35rem;
}

.result-money-local small {
  color: var(--teal);
  font-weight: 900;
}

@media (max-width: 980px) {
  .recommend-head-local,
  .result-head-local {
    display: grid;
    align-items: start;
  }

  .service-panel-local,
  .workspace-local,
  .result-card-local {
    grid-template-columns: 1fr;
  }

  .summary-panel-local {
    position: static;
  }

  .result-money-local {
    justify-items: start;
  }
}

@media (max-width: 720px) {
  .service-stats-local,
  .segment-grid-local.audience,
  .segment-grid-local.two,
  .segment-grid-local.three,
  .input-grid-local {
    grid-template-columns: 1fr;
  }
}
</style>