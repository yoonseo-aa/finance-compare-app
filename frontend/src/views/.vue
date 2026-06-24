<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFetch, getToken } from "../api/client";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const items = ref([]);
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const usingPublicData = ref(false);
const activeResult = ref("top");

const form = reactive({
  direction: "forward",
  productType: "saving",
  monthlySaving: 300000,
  depositAmount: 5000000,
  targetAmount: 10000000,
  preferredTerm: 24,
  riskTolerance: "stable",
  purpose: "목돈"
});

const audienceChips = [
  { label: "전체", count: 212 },
  { label: "청년", count: 22 },
  { label: "시니어", count: 4 },
  { label: "다자녀", count: 5 },
  { label: "한부모", count: 3 },
  { label: "장애인", count: 2 },
  { label: "주택청약", count: 4 },
  { label: "소상공인", count: 2 }
];

const purposeChips = ["결혼자금", "차 구매", "여행", "목돈", "학자금"];
const activeAudiences = ref(["전체"]);

const filteredItems = computed(() => {
  const filtered = items.value.filter(item => {
    if (form.productType === "all") return true;
    return item.product.product_type === form.productType;
  });

  return [...filtered].sort((a, b) => {
    if (activeResult.value === "rate") return Number(b.option.intr_rate2) - Number(a.option.intr_rate2);
    if (activeResult.value === "easy") return conditionScore(b) - conditionScore(a);
    return displayScore(b) - displayScore(a);
  });
});

const summary = computed(() => {
  const list = filteredItems.value;
  const top = list[0];
  const topRate = top ? Number(top.option.intr_rate2).toFixed(2) : "0.00";
  const maturity = top ? estimateMaturity(top) : 0;

  return {
    count: list.length,
    topRate,
    maturity,
    taxLabel: "세후, 일반과세 15.4%"
  };
});

function normalizeRecommendation(raw) {
  const option = raw.option || {};
  return {
    product: raw.product,
    option: {
      id: option.id || raw.product.id,
      save_term: Number(option.save_term || form.preferredTerm),
      intr_rate: Number(option.intr_rate || raw.product.best_rate || 0),
      intr_rate2: Number(option.intr_rate2 || raw.product.best_rate || 0),
      rate_type: option.rate_type || "단리"
    },
    score: Number(raw.score || Number(raw.product.best_rate || 0) * 10),
    reasons: raw.reasons || [
      `최고 우대금리 ${raw.product.best_rate || 0}%`,
      `${form.preferredTerm}개월 조건으로 비교 가능`
    ]
  };
}

function bestOptionFromDetail(product) {
  const options = product.options || [];
  const best = [...options].sort((a, b) => Number(b.intr_rate2) - Number(a.intr_rate2))[0];
  return normalizeRecommendation({
    product,
    option: best || {
      save_term: form.preferredTerm,
      intr_rate: product.best_rate || 0,
      intr_rate2: product.best_rate || 0
    },
    score: Number(product.best_rate || 0) * 10,
    reasons: [
      `최고 우대금리 ${product.best_rate || 0}%`,
      "공개 상품 데이터 기준 추천"
    ]
  });
}

async function loadPublicRecommendations() {
  const products = await apiFetch("/products/?sort=rate");
  const topProducts = products.slice(0, 8);
  const details = await Promise.all(
    topProducts.map(product => apiFetch(`/products/${product.id}/`).catch(() => product))
  );
  items.value = details.map(bestOptionFromDetail);
  usingPublicData.value = true;
}

async function loadRecommendations() {
  loading.value = true;
  error.value = "";

  try {
    if (getToken()) {
      const data = await apiFetch("/recommendations/?limit=12");
      items.value = data.map(normalizeRecommendation);
      usingPublicData.value = false;
    } else {
      await loadPublicRecommendations();
    }
  } catch (err) {
    try {
      await loadPublicRecommendations();
      error.value = "";
    } catch {
      error.value = err.message;
    }
  } finally {
    loading.value = false;
  }
}

function formatWon(value) {
  return `${Math.round(Number(value || 0)).toLocaleString("ko-KR")}원`;
}

function step(field, amount, min) {
  form[field] = Math.max(min, Number(form[field] || 0) + amount);
}

function toggleAudience(label) {
  if (label === "전체") {
    activeAudiences.value = ["전체"];
    return;
  }

  const next = activeAudiences.value.filter(item => item !== "전체");
  const index = next.indexOf(label);
  if (index >= 0) next.splice(index, 1);
  else next.push(label);
  activeAudiences.value = next.length ? next : ["전체"];
}

function conditionScore(item) {
  const text = `${item.product.name} ${item.product.bank_name} ${item.reasons.join(" ")}`;
  let score = 0;
  if (text.includes("청년")) score += 8;
  if (text.includes("우대")) score += 6;
  if (text.includes("비대면") || text.includes("인터넷")) score += 5;
  if (text.includes("첫")) score += 4;
  return score;
}

function displayScore(item) {
  const audienceBonus = activeAudiences.value.includes("전체") ? 0 : activeAudiences.value.length * 2;
  const purposeBonus = form.purpose ? 2 : 0;
  return Math.round(Number(item.score || 0) + audienceBonus + purposeBonus);
}

function estimateMaturity(item) {
  const months = Number(item.option.save_term || form.preferredTerm || 12);
  const rate = Number(item.option.intr_rate2 || 0) / 100;

  if (item.product.product_type === "deposit") {
    const interest = form.depositAmount * rate * (months / 12);
    return form.depositAmount + interest * 0.846;
  }

  const principal = form.monthlySaving * months;
  const interest = form.monthlySaving * rate * ((months + 1) / 2);
  return principal + interest * 0.846;
}

function estimateInterest(item) {
  const base = item.product.product_type === "deposit"
    ? form.depositAmount
    : form.monthlySaving * Number(item.option.save_term || form.preferredTerm || 12);
  return Math.max(0, estimateMaturity(item) - base);
}

async function applyRecommendation() {
  saving.value = true;
  error.value = "";

  try {
    if (auth.user) {
      await auth.updateProfile({
        monthly_saving: form.monthlySaving,
        preferred_term: form.preferredTerm,
        risk_tolerance: form.riskTolerance
      });
    }
    await loadRecommendations();
  } catch (err) {
    error.value = err.message;
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  if (getToken() && !auth.user) await auth.bootstrap();
  if (auth.user) {
    form.monthlySaving = auth.user.monthly_saving || form.monthlySaving;
    form.preferredTerm = auth.user.preferred_term || form.preferredTerm;
    form.riskTolerance = auth.user.risk_tolerance || form.riskTolerance;
  }
  await loadRecommendations();
});
</script>

<template>
  <main class="recommend-ref-page">
    <section class="recommend-ref-shell">
      <header class="recommend-app-head">
        <RouterLink class="recommend-back" to="/">‹</RouterLink>
        <div class="recommend-title-chip">💰</div>
        <strong>예적금 금리비교</strong>
        <RouterLink class="recommend-close" to="/products">전체상품</RouterLink>
      </header>

      <section class="recommend-intro">
        <p>FinPick 추천</p>
        <h1>목표를 입력하면<br>내 조건의 예적금 TOP 5</h1>
        <span>전국 금융상품 데이터와 내 조건을 함께 비교합니다.</span>
      </section>

      <nav class="recommend-icon-tabs" aria-label="추천 메뉴">
        <RouterLink to="/products"><span>🏦</span>정기예금</RouterLink>
        <button type="button" :class="{ active: form.productType === 'saving' }" @click="form.productType = 'saving'"><span>🐷</span>적금</button>
        <button type="button" class="active"><span>🎯</span>추천</button>
        <button type="button"><span>⭐</span>즐겨찾기</button>
        <button type="button"><span>🧮</span>계산기</button>
      </nav>

      <section class="recommend-calculator">
        <div class="calculator-head">
          <div>
            <h2>🎯 목표를 입력하면<br>만기 수령액 TOP 5</h2>
            <p>전국 상품 중 세후 실수령액과 추천점수 기준</p>
          </div>
          <div class="calculator-rate">
            <span>최고금리</span>
            <strong>{{ summary.topRate }}%</strong>
          </div>
        </div>

        <div class="pill-switch">
          <button type="button" :class="{ active: form.direction === 'forward' }" @click="form.direction = 'forward'">📥 정방향</button>
          <button type="button" :class="{ active: form.direction === 'target' }" @click="form.direction = 'target'">🎯 목표 역산</button>
        </div>

        <div class="pill-switch product-switch">
          <button type="button" :class="{ active: form.productType === 'deposit' }" @click="form.productType = 'deposit'">🏦 정기예금</button>
          <button type="button" :class="{ active: form.productType === 'saving' }" @click="form.productType = 'saving'">🐷 적금</button>
          <button type="button" :class="{ active: form.productType === 'all' }" @click="form.productType = 'all'">전체</button>
        </div>

        <div class="amount-grid">
          <div class="amount-box">
            <span>{{ form.productType === "deposit" ? "예치금" : "월 납입액" }}</span>
            <div>
              <button type="button" @click="step(form.productType === 'deposit' ? 'depositAmount' : 'monthlySaving', form.productType === 'deposit' ? -1000000 : -100000, 0)">−</button>
              <strong>{{ formatWon(form.productType === "deposit" ? form.depositAmount : form.monthlySaving).replace("원", "") }}</strong>
              <button type="button" @click="step(form.productType === 'deposit' ? 'depositAmount' : 'monthlySaving', form.productType === 'deposit' ? 1000000 : 100000, 0)">+</button>
            </div>
          </div>
          <div class="amount-box">
            <span>{{ form.direction === "target" ? "목표 금액" : "기간" }}</span>
            <div>
              <button type="button" @click="step(form.direction === 'target' ? 'targetAmount' : 'preferredTerm', form.direction === 'target' ? -1000000 : -6, form.direction === 'target' ? 1000000 : 6)">−</button>
              <strong>{{ form.direction === "target" ? formatWon(form.targetAmount).replace("원", "") : `${form.preferredTerm}개월` }}</strong>
              <button type="button" @click="step(form.direction === 'target' ? 'targetAmount' : 'preferredTerm', form.direction === 'target' ? 1000000 : 6, form.direction === 'target' ? 1000000 : 6)">+</button>
            </div>
          </div>
        </div>

        <button class="recommend-submit" type="button" :disabled="saving" @click="applyRecommendation">
          {{ saving ? "다시 계산 중" : "이 조건으로 추천 보기" }}
        </button>
      </section>

      <section class="recommend-chip-group" aria-label="대상 조건">
        <button
          v-for="chip in audienceChips"
          :key="chip.label"
          type="button"
          :class="{ active: activeAudiences.includes(chip.label) }"
          @click="toggleAudience(chip.label)"
        >
          {{ chip.label }} <strong>{{ chip.count }}</strong>
        </button>
      </section>

      <section class="recommend-purpose-group" aria-label="저축 목적">
        <button
          v-for="purpose in purposeChips"
          :key="purpose"
          type="button"
          :class="{ active: form.purpose === purpose }"
          @click="form.purpose = purpose"
        >
          {{ purpose }}
        </button>
      </section>

      <section class="recommend-mini-summary">
        <article>
          <span>추천 상품</span>
          <strong>{{ summary.count }}개</strong>
        </article>
        <article>
          <span>예상 1위 수령액</span>
          <strong>{{ formatWon(summary.maturity) }}</strong>
        </article>
        <article>
          <span>기준</span>
          <strong>{{ summary.taxLabel }}</strong>
        </article>
      </section>

      <section class="recommend-ranking-section">
        <div class="ranking-title-row">
          <div>
            <h2>📊 만기 수령액 TOP 5</h2>
            <p v-if="usingPublicData">로그인 전이라 공개 상품 데이터 기준으로 먼저 보여드려요.</p>
            <p v-else>내 프로필과 추천점수를 함께 반영했습니다.</p>
          </div>
          <div class="ranking-sort">
            <button type="button" :class="{ active: activeResult === 'top' }" @click="activeResult = 'top'">추천순</button>
            <button type="button" :class="{ active: activeResult === 'rate' }" @click="activeResult = 'rate'">금리순</button>
            <button type="button" :class="{ active: activeResult === 'easy' }" @click="activeResult = 'easy'">조건쉬운순</button>
          </div>
        </div>

        <div v-if="loading" class="recommend-state">추천 상품을 계산하고 있습니다.</div>
        <div v-else-if="error" class="recommend-state warning">{{ error }}</div>
        <div v-else-if="!filteredItems.length" class="recommend-state">조건에 맞는 상품이 없습니다.</div>

        <div class="recommend-rank-list">
          <RouterLink
            v-for="(item, index) in filteredItems.slice(0, 5)"
            :key="`${item.product.id}-${item.option.id}`"
            class="recommend-rank-card"
            :class="{ winner: index === 0 }"
            :to="`/products/${item.product.id}`"
          >
            <span class="rank-number">{{ index + 1 }}</span>
            <div class="rank-product">
              <span>{{ item.product.bank_name }}</span>
              <h3>{{ item.product.name }}</h3>
              <p>{{ item.option.save_term }}개월 · 최고 {{ item.option.intr_rate2 }}% · 추천점수 {{ displayScore(item) }}점</p>
              <div class="reason-row">
                <em v-for="reason in item.reasons.slice(0, 2)" :key="reason">{{ reason }}</em>
              </div>
            </div>
            <div class="rank-value">
              <strong>{{ formatWon(estimateMaturity(item)) }}</strong>
              <span>+ {{ formatWon(estimateInterest(item)) }}</span>
            </div>
          </RouterLink>
        </div>
      </section>
    </section>
  </main>
</template>
