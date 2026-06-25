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
const activeRecommendationType = ref("deposit");
const loanItems = ref([]);
const loanResultMode = ref("score");
const loanError = ref("");
const savingsItems = ref([]);
const savingsResultMode = ref("score");
const savingsError = ref("");
const aiExplanationLoading = ref(false);
const aiExplanationError = ref("");
const aiExplanations = reactive({ deposit: {}, loan: {}, savings: {} });
const aiExplanationMeta = reactive({
  deposit: { usedAi: false, model: null },
  loan: { usedAi: false, model: null },
  savings: { usedAi: false, model: null }
});

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

const loanForm = reactive({
  audience: "all",
  loanType: "mortgage",
  strategy: "rate",
  desiredAmount: 200000000,
  loanTerm: 30,
  repayType: "원리금균등상환",
  incomeRange: "4000-6000",
  creditGrade: "excellent",
  tags: ["무주택", "직장인"]
});

const savingsForm = reactive({
  audience: "all",
  productType: "all",
  strategy: "rate",
  monthlyAmount: 400000,
  targetAmount: 5000000,
  periodMonths: 12,
  purpose: "목돈 마련",
  preference: "stable",
  tags: ["자유 납입", "우대조건 간단"]
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
    title: "전체 예적금 상품",
    description: "기간, 금리, 예상 수령액을 기준으로 모든 상품을 비교합니다."
  },
  {
    label: "청년",
    value: "youth",
    count: 22,
    title: "청년 추천",
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

const loanAudiences = [
  { label: "전체", value: "all", count: 8, title: "전체 대출 상품", description: "금리, 한도, 상환 부담을 기준으로 조건에 맞는 상품을 추천합니다." },
  { label: "직장인", value: "employee", count: 5, title: "직장인 추천", description: "소득 안정성과 상환 부담을 함께 고려해 상품을 비교합니다." },
  { label: "사회초년생", value: "starter", count: 4, title: "사회초년생 추천", description: "초기 한도와 금리 부담이 낮은 상품을 우선 확인합니다." },
  { label: "신혼부부", value: "newlywed", count: 4, title: "신혼부부 주거 추천", description: "주거 목적과 장기 상환 조건에 맞는 상품을 강조합니다." },
  { label: "자영업자", value: "business", count: 4, title: "자영업자 추천", description: "사업자 조건과 상환 방식이 유연한 상품을 함께 비교합니다." }
];

const loanProductTypes = [
  { label: "주택담보대출", value: "mortgage", description: "주택을 담보로 제공" },
  { label: "전세자금대출", value: "rent", description: "전세 보증금 마련" },
  { label: "개인신용대출", value: "credit", description: "신용을 기반으로 한 대출" }
];

const loanStrategies = [
  { label: "금리 우선", value: "rate", description: "최저 금리 중심 추천" },
  { label: "한도 우선", value: "limit", description: "최대한도 중심 추천" },
  { label: "상환 부담 최소", value: "payment", description: "월 상환액 최소화" },
  { label: "고정/변동 선호", value: "fixed", description: "금리 유형 선호 반영" }
];

const repayTypes = ["원리금균등상환", "원금균등상환", "만기일시상환"];
const incomeRanges = ["2천만 ~ 4천만", "4천만 ~ 6천만", "6천만 ~ 8천만", "8천만 이상"];
const creditGrades = [
  { label: "우수", value: "excellent" },
  { label: "보통", value: "normal" },
  { label: "낮음", value: "low" }
];
const loanTags = ["무주택", "청년", "직장인", "신혼부부", "사업자", "보증서 가능"];

const savingsAudiences = [
  { label: "전체", value: "all", count: 12, title: "전체 저축 상품", description: "목적, 납입 방식, 기간, 수익률을 기준으로 모든 상품을 비교합니다." },
  { label: "청년", value: "youth", count: 6, title: "청년 저축 추천 서비스", description: "월 납입 부담과 자유로운 적립 조건을 함께 비교합니다." },
  { label: "직장인", value: "employee", count: 5, title: "직장인 저축 추천 서비스", description: "급여 흐름에 맞춰 꾸준히 모을 수 있는 상품을 우선 확인합니다." },
  { label: "신혼부부", value: "couple", count: 4, title: "신혼부부 목적자금 저축", description: "목돈 마련과 안정적인 만기 금액을 함께 고려합니다." },
  // { label: "시니어", value: "senior", count: 3, title: "시니어 안정형 저축", description: "조건이 단순하고 안정적인 저축 상품을 중심으로 추천합니다." },
  { label: "소상공인", value: "business", count: 3, title: "소상공인 유동성 저축", description: "현금흐름에 맞춰 유연하게 납입할 수 있는 상품을 비교합니다." }
];

const savingsProductTypes = [
  { label: "전체", value: "all", description: "저축 상품을 함께 비교합니다." },
  { label: "자유적립식 저축", value: "free", description: "원할 때 자유롭게 납입" },
  { label: "정기적립식 저축", value: "regular", description: "매월 일정 금액 납입" },
  { label: "목돈마련 저축", value: "goal", description: "목표 금액 중심 저축" }
];

const savingsStrategies = [
  { label: "금리 우선", value: "rate", description: "높은 수익률 중심 추천" },
  { label: "유연성 우선", value: "flexible", description: "납입 자유도 중심 추천" },
  { label: "목표 달성 우선", value: "target", description: "목표 금액 달성 가능성 중심 추천" },
  { label: "안정성 우선", value: "stable", description: "조건이 단순하고 안정적인 상품 추천" }
];

const savingsPurposes = ["목돈 마련", "비상금", "여행", "학자금", "결혼자금", "단기 저축"];
const savingsPreferences = [
  { label: "안정형", value: "stable" },
  { label: "금리중시형", value: "rate" },
  { label: "유연성중시형", value: "flexible" }
];
const savingsTags = ["자유 납입", "자동이체 가능", "우대조건 간단", "비상금", "목돈 마련", "단기 저축", "장기 저축"];

const activeAudience = computed(() => audiences.find(item => item.value === form.audience) || audiences[0]);
const activeLoanAudience = computed(() => loanAudiences.find(item => item.value === loanForm.audience) || loanAudiences[0]);
const activeLoanType = computed(() => loanProductTypes.find(item => item.value === loanForm.loanType) || loanProductTypes[0]);
const activeSavingsAudience = computed(() => savingsAudiences.find(item => item.value === savingsForm.audience) || savingsAudiences[0]);
const activeSavingsType = computed(() => savingsProductTypes.find(item => item.value === savingsForm.productType) || savingsProductTypes[0]);

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

const visibleLoanItems = computed(() => {
  const filtered = loanItems.value.filter(loan => {
    if (loanForm.loanType !== "all" && loan.loan_type !== loanForm.loanType) return false;
    return true;
  });

  return [...filtered].sort((a, b) => {
    if (loanResultMode.value === "limit") return loanLimitScore(b) - loanLimitScore(a);
    if (loanResultMode.value === "rate") return loanRateValue(a) - loanRateValue(b);
    if (loanResultMode.value === "payment") return estimateLoanPayment(a) - estimateLoanPayment(b);
    return loanRecommendationScore(b) - loanRecommendationScore(a);
  });
});

const loanSummary = computed(() => {
  const list = visibleLoanItems.value;
  const top = list[0];
  const rates = list.map(loanRateValue).filter(Boolean);
  return {
    count: list.length,
    bestRate: rates.length ? Math.min(...rates) : 0,
    monthlyPayment: top ? estimateLoanPayment(top) : 0,
    selectedCondition: `대출 · ${activeLoanType.value.label}`
  };
});

const visibleSavingsItems = computed(() => {
  const filtered = savingsItems.value.filter(item => {
    if (savingsForm.productType !== "all" && normalizeSavingsType(item) !== savingsForm.productType) return false;
    return true;
  });

  return [...filtered].sort((a, b) => {
    if (savingsResultMode.value === "rate") return savingsRateValue(b) - savingsRateValue(a);
    if (savingsResultMode.value === "maturity") return estimateSavingsMaturity(b) - estimateSavingsMaturity(a);
    if (savingsResultMode.value === "easy") return savingsEaseScore(b) - savingsEaseScore(a);
    return savingsRecommendationScore(b) - savingsRecommendationScore(a);
  });
});

const savingsSummary = computed(() => {
  const list = visibleSavingsItems.value;
  const top = list[0];
  const rates = list.map(savingsRateValue).filter(Boolean);
  return {
    count: list.length,
    averageRate: rates.length ? rates.reduce((total, rate) => total + rate, 0) / rates.length : 0,
    topMaturity: top ? estimateSavingsMaturity(top) : 0,
    selectedCondition: `저축 · ${activeSavingsType.value.label}`
  };
});

const topDepositItems = computed(() => visibleItems.value.slice(0, 5));
const topLoanItems = computed(() => visibleLoanItems.value.slice(0, 5));
const topSavingsItems = computed(() => visibleSavingsItems.value.slice(0, 5));

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

function loanRateValue(loan) {
  return Number(loan.rate_min || loan.rate_avg || loan.rate_max || 0);
}

function loanLimitScore(loan) {
  const text = `${loan.loan_limit || ""} ${loan.name || ""}`;
  const numbers = text.match(/\d+(?:\.\d+)?/g)?.map(Number) || [];
  const largest = numbers.length ? Math.max(...numbers) : 1;
  if (text.includes("억")) return largest * 10000;
  return largest;
}

function estimateLoanPayment(loan) {
  const principal = Number(loanForm.desiredAmount || 0);
  const years = Number(loanForm.loanTerm || 1);
  const months = Math.max(12, years * 12);
  const monthlyRate = loanRateValue(loan) / 100 / 12;
  if (!monthlyRate) return Math.round(principal / months);
  const payment = principal * monthlyRate * ((1 + monthlyRate) ** months) / (((1 + monthlyRate) ** months) - 1);
  return Math.round(payment || 0);
}

function estimateLoanInterest(loan) {
  const months = Math.max(12, Number(loanForm.loanTerm || 1) * 12);
  return Math.max(0, estimateLoanPayment(loan) * months - Number(loanForm.desiredAmount || 0));
}

function loanConditionText(loan) {
  return `${loan.name || ""} ${loan.bank_name || ""} ${loan.loan_type_label || ""} ${loan.loan_product_type || ""} ${loan.repay_type || ""} ${loan.join_member || ""} ${loan.loan_inci_expn || ""}`;
}

function loanRecommendationScore(loan) {
  const text = loanConditionText(loan);
  let score = 88;
  const rate = loanRateValue(loan);
  score += Math.max(0, 16 - rate * 2);
  if (loan.loan_type === loanForm.loanType) score += 14;
  if (loanForm.strategy === "rate") score += Math.max(0, 10 - rate);
  if (loanForm.strategy === "limit") score += Math.min(12, loanLimitScore(loan) / 5000);
  if (loanForm.strategy === "payment") score += Math.max(0, 12 - estimateLoanPayment(loan) / 200000);
  if (loanForm.strategy === "fixed" && (text.includes("고정") || text.includes("혼합"))) score += 9;
  if (loanForm.repayType && text.includes(loanForm.repayType.replace("상환", ""))) score += 5;
  if (loanForm.audience === "newlywed" && loan.loan_type !== "credit") score += 6;
  if (loanForm.audience === "starter" && rate <= 4.5) score += 5;
  if (loanForm.audience === "business" && text.includes("사업")) score += 8;
  if (loanForm.tags.some(tag => text.includes(tag))) score += 4;
  return Math.max(0, Math.min(100, Math.round(score)));
}

function loanReasonTags(loan) {
  const tags = [
    `금리 최저 ${loanRateValue(loan).toFixed(2)}%`,
    `대출 기간 ${Math.max(1, loanForm.loanTerm - 20)}년 ~ ${loanForm.loanTerm + 10}년`,
    loan.repay_type || loanForm.repayType
  ];
  if (loan.loan_limit) tags.unshift(`최대 한도 ${loan.loan_limit}`);
  return tags.filter(Boolean).slice(0, 4);
}

function savingsRateValue(item) {
  return Number(item.rate_value || item.best_rate || item.rate || 0);
}

function normalizeSavingsType(item) {
  const text = `${item.product_subtype || ""} ${item.product_type_label || ""} ${item.name || ""}`;
  if (text.includes("자유")) return "free";
  if (text.includes("정기") || text.includes("정액") || text.includes("매월")) return "regular";
  if (text.includes("목돈") || text.includes("목표")) return "goal";
  return "free";
}

function savingsTypeLabel(item) {
  const normalized = normalizeSavingsType(item);
  return savingsProductTypes.find(type => type.value === normalized)?.label || item.product_type_label || "저축";
}

function savingsConditionText(item) {
  return `${item.name || ""} ${item.bank_name || ""} ${item.product_subtype || ""} ${item.join_way || ""} ${item.join_member || ""} ${item.special_condition || ""} ${item.etc_note || ""}`;
}

function savingsEaseScore(item) {
  const text = savingsConditionText(item);
  let score = 58;
  if (text.includes("자유")) score += 14;
  if (text.includes("자동이체")) score += 8;
  if (text.includes("비대면") || text.includes("인터넷") || text.includes("스마트")) score += 8;
  if (!text.includes("급여") && !text.includes("카드") && !text.includes("실적")) score += 6;
  return Math.min(score, 100);
}

function savingsRecommendationScore(item) {
  const text = savingsConditionText(item);
  const rate = savingsRateValue(item);
  let score = 70 + Math.min(18, rate * 4);

  if (savingsForm.productType !== "all" && normalizeSavingsType(item) === savingsForm.productType) score += 10;
  if (savingsForm.strategy === "rate") score += Math.min(10, rate * 2);
  if (savingsForm.strategy === "flexible" && text.includes("자유")) score += 11;
  if (savingsForm.strategy === "target") score += Math.max(0, 12 - Math.abs(savingsForm.periodMonths - 12) / 2);
  if (savingsForm.strategy === "stable") score += Math.round(savingsEaseScore(item) / 12);
  if (savingsForm.audience === "youth" && (text.includes("청년") || text.includes("첫"))) score += 8;
  if (savingsForm.audience === "couple" && savingsForm.purpose.includes("목돈")) score += 5;
  if (savingsForm.tags.some(tag => text.includes(tag.replace(" 가능", "")))) score += 4;

  return Math.max(0, Math.min(100, Math.round(score)));
}

function estimateSavingsMaturity(item) {
  const months = Number(savingsForm.periodMonths || 12);
  const annualRate = savingsRateValue(item) / 100;
  const principal = Number(savingsForm.monthlyAmount || 0) * months;
  const interest = Number(savingsForm.monthlyAmount || 0) * annualRate * ((months + 1) / 2);
  return principal + interest * 0.846;
}

function estimateSavingsInterest(item) {
  const principal = Number(savingsForm.monthlyAmount || 0) * Number(savingsForm.periodMonths || 12);
  return Math.max(0, estimateSavingsMaturity(item) - principal);
}

function savingsReasonTags(item) {
  const tags = [
    `최고 ${savingsRateValue(item).toFixed(2)}%`,
    `${savingsForm.periodMonths}개월`,
    savingsTypeLabel(item),
    item.join_way || "가입방법 확인"
  ];
  if (item.special_condition) tags.push("우대조건 확인");
  return tags.filter(Boolean).slice(0, 4);
}

function getAiExplanation(type, id) {
  return aiExplanations[type]?.[String(id)] || null;
}

function clearAiExplanations(type) {
  aiExplanations[type] = {};
  aiExplanationMeta[type] = { usedAi: false, model: null };
}

function localAiFallback(type, list) {
  const isLoan = type === "loan";
  const isSavings = type === "savings";
  return list.map(item => {
    const id = isLoan || isSavings ? item.product_code : item.product.id;
    return {
      id: String(id),
      ai_reason: isLoan
        ? "선택한 조건에서 금리와 월 예상 상환액 기준으로 비교 상위에 있어 추천합니다."
        : isSavings
          ? "선택한 저축 조건에서 수익률, 납입 방식, 예상 만기 금액을 비교했을 때 적합해 추천합니다."
          : "선택한 조건에서 금리와 예상 수령액이 비교적 우수해 추천합니다.",
      ai_summary_tags: isLoan
        ? ["상환 부담 비교", "금리 기준", "조건 적합"]
        : isSavings
          ? ["목돈 마련 적합", "저축 조건 비교", "조건 적합"]
          : ["금리 우수", "예상 수령액", "조건 적합"],
      caution: ""
    };
  });
}

function buildDepositAiPayload() {
  return {
    recommendation_type: "deposit",
    user_conditions: {
      target: activeAudience.value.label,
      product_type: productTypes.find(type => type.value === form.productType)?.label || "전체",
      monthly_amount: form.monthlySaving,
      deposit_amount: form.depositAmount,
      period_months: form.preferredTerm,
      saving_goal: form.purpose,
      risk_preference: form.riskTolerance
    },
    recommendations: topDepositItems.value.map(item => ({
      id: String(item.product.id),
      name: item.product.name,
      bank_name: item.product.bank_name,
      product_type: productTypeLabel(item.product.product_type),
      rate: Number(item.option.intr_rate2 || 0),
      period: Number(item.option.save_term || 0),
      expected_amount: Math.round(estimateMaturity(item)),
      score: recommendationScore(item),
      conditions: item.reasons.slice(0, 3)
    }))
  };
}

function buildLoanAiPayload() {
  return {
    recommendation_type: "loan",
    user_conditions: {
      target: activeLoanAudience.value.label,
      loan_type: activeLoanType.value.label,
      loan_amount: loanForm.desiredAmount,
      loan_period_years: loanForm.loanTerm,
      repayment_type: loanForm.repayType,
      income_range: loanForm.incomeRange,
      credit_grade: creditGrades.find(grade => grade.value === loanForm.creditGrade)?.label || loanForm.creditGrade,
      priority: loanStrategies.find(strategy => strategy.value === loanForm.strategy)?.label || loanForm.strategy,
      tags: loanForm.tags
    },
    recommendations: topLoanItems.value.map(loan => ({
      id: String(loan.product_code),
      name: loan.name,
      bank_name: loan.bank_name,
      loan_type: loan.loan_type_label,
      min_rate: loanRateValue(loan),
      max_limit: loan.loan_limit || "",
      monthly_payment: estimateLoanPayment(loan),
      score: loanRecommendationScore(loan),
      repayment_type: loan.repay_type || loanForm.repayType
    }))
  };
}

function buildSavingsAiPayload() {
  return {
    recommendation_type: "saving",
    user_conditions: {
      target: activeSavingsAudience.value.label,
      saving_product_type: activeSavingsType.value.label,
      monthly_amount: savingsForm.monthlyAmount,
      target_amount: savingsForm.targetAmount,
      period_months: savingsForm.periodMonths,
      saving_goal: savingsForm.purpose,
      preference: savingsPreferences.find(item => item.value === savingsForm.preference)?.label || savingsForm.preference,
      extra_conditions: savingsForm.tags
    },
    recommendations: topSavingsItems.value.map(item => ({
      id: String(item.product_code),
      name: item.name,
      bank_name: item.bank_name,
      product_type: savingsTypeLabel(item),
      rate: savingsRateValue(item),
      period: savingsForm.periodMonths,
      expected_amount: Math.round(estimateSavingsMaturity(item)),
      expected_interest: Math.round(estimateSavingsInterest(item)),
      score: savingsRecommendationScore(item),
      conditions: savingsReasonTags(item)
    }))
  };
}

async function loadAiExplanations(type) {
  const currentList = type === "loan" ? topLoanItems.value : type === "savings" ? topSavingsItems.value : topDepositItems.value;
  if (!currentList.length) return;

  aiExplanationLoading.value = true;
  aiExplanationError.value = "";
  clearAiExplanations(type);
  try {
    const payload = type === "loan" ? buildLoanAiPayload() : type === "savings" ? buildSavingsAiPayload() : buildDepositAiPayload();
    const data = await apiFetch("/recommendations/ai-explain/", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    aiExplanationMeta[type] = { usedAi: Boolean(data.used_ai), model: data.model || null };
    const mapped = {};
    (data.items || []).forEach(item => {
      mapped[String(item.id)] = item;
    });
    aiExplanations[type] = mapped;
  } catch (err) {
    aiExplanationError.value = "AI 추천 이유를 불러오지 못해 기본 설명을 표시합니다.";
    const fallback = {};
    localAiFallback(type, currentList).forEach(item => {
      fallback[String(item.id)] = item;
    });
    aiExplanations[type] = fallback;
  } finally {
    aiExplanationLoading.value = false;
  }
}

function formatLoanAmount(value) {
  const amount = Number(value || 0);
  if (amount >= 100000000) {
    const eok = amount / 100000000;
    return `${Number.isInteger(eok) ? eok : eok.toFixed(1)}억원`;
  }
  if (amount >= 10000) return `${Math.round(amount / 10000).toLocaleString("ko-KR")}만원`;
  return formatMoney(amount);
}

function changeLoanValue(field, amount, minimum) {
  loanForm[field] = Math.max(minimum, Number(loanForm[field] || 0) + amount);
}

function toggleLoanTag(tag) {
  if (loanForm.tags.includes(tag)) {
    loanForm.tags = loanForm.tags.filter(item => item !== tag);
  } else {
    loanForm.tags.push(tag);
  }
}

function changeSavingsValue(field, amount, minimum) {
  savingsForm[field] = Math.max(minimum, Number(savingsForm[field] || 0) + amount);
}

function toggleSavingsTag(tag) {
  if (savingsForm.tags.includes(tag)) {
    savingsForm.tags = savingsForm.tags.filter(item => item !== tag);
  } else {
    savingsForm.tags.push(tag);
  }
}

async function loadLoanRecommendations() {
  loanError.value = "";
  try {
    const data = await apiFetch("/loans/?type=all");
    loanItems.value = data.results || [];
  } catch (err) {
    loanError.value = err.message || "대출 추천 데이터를 불러오지 못했습니다.";
  }
}

async function loadSavingsRecommendations() {
  savingsError.value = "";
  try {
    const data = await apiFetch("/savings/");
    savingsItems.value = data.results || data || [];
  } catch (err) {
    savingsError.value = err.message || "저축 추천 데이터를 불러오지 못했습니다.";
  }
}

async function applyLoanDiagnosis() {
  saving.value = true;
  loanError.value = "";
  try {
    if (!loanItems.value.length) await loadLoanRecommendations();
    await loadAiExplanations("loan");
  } finally {
    saving.value = false;
  }
}

async function applySavingsDiagnosis() {
  saving.value = true;
  savingsError.value = "";
  try {
    if (!savingsItems.value.length) await loadSavingsRecommendations();
    await loadAiExplanations("savings");
  } finally {
    saving.value = false;
  }
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
    await loadAiExplanations("deposit");
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
  await loadLoanRecommendations();
  await loadSavingsRecommendations();
  loadAiExplanations("deposit");
});
</script>

<template>
  <main class="recommend-page-local">
    <section class="container recommend-container-local">
      <div class="section-head recommend-head-local">
        <div>
          <!-- <p class="eyebrow">FinPick recommendation</p> -->
          <h1>금융상품 추천</h1>
          <p>금리, 한도, 상환 부담을 기준으로 내 조건에 맞는 금융상품을 비교합니다.</p>
        </div>
        <div class="head-actions-local">
          <RouterLink class="btn primary" to="/recommend-profile">나의 정보 입력하기</RouterLink>
          <RouterLink class="btn ghost" to="/products">전체 상품 보기</RouterLink>
          <RouterLink class="btn plain" to="/dashboard">나의 대시보드 보기</RouterLink>
        </div>
      </div>

      <StatusBlock :loading="loading" :error="error" />

      <div class="service-tabs-local" role="tablist" aria-label="추천 서비스 선택">
        <button type="button" :class="{ active: activeRecommendationType === 'deposit' }" @click="activeRecommendationType = 'deposit'">
          <span aria-hidden="true">▥</span> 예적금 추천 서비스
        </button>
        <button type="button" :class="{ active: activeRecommendationType === 'loan' }" @click="activeRecommendationType = 'loan'">
          <span aria-hidden="true">⌂</span> 대출 추천 서비스
        </button>
        <button type="button" :class="{ active: activeRecommendationType === 'savings' }" @click="activeRecommendationType = 'savings'">
          <span aria-hidden="true">◇</span> 저축 추천 서비스
        </button>
      </div>

      <section class="service-panel-local">
        <div class="service-copy-local">
          <span>선택한 추천 서비스</span>
          <h2>{{ activeRecommendationType === "deposit" ? activeAudience.title : activeRecommendationType === "loan" ? activeLoanAudience.title : activeSavingsAudience.title }}</h2>
          <p>{{ activeRecommendationType === "deposit" ? activeAudience.description : activeRecommendationType === "loan" ? activeLoanAudience.description : activeSavingsAudience.description }}</p>
        </div>
        <div v-if="activeRecommendationType === 'deposit'" class="service-summary-local">
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">↗</span>
              <span>평균 최고금리</span>
            </div>
            <strong>{{ summary.averageRate.toFixed(2) }}%</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">₩</span>
              <span>1위 예상 수령액</span>
            </div>
            <strong>{{ formatMoney(summary.topMaturity) }}</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">⌘</span>
              <span>선택 조건</span>
            </div>
            <strong>{{ activeAudience.label }} · {{ productTypes.find(type => type.value === form.productType)?.label }}</strong>
          </article>
        </div>
        <div v-else-if="activeRecommendationType === 'loan'" class="service-summary-local">
          <!-- <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">♙</span>
              <span>추천 대상</span>
            </div>
            <strong>{{ loanSummary.count }}개</strong>
          </article> -->
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">%</span>
              <span>최저 금리</span>
            </div>
            <strong>{{ loanSummary.bestRate.toFixed(2) }}%</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">₩</span>
              <span>월 예상 상환액</span>
            </div>
            <strong>{{ formatMoney(loanSummary.monthlyPayment) }}</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">⌘</span>
              <span>선택 조건</span>
            </div>
            <strong>{{ loanSummary.selectedCondition }}</strong>
          </article>
        </div>
        <div v-else class="service-summary-local">
           <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">%</span>
              <span>평균 수익률</span>
            </div>
            <strong>{{ savingsSummary.averageRate.toFixed(2) }}%</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">₩</span>
              <span>예상 만기 금액</span>
            </div>
            <strong>{{ formatMoney(savingsSummary.topMaturity) }}</strong>
          </article>
          <article>
            <div class="summary-label-local">
              <span class="summary-icon-local" aria-hidden="true">⌘</span>
              <span>선택 조건</span>
            </div>
            <strong>{{ savingsSummary.selectedCondition }}</strong>
          </article>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="section-head">
          <h2>추천 조건</h2>
          <p>서비스 대상, 상품 유형, 저축 조건을 바꾸면 아래 추천 결과가 함께 바뀝니다.</p>
        </div>

        <div class="workspace-local">
          <article v-if="activeRecommendationType === 'deposit'" class="content-panel filter-panel-local">
            <div class="condition-control-grid-local">
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
            </div>

            <div class="input-grid-local">
              <article class="step-box-local">
                <span class="field-label-local">{{ form.productType === "deposit" ? "예치 가능 금액" : "월 저축 가능 금액" }}</span>
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
                <span class="field-label-local">{{ form.direction === "target" ? "목표 금액" : "희망 기간" }}</span>
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

              <!-- <label class="select-field-local"> -->
                <!-- <span class="field-label-local">저축 목적</span> -->
                <!-- <select v-model="form.purpose"> -->
                  <!-- <option v-for="purpose in purposes" :key="purpose" :value="purpose">{{ purpose }}</option> -->
                <!-- </select> -->
              <!-- </label> -->

              <!-- <label class="select-field-local"> -->
                <!-- <span class="field-label-local">추천 성향</span> -->
                <!-- <select v-model="form.riskTolerance"> -->
                  <!-- <option value="stable">안정형</option> -->
                  <!-- <option value="balanced">균형형</option> -->
                  <!-- <option value="aggressive">고금리형</option> -->
                <!-- </select> -->
              <!-- </label> -->
            </div>

            <div class="quick-choice-local">
              <span>저축 목적
              </span>
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
            </div>

            <button class="btn primary full" type="button" :disabled="saving" @click="applyDiagnosis">
              <span aria-hidden="true">✦</span>
              {{ saving ? "조건 반영 중" : "내 조건으로 추천 보기" }}
            </button>
          </article>

          <article v-else-if="activeRecommendationType === 'loan'" class="content-panel filter-panel-local">
            <div class="condition-control-grid-local">
              <div class="control-group-local">
                <h3>추천 서비스</h3>
                <div class="segment-grid-local audience">
                  <button
                    v-for="audience in loanAudiences"
                    :key="audience.value"
                    type="button"
                    :class="{ active: loanForm.audience === audience.value }"
                    @click="loanForm.audience = audience.value"
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
                    v-for="type in loanProductTypes"
                    :key="type.value"
                    type="button"
                    :class="{ active: loanForm.loanType === type.value }"
                    @click="loanForm.loanType = type.value"
                  >
                    <span>{{ type.label }}</span>
                    <small>{{ type.description }}</small>
                  </button>
                </div>
              </div>

              <div class="control-group-local">
                <h3>계산 방식</h3>
                <div class="segment-grid-local two loan-strategy-grid-local">
                  <button
                    v-for="strategy in loanStrategies"
                    :key="strategy.value"
                    type="button"
                    :class="{ active: loanForm.strategy === strategy.value }"
                    @click="loanForm.strategy = strategy.value"
                  >
                    <span>{{ strategy.label }}</span>
                    <small>{{ strategy.description }}</small>
                  </button>
                </div>
              </div>
            </div>

            <div class="input-grid-local loan-input-grid-local">
              <article class="step-box-local">
                <span class="field-label-local">희망 대출 금액</span>
                <div>
                  <button type="button" @click="changeLoanValue('desiredAmount', -10000000, 10000000)">-</button>
                  <strong>{{ formatLoanAmount(loanForm.desiredAmount) }}</strong>
                  <button type="button" @click="changeLoanValue('desiredAmount', 10000000, 10000000)">+</button>
                </div>
              </article>

              <article class="step-box-local">
                <span class="field-label-local">대출 기간</span>
                <div>
                  <button type="button" @click="changeLoanValue('loanTerm', -1, 1)">-</button>
                  <strong>{{ loanForm.loanTerm }}년</strong>
                  <button type="button" @click="changeLoanValue('loanTerm', 1, 1)">+</button>
                </div>
              </article>

              <label class="select-field-local">
                <span class="field-label-local">상환 방식</span>
                <select v-model="loanForm.repayType">
                  <option v-for="type in repayTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </label>

              <label class="select-field-local">
                <span class="field-label-local">소득 구간</span>
                <select v-model="loanForm.incomeRange">
                  <option v-for="range in incomeRanges" :key="range" :value="range">{{ range }}</option>
                </select>
              </label>

              <label class="select-field-local">
                <span class="field-label-local">신용도</span>
                <select v-model="loanForm.creditGrade">
                  <option v-for="grade in creditGrades" :key="grade.value" :value="grade.value">{{ grade.label }}</option>
                </select>
              </label>
            </div>

            <div class="quick-choice-local">
              <span>추가 조건</span>
              <div class="purpose-row-local">
                <button
                  v-for="tag in loanTags"
                  :key="tag"
                  type="button"
                  :class="{ active: loanForm.tags.includes(tag) }"
                  @click="toggleLoanTag(tag)"
                >
                  ✓ {{ tag }}
                </button>
              </div>
            </div>

            <button class="btn primary full" type="button" :disabled="saving" @click="applyLoanDiagnosis">
              <span aria-hidden="true">✦</span>
              {{ saving ? "조건 반영 중" : "내 조건으로 추천 보기" }}
            </button>
          </article>

          <article v-else class="content-panel filter-panel-local">
            <div class="condition-control-grid-local">
              <div class="control-group-local">
                <h3>추천 서비스</h3>
                <div class="segment-grid-local audience">
                  <button
                    v-for="audience in savingsAudiences"
                    :key="audience.value"
                    type="button"
                    :class="{ active: savingsForm.audience === audience.value }"
                    @click="savingsForm.audience = audience.value"
                  >
                    <span>{{ audience.label }}</span>
                    <small>{{ audience.count }}개</small>
                  </button>
                </div>
              </div>

              <div class="control-group-local">
                <h3>상품 유형</h3>
                <div class="segment-grid-local three savings-type-grid-local">
                  <button
                    v-for="type in savingsProductTypes"
                    :key="type.value"
                    type="button"
                    :class="{ active: savingsForm.productType === type.value }"
                    @click="savingsForm.productType = type.value"
                  >
                    <span>{{ type.label }}</span>
                    <small>{{ type.description }}</small>
                  </button>
                </div>
              </div>

              <div class="control-group-local">
                <h3>계산 방식</h3>
                <div class="segment-grid-local two loan-strategy-grid-local">
                  <button
                    v-for="strategy in savingsStrategies"
                    :key="strategy.value"
                    type="button"
                    :class="{ active: savingsForm.strategy === strategy.value }"
                    @click="savingsForm.strategy = strategy.value"
                  >
                    <span>{{ strategy.label }}</span>
                    <small>{{ strategy.description }}</small>
                  </button>
                </div>
              </div>
            </div>

            <div class="input-grid-local loan-input-grid-local">
              <article class="step-box-local">
                <span class="field-label-local">월 저축 가능 금액</span>
                <div>
                  <button type="button" @click="changeSavingsValue('monthlyAmount', -100000, 0)">-</button>
                  <strong>{{ formatShortMoney(savingsForm.monthlyAmount) }}</strong>
                  <button type="button" @click="changeSavingsValue('monthlyAmount', 100000, 0)">+</button>
                </div>
              </article>

              <article class="step-box-local">
                <span class="field-label-local">목표 금액</span>
                <div>
                  <button type="button" @click="changeSavingsValue('targetAmount', -1000000, 1000000)">-</button>
                  <strong>{{ formatShortMoney(savingsForm.targetAmount) }}</strong>
                  <button type="button" @click="changeSavingsValue('targetAmount', 1000000, 1000000)">+</button>
                </div>
              </article>

              <article class="step-box-local">
                <span class="field-label-local">희망 기간</span>
                <div>
                  <button type="button" @click="changeSavingsValue('periodMonths', -6, 6)">-</button>
                  <strong>{{ savingsForm.periodMonths }}개월</strong>
                  <button type="button" @click="changeSavingsValue('periodMonths', 6, 6)">+</button>
                </div>
              </article>

              <label class="select-field-local">
                <span class="field-label-local">저축 목적</span>
                <select v-model="savingsForm.purpose">
                  <option v-for="purpose in savingsPurposes" :key="purpose" :value="purpose">{{ purpose }}</option>
                </select>
              </label>

              <label class="select-field-local">
                <span class="field-label-local">추천 성향</span>
                <select v-model="savingsForm.preference">
                  <option v-for="preference in savingsPreferences" :key="preference.value" :value="preference.value">{{ preference.label }}</option>
                </select>
              </label>
            </div>

            <div class="quick-choice-local">
              <span>추가 조건</span>
              <div class="purpose-row-local">
                <button
                  v-for="tag in savingsTags"
                  :key="tag"
                  type="button"
                  :class="{ active: savingsForm.tags.includes(tag) }"
                  @click="toggleSavingsTag(tag)"
                >
                  ✓ {{ tag }}
                </button>
              </div>
            </div>

            <button class="btn primary full" type="button" :disabled="saving" @click="applySavingsDiagnosis">
              <span aria-hidden="true">✦</span>
              {{ saving ? "조건 반영 중" : "내 조건으로 추천 보기" }}
            </button>
          </article>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="result-head-local">
          <div class="section-head">
            <h2>추천 결과 TOP 5</h2>
            <p>{{ activeRecommendationType === "deposit" ? "추천점수, 만기 수령액, 금리, 우대조건 쉬운순으로 비교할 수 있습니다." : activeRecommendationType === "loan" ? "추천점수, 한도, 금리, 월상환액 기준으로 비교할 수 있습니다." : "추천점수, 수익률, 만기금액, 조건 쉬운순으로 비교할 수 있습니다." }}</p>
          </div>
          <div v-if="activeRecommendationType === 'deposit'" class="sort-tabs-local">
            <button type="button" :class="{ active: resultMode === 'score' }" @click="resultMode = 'score'">추천순</button>
            <button type="button" :class="{ active: resultMode === 'maturity' }" @click="resultMode = 'maturity'">수령액순</button>
            <button type="button" :class="{ active: resultMode === 'rate' }" @click="resultMode = 'rate'">금리순</button>
            <button type="button" :class="{ active: resultMode === 'easy' }" @click="resultMode = 'easy'">조건 쉬운순</button>
          </div>
          <div v-else-if="activeRecommendationType === 'loan'" class="sort-tabs-local">
            <button type="button" :class="{ active: loanResultMode === 'score' }" @click="loanResultMode = 'score'">추천순</button>
            <button type="button" :class="{ active: loanResultMode === 'limit' }" @click="loanResultMode = 'limit'">한도순</button>
            <button type="button" :class="{ active: loanResultMode === 'rate' }" @click="loanResultMode = 'rate'">금리순</button>
            <button type="button" :class="{ active: loanResultMode === 'payment' }" @click="loanResultMode = 'payment'">월상환액순</button>
          </div>
          <div v-else class="sort-tabs-local">
            <button type="button" :class="{ active: savingsResultMode === 'score' }" @click="savingsResultMode = 'score'">추천순</button>
            <button type="button" :class="{ active: savingsResultMode === 'maturity' }" @click="savingsResultMode = 'maturity'">만기금액순</button>
            <button type="button" :class="{ active: savingsResultMode === 'rate' }" @click="savingsResultMode = 'rate'">금리순</button>
            <button type="button" :class="{ active: savingsResultMode === 'easy' }" @click="savingsResultMode = 'easy'">조건 쉬운순</button>
          </div>
        </div>

        <div v-if="activeRecommendationType === 'deposit' && !loading && !visibleItems.length" class="status-block">조건에 맞는 상품이 없습니다.</div>
        <div v-if="activeRecommendationType === 'loan' && loanError" class="status-block warning">{{ loanError }}</div>
        <div v-else-if="activeRecommendationType === 'loan' && !visibleLoanItems.length" class="status-block">조건에 맞는 대출 상품이 없습니다. 조건을 완화하거나 다른 대출 유형을 선택해보세요.</div>
        <div v-if="activeRecommendationType === 'savings' && savingsError" class="status-block warning">{{ savingsError }}</div>
        <div v-else-if="activeRecommendationType === 'savings' && !visibleSavingsItems.length" class="status-block">조건에 맞는 저축 상품이 없습니다. 조건을 완화하거나 다른 저축 유형을 선택해보세요.</div>

        <div v-if="activeRecommendationType === 'deposit'" class="result-list-local">
          <RouterLink
            v-for="(item, index) in topDepositItems"
            :key="`${item.product.id}-${item.option.id}`"
            class="result-card-local"
            :class="{ featured: index === 0 }"
            :to="`/products/${item.product.id}`"
          >
            <span class="rank-local">{{ index + 1 }}</span>
            <div class="product-main-local">
              <div class="product-heading-local">
                <span class="product-bank-local">{{ item.product.bank_name }}</span>
                <span class="product-type-local">{{ productTypeLabel(item.product.product_type) }}</span>
              </div>
              <h3>{{ item.product.name }}</h3>
              <p class="product-meta-local">
                <span>{{ item.option.save_term }}개월</span>
                <span>최고 {{ item.option.intr_rate2.toFixed(2) }}%</span>
                <span>추천점수 {{ recommendationScore(item) }}점</span>
              </p>
              <div>
                <em v-for="reason in item.reasons.slice(0, 2)" :key="reason">{{ reason }}</em>
              </div>
              <section class="ai-reason-local">
                <span>AI 추천 이유</span>
                <p v-if="aiExplanationLoading && !getAiExplanation('deposit', item.product.id)">AI가 추천 이유를 분석하고 있습니다...</p>
                <p v-else>{{ getAiExplanation('deposit', item.product.id)?.ai_reason || "선택한 조건에서 금리와 예상 수령액이 비교적 우수해 추천합니다." }}</p>
                <div v-if="getAiExplanation('deposit', item.product.id)?.ai_summary_tags?.length" class="ai-tags-local">
                  <small v-for="tag in getAiExplanation('deposit', item.product.id).ai_summary_tags" :key="tag">{{ tag }}</small>
                </div>
                <small v-if="getAiExplanation('deposit', item.product.id)?.caution" class="ai-caution-local">{{ getAiExplanation('deposit', item.product.id).caution }}</small>
              </section>
            </div>
            <div class="result-money-local">
              <span>세후 예상 수령액</span>
              <strong>{{ formatMoney(estimateMaturity(item)) }}</strong>
              <small>예상 이자 + {{ formatMoney(estimateInterest(item)) }}</small>
            </div>
          </RouterLink>
        </div>

        <div v-else-if="activeRecommendationType === 'loan'" class="result-list-local">
          <RouterLink
            v-for="(loan, index) in topLoanItems"
            :key="`${loan.loan_type}-${loan.product_code}`"
            class="result-card-local loan-result-card-local"
            :class="{ featured: index === 0 }"
            :to="{ name: 'loan-detail', params: { type: loan.loan_type, code: loan.product_code } }"
          >
            <span class="rank-local">{{ index + 1 }}</span>
            <div class="product-main-local">
              <div class="product-heading-local">
                <span class="product-bank-local">{{ loan.bank_name }}</span>
                <span class="product-type-local">{{ loan.loan_type_label }}</span>
              </div>
              <h3>{{ loan.name }}</h3>
              <p class="product-meta-local">
                <span>금리 최저 {{ loanRateValue(loan).toFixed(2) }}%</span>
                <span>추천점수 {{ loanRecommendationScore(loan) }}점</span>
                <span>대출 기간 {{ Math.max(1, loanForm.loanTerm - 20) }}년 ~ {{ loanForm.loanTerm + 10 }}년</span>
              </p>
              <div>
                <em v-for="reason in loanReasonTags(loan)" :key="reason">{{ reason }}</em>
              </div>
              <section class="ai-reason-local">
                <span>AI 추천 이유</span>
                <p v-if="aiExplanationLoading && !getAiExplanation('loan', loan.product_code)">AI가 추천 이유를 분석하고 있습니다...</p>
                <p v-else>{{ getAiExplanation('loan', loan.product_code)?.ai_reason || "선택한 조건에서 금리와 월 예상 상환액 기준으로 비교 상위에 있어 추천합니다." }}</p>
                <div v-if="getAiExplanation('loan', loan.product_code)?.ai_summary_tags?.length" class="ai-tags-local">
                  <small v-for="tag in getAiExplanation('loan', loan.product_code).ai_summary_tags" :key="tag">{{ tag }}</small>
                </div>
                <small v-if="getAiExplanation('loan', loan.product_code)?.caution" class="ai-caution-local">{{ getAiExplanation('loan', loan.product_code).caution }}</small>
              </section>
            </div>
            <div class="result-money-local">
              <span>월 예상 상환액</span>
              <strong>{{ formatMoney(estimateLoanPayment(loan)) }}</strong>
              <small>총 이자 약 {{ formatLoanAmount(estimateLoanInterest(loan)) }}</small>
            </div>
          </RouterLink>
        </div>

        <div v-else class="result-list-local">
          <RouterLink
            v-for="(item, index) in topSavingsItems"
            :key="item.product_code"
            class="result-card-local savings-result-card-local"
            :class="{ featured: index === 0 }"
            :to="{ name: 'savings-detail', params: { code: item.product_code } }"
          >
            <span class="rank-local">{{ index + 1 }}</span>
            <div class="product-main-local">
              <div class="product-heading-local">
                <span class="product-bank-local">{{ item.bank_name }}</span>
                <span class="product-type-local">{{ savingsTypeLabel(item) }}</span>
              </div>
              <h3>{{ item.name }}</h3>
              <p class="product-meta-local">
                <span>최고 {{ savingsRateValue(item).toFixed(2) }}%</span>
                <span>추천점수 {{ savingsRecommendationScore(item) }}점</span>
                <span>{{ savingsForm.periodMonths }}개월</span>
              </p>
              <div>
                <em v-for="reason in savingsReasonTags(item)" :key="reason">{{ reason }}</em>
              </div>
              <section class="ai-reason-local">
                <span>AI 추천 이유</span>
                <p v-if="aiExplanationLoading && !getAiExplanation('savings', item.product_code)">AI가 추천 이유를 분석하고 있습니다...</p>
                <p v-else>{{ getAiExplanation('savings', item.product_code)?.ai_reason || "선택한 저축 조건에서 수익률과 예상 만기 금액 기준으로 비교 상위에 있어 추천합니다." }}</p>
                <div v-if="getAiExplanation('savings', item.product_code)?.ai_summary_tags?.length" class="ai-tags-local">
                  <small v-for="tag in getAiExplanation('savings', item.product_code).ai_summary_tags" :key="tag">{{ tag }}</small>
                </div>
                <small v-if="getAiExplanation('savings', item.product_code)?.caution" class="ai-caution-local">{{ getAiExplanation('savings', item.product_code).caution }}</small>
              </section>
            </div>
            <div class="result-money-local">
              <span>예상 만기 금액</span>
              <strong>{{ formatMoney(estimateSavingsMaturity(item)) }}</strong>
              <small>예상 이자 + {{ formatMoney(estimateSavingsInterest(item)) }}</small>
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
  font-size: 2rem;
}

.head-actions-local,
.sort-tabs-local,
.purpose-row-local {
  display: flex;
  align-items: center;
  gap: .6rem;
  flex-wrap: wrap;
}

.service-tabs-local {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .25rem;
  margin: 1rem 0;
  border: 1px solid #dbe6f3;
  border-radius: 12px;
  background: #edf2f8;
  padding: .25rem;
}

.service-tabs-local button {
  min-height: 48px;
  border: 1px solid transparent;
  border-radius: 9px;
  background: transparent;
  color: #526780;
  cursor: pointer;
  font-weight: 900;
}

.service-tabs-local button.active {
  border-color: #9fc1ff;
  background: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, .08);
  color: #196ae9;
}

.service-tabs-local span {
  margin-right: .35rem;
}

.service-panel-local {
  display: grid;
  grid-template-columns: minmax(260px, .8fr) minmax(0, 1.2fr);
  gap: 1rem;
  align-items: center;
  margin-top: 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(120deg, #f6f9ff, #edf8f6);
  box-shadow: 0 8px 24px rgba(23, 32, 51, .05);
  padding: 1.25rem;
}

.service-copy-local > span,
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
.service-copy-local p {
  margin: 0;
  color: var(--muted);
  line-height: 1.65;
}

.service-summary-local {
  display: grid;
  gap: .75rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.service-summary-local.loan-summary-local {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.service-summary-local article {
  border: 1px solid #d7e4f5;
  border-radius: 8px;
  background: rgba(255, 255, 255, .82);
  padding: .95rem;
}

.service-summary-local span,
.step-box-local > span,
.input-grid-local label > span,
.result-money-local span {
  display: block;
  color: var(--muted);
  font-size: .88rem;
  font-weight: 900;
}

.service-summary-local strong {
  display: block;
  margin-top: .35rem;
  color: var(--blue);
  font-size: clamp(1rem, 1.8vw, 1.35rem);
  overflow-wrap: anywhere;
}

.workspace-local {
  display: block;
}

.filter-panel-local,
.control-group-local {
  display: grid;
  gap: 1rem;
}

.control-group-local h3 {
  margin: 0;
  font-size: 1rem;
}

.condition-control-grid-local {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.condition-control-grid-local > :first-child {
  grid-column: 1 / -1;
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

.savings-type-grid-local {
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
  min-height: 64px;
  padding: .7rem .85rem;
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
  .result-card-local {
    grid-template-columns: 1fr;
  }

  .condition-control-grid-local {
    grid-template-columns: 1fr;
  }

  .condition-control-grid-local > :first-child {
    grid-column: auto;
  }

  .result-money-local {
    justify-items: start;
  }
}

@media (max-width: 720px) {
  .service-summary-local,
  .segment-grid-local.audience,
  .segment-grid-local.two,
  .segment-grid-local.three,
  .savings-type-grid-local,
  .input-grid-local {
    grid-template-columns: 1fr;
  }
}

/* Refined financial-service presentation */
.recommend-page-local {
  background:
    radial-gradient(circle at 100% 0, rgba(37, 99, 235, .08), transparent 28rem),
    linear-gradient(180deg, #f7faff 0, #f3f7fb 38rem, #f6f8fb 100%);
}

.recommend-container-local {
  max-width: 1280px;
  padding-top: 2.8rem;
  padding-bottom: 4rem;
}

.recommend-head-local {
  margin-bottom: 1.5rem;
}

.recommend-head-local h1,
.result-head-local h2 {
  color: #102a4b;
  letter-spacing: -.045em;
}

.head-actions-local .btn {
  min-height: 42px;
  border-radius: 10px;
  padding-inline: 1rem;
}

.service-panel-local {
  position: relative;
  grid-template-columns: minmax(300px, .82fr) minmax(0, 1.18fr);
  gap: 2rem;
  overflow: hidden;
  border: 1px solid #dce7f5;
  border-radius: 20px;
  background: linear-gradient(115deg, #ffffff 8%, #f7fbff 58%, #eff7ff 100%);
  box-shadow: 0 14px 34px rgba(19, 56, 97, .08);
  padding: 1.7rem 2rem;
}

.service-panel-local::before {
  position: absolute;
  top: -4.5rem;
  right: 31%;
  width: 12rem;
  height: 12rem;
  border-radius: 999px;
  background: rgba(20, 184, 166, .06);
  content: "";
  pointer-events: none;
}

.service-copy-local,
.service-summary-local {
  position: relative;
  z-index: 1;
}

.service-copy-local > span {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  color: #0f9f9b;
  font-size: .86rem;
  letter-spacing: -.01em;
}

.service-copy-local > span::before,
.control-group-local h3::before {
  display: inline-block;
  width: .5rem;
  height: .5rem;
  margin-right: .45rem;
  border-radius: 50%;
  background: #11b5ae;
  content: "";
}

.service-panel-local h2 {
  margin: .55rem 0 .6rem;
  color: #102a4b;
  font-size: clamp(1.7rem, 3vw, 2.45rem);
  font-weight: 850;
  line-height: 1.15;
}

.service-copy-local p {
  max-width: 33rem;
  color: #6b7d93;
  font-size: .98rem;
}

.service-summary-local {
  gap: .8rem;
}

.service-summary-local article {
  min-height: 112px;
  border: 1px solid #dbe7f5;
  border-radius: 15px;
  background: rgba(255, 255, 255, .92);
  box-shadow: 0 8px 20px rgba(34, 68, 110, .055);
  padding: 1rem 1.05rem;
}

.summary-label-local {
  display: flex;
  align-items: center;
  gap: .55rem;
  color: #50647f;
  font-size: .86rem;
  font-weight: 850;
}

.summary-icon-local {
  display: grid !important;
  width: 2.2rem;
  height: 2.2rem;
  place-items: center;
  border-radius: 10px;
  background: #edf5ff;
  color: #1671f9 !important;
  font-size: 1.15rem !important;
  font-weight: 900 !important;
}

.service-summary-local strong {
  margin-top: .6rem;
  color: #1469ec;
  font-size: clamp(1.05rem, 1.8vw, 1.45rem);
  font-weight: 900;
  letter-spacing: -.035em;
}

.service-summary-local article:last-child strong {
  font-size: clamp(.98rem, 1.45vw, 1.18rem);
}

.dashboard-section {
  margin-top: 1.55rem;
}

.dashboard-section > .section-head {
  margin: 0 0 1rem;
}

.dashboard-section > .section-head h2 {
  color: #142c4c;
  font-size: 1.32rem;
}

.filter-panel-local {
  gap: 1.15rem;
  border: 1px solid #dfe8f3;
  border-radius: 20px;
  background: rgba(255, 255, 255, .96);
  box-shadow: 0 12px 30px rgba(29, 55, 88, .055);
  padding: 1.45rem;
}

.condition-control-grid-local {
  gap: 1.15rem;
  padding: 1.15rem;
  border: 1px solid #ebf0f6;
  border-radius: 16px;
  background: linear-gradient(180deg, #fdfefe, #fbfdff);
}

.control-group-local {
  gap: .7rem;
}

.control-group-local h3 {
  display: flex;
  align-items: center;
  color: #079f9b;
  font-size: .94rem;
  letter-spacing: -.02em;
}

.control-group-local h3::before {
  margin-right: .48rem;
}

.segment-grid-local {
  gap: .7rem;
}

.segment-grid-local button {
  min-height: 80px;
  border-color: #dce6f2;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 2px 5px rgba(42, 67, 98, .015);
  padding: .9rem .95rem;
  transition: border-color .18s ease, background .18s ease, box-shadow .18s ease, transform .18s ease;
}

.segment-grid-local button:hover {
  border-color: #9fc1ff;
  box-shadow: 0 8px 18px rgba(37, 99, 235, .08);
  transform: translateY(-1px);
}

.segment-grid-local button span {
  color: #1c3557;
  font-size: .96rem;
}

.segment-grid-local button small {
  margin-top: .38rem;
  color: #718198;
  font-size: .77rem;
}

.segment-grid-local button.active {
  border-color: #2878ff;
  background: linear-gradient(135deg, #f8fbff, #eef5ff);
  box-shadow: 0 7px 18px rgba(37, 99, 235, .12), inset 0 0 0 1px rgba(37, 99, 235, .1);
}

.segment-grid-local button.active span {
  color: #1765e5;
}

.input-grid-local {
  gap: 1rem;
}

.step-box-local,
.input-grid-local label {
  min-height: 104px;
  gap: .75rem;
  border-color: #e0e9f3;
  border-radius: 14px;
  background: #fbfdff;
  padding: 1rem 1.15rem;
}

.field-label-local {
  color: #079f9b !important;
  font-size: .88rem !important;
  font-weight: 900 !important;
}

.step-box-local div {
  grid-template-columns: 38px minmax(0, 1fr) 38px;
  gap: .8rem;
}

.step-box-local button {
  width: 38px;
  height: 38px;
  border: 1px solid #e0eaf5;
  border-radius: 10px;
  background: #edf3f8;
  color: #213955;
  font-size: 1.12rem;
}

.step-box-local button:hover {
  background: #e1edff;
  color: #1469ec;
}

.step-box-local strong {
  color: #142d50;
  font-size: 1.34rem;
  letter-spacing: -.04em;
}

.select-field-local select {
  min-height: 42px;
  border: 1px solid #d9e5f1;
  border-radius: 10px;
  background: #fff;
  color: #183452;
  font-weight: 800;
  outline-color: #2c77fa;
  padding: .55rem .75rem;
}

.quick-choice-local {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 46px;
}

.quick-choice-local > span {
  flex: 0 0 auto;
  color: #526780;
  font-size: .86rem;
  font-weight: 900;
}

.purpose-row-local {
  gap: .55rem;
}

.purpose-row-local button,
.sort-tabs-local button {
  min-height: 36px;
  border-color: #dbe5f1;
  border-radius: 9px;
  background: #fff;
  color: #40546d;
  font-size: .84rem;
  transition: all .18s ease;
}

.purpose-row-local button:hover,
.sort-tabs-local button:hover {
  border-color: #a9c8ff;
  color: #1969ec;
}

.purpose-row-local button.active,
.sort-tabs-local button.active {
  border-color: #91b9ff;
  background: #eef5ff;
  color: #1769ef;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, .08);
}

.filter-panel-local .btn.full {
  min-height: 50px;
  border-radius: 11px;
  box-shadow: 0 10px 20px rgba(25, 105, 236, .2);
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: -.015em;
}

.filter-panel-local .btn.full span {
  margin-right: .35rem;
  font-size: 1.1rem;
}

.result-head-local {
  align-items: end;
  margin-top: .5rem;
  margin-bottom: 1rem;
}

.result-head-local h2 {
  margin-bottom: .3rem;
  font-size: 1.42rem;
}

.result-list-local {
  gap: .9rem;
}

.result-card-local {
  grid-template-columns: 62px minmax(0, 1fr) minmax(245px, auto);
  gap: 1.25rem;
  min-height: 138px;
  border-color: #dce6f1;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(29, 55, 88, .045);
  padding: 1rem 1.15rem;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.result-card-local:hover {
  border-color: #a9c8ff;
  box-shadow: 0 15px 28px rgba(37, 99, 235, .09);
  transform: translateY(-2px);
}

.result-card-local.featured {
  border-color: #9ec1ff;
  background: linear-gradient(105deg, #fff 0, #fbfdff 67%, #f4f9ff 100%);
}

.rank-local {
  width: 56px;
  height: 82px;
  border-radius: 10px;
  background: #edf2f7;
  color: #50647a;
  font-size: 1.5rem;
}

.featured .rank-local {
  background: linear-gradient(160deg, #1f78fa, #155de8);
  box-shadow: 0 8px 16px rgba(30, 105, 234, .2);
}

.product-main-local {
  min-width: 0;
}

.product-main-local div.product-heading-local {
  align-items: center;
  gap: .5rem;
  margin: 0;
}

.product-bank-local {
  color: #5d7088;
  font-size: .82rem;
  font-weight: 850;
}

.product-type-local {
  padding: .22rem .52rem;
  border-radius: 999px;
  background: #eff5ff;
  color: #2873e9;
  font-size: .73rem;
  font-weight: 900;
}

.product-main-local h3 {
  margin: .36rem 0 .55rem;
  color: #152f51;
  font-size: 1.2rem;
  letter-spacing: -.025em;
}

.product-main-local p.product-meta-local {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  color: #5d7088;
  font-size: .84rem;
}

.product-meta-local span + span {
  margin-left: .65rem;
  padding-left: .65rem;
  border-left: 1px solid #dce5ef;
}

.product-main-local div:not(.product-heading-local) {
  gap: .42rem;
  margin-top: .7rem;
}

.product-main-local em {
  border: 1px solid #edf1f6;
  background: #f5f8fc;
  color: #63758c;
  font-size: .73rem;
}

.ai-reason-local {
  display: grid !important;
  gap: .35rem !important;
  margin-top: .75rem !important;
  border: 1px solid #dfeaff;
  border-radius: 12px;
  background: #f7fbff;
  padding: .72rem .82rem;
}

.ai-reason-local > span {
  color: #176be9;
  font-size: .76rem;
  font-weight: 900;
}

.ai-reason-local p {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: #405773;
  font-size: .8rem;
  font-weight: 750;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.ai-tags-local {
  display: flex !important;
  flex-wrap: wrap;
  gap: .35rem !important;
  margin-top: 0 !important;
}

.ai-tags-local small {
  border-radius: 999px;
  background: #eaf3ff;
  color: #246ce5;
  font-size: .68rem;
  font-weight: 900;
  padding: .18rem .45rem;
}

.ai-caution-local {
  color: #7c8797;
  font-size: .7rem;
  font-weight: 800;
}

.result-money-local {
  min-width: 230px;
  justify-items: start;
  gap: .3rem;
  border-left: 1px solid #e2eaf3;
  padding-left: 1.35rem;
}

.result-money-local span {
  color: #566b84;
  font-size: .8rem;
}

.result-money-local strong {
  color: #176be9;
  font-size: clamp(1.35rem, 2vw, 1.7rem);
  letter-spacing: -.045em;
}

.result-money-local small {
  color: #08a39f;
  font-size: .82rem;
}

.loan-summary-local article {
  min-height: 104px;
}

.loan-strategy-grid-local {
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
}

.loan-input-grid-local {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.loan-input-grid-local .select-field-local {
  min-height: 104px;
}

.loan-result-card-local .product-type-local {
  background: #e8f1ff;
  color: #1f66d6;
}

@media (max-width: 980px) {
  .service-panel-local {
    grid-template-columns: 1fr;
    gap: 1.2rem;
  }

  .service-summary-local.loan-summary-local,
  .loan-strategy-grid-local,
  .savings-type-grid-local,
  .loan-input-grid-local {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }

  .result-card-local {
    grid-template-columns: 58px minmax(0, 1fr);
  }

  .result-money-local {
    grid-column: 2;
    border-top: 1px solid #e2eaf3;
    border-left: 0;
    padding-top: .85rem;
    padding-left: 0;
  }
}

@media (max-width: 720px) {
  .recommend-container-local {
    padding-top: 1.75rem;
  }

  .service-panel-local,
  .filter-panel-local {
    border-radius: 16px;
    padding: 1.15rem;
  }

  .service-summary-local,
  .service-summary-local.loan-summary-local,
  .condition-control-grid-local,
  .input-grid-local,
  .loan-strategy-grid-local,
  .savings-type-grid-local,
  .loan-input-grid-local {
    grid-template-columns: 1fr !important;
  }

  .quick-choice-local {
    display: grid;
    gap: .6rem;
  }

  .result-card-local {
    grid-template-columns: 1fr;
    gap: .9rem;
  }

  .rank-local {
    width: 48px;
    height: 48px;
  }

  .result-money-local {
    grid-column: auto;
  }
}
</style>
