<script setup>
import { Chart } from "chart.js/auto";
import { computed, nextTick, onMounted, ref } from "vue";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import PageHeader from "../components/PageHeader.vue";

const dashboard = ref(null);
const loading = ref(true);
const error = ref("");
const maturityCanvas = ref(null);
const rateCanvas = ref(null);
const conditionCanvas = ref(null);
const chartInstances = [];

const assetStatus = computed(() => dashboard.value?.asset_status || {});
const goal = computed(() => dashboard.value?.goal || {});
const topRecommendations = computed(() => dashboard.value?.recommendation_groups?.stable || []);

function formatMoney(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

function formatPercent(value) {
  return `${Number(value || 0).toLocaleString("ko-KR", { maximumFractionDigits: 1 })}%`;
}

function shortLabel(label) {
  if (!label) return "";
  return label.length > 10 ? `${label.slice(0, 10)}...` : label;
}

function resetCharts() {
  while (chartInstances.length) chartInstances.pop().destroy();
}

function makeGradient(canvas, color) {
  const context = canvas.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 320);
  gradient.addColorStop(0, color);
  gradient.addColorStop(1, "rgba(255,255,255,0)");
  return gradient;
}

function baseLineOptions(unit = "") {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { intersect: false, mode: "index" },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#0f172a",
        padding: 12,
        titleFont: { weight: "800" },
        bodyFont: { weight: "700" },
        callbacks: {
          label(context) {
            const value = Number(context.parsed.y || 0).toLocaleString("ko-KR", { maximumFractionDigits: 1 });
            return `${context.dataset.label}: ${value}${unit}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: "rgba(148, 163, 184, .16)" },
        border: { color: "#d7dee8" },
        ticks: { color: "#7b8794", maxRotation: 0, callback(value) { return shortLabel(this.getLabelForValue(value)); } }
      },
      y: {
        border: { display: false },
        grid: { color: "rgba(148, 163, 184, .18)" },
        ticks: { color: "#64748b" }
      }
    }
  };
}

function renderCharts() {
  if (!dashboard.value) return;
  resetCharts();
  const charts = dashboard.value.charts;

  if (maturityCanvas.value) {
    chartInstances.push(new Chart(maturityCanvas.value, {
      type: "line",
      data: {
        labels: charts.maturity_amounts.labels,
        datasets: [{
          label: "예상 만기 금액",
          data: charts.maturity_amounts.data,
          borderColor: "#20b886",
          backgroundColor: makeGradient(maturityCanvas.value, "rgba(32, 184, 134, .22)"),
          borderWidth: 1.7,
          pointRadius: 0,
          pointHoverRadius: 3.5,
          fill: true,
          cubicInterpolationMode: "monotone",
          tension: .18
        }]
      },
      options: baseLineOptions("원")
    }));
  }

  if (rateCanvas.value) {
    chartInstances.push(new Chart(rateCanvas.value, {
      type: "bar",
      data: {
        labels: charts.rate_compare.labels,
        datasets: [{ label: "최고 우대금리", data: charts.rate_compare.data, backgroundColor: "#2f80ed", borderRadius: 6 }]
      },
      options: { ...baseLineOptions("%"), plugins: { ...baseLineOptions("%").plugins, legend: { display: false } } }
    }));
  }

  if (conditionCanvas.value) {
    chartInstances.push(new Chart(conditionCanvas.value, {
      type: "bar",
      data: {
        labels: charts.condition_ease.labels,
        datasets: [{ label: "우대조건 쉬움", data: charts.condition_ease.data, backgroundColor: "#00a6a6", borderRadius: 6 }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { min: 0, max: 100, grid: { color: "rgba(148, 163, 184, .18)" } }, y: { grid: { display: false }, ticks: { callback(value) { return shortLabel(this.getLabelForValue(value)); } } } },
        plugins: { legend: { display: false } }
      }
    }));
  }
}

async function loadDashboard() {
  loading.value = true;
  error.value = "";
  try {
    dashboard.value = await apiFetch("/dashboard/");
    await nextTick();
    renderCharts();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <main class="container dashboard-page aligned-dashboard-page">
    <PageHeader
      eyebrow="MY FINANCE"
      title="개인화 대시보드"
      description="내 추천 프로필과 금융 API 상품 데이터를 바탕으로 목표 가능성, 재산현황, 추천 상품을 확인합니다."
    />

    <div class="filter-bar dashboard-action-bar">
      <RouterLink class="btn primary" to="/recommend-profile">나의 정보 입력하기</RouterLink>
      <RouterLink class="btn ghost" to="/recommendations">추천 결과 보러가기</RouterLink>
      <RouterLink class="btn ghost" to="/products">상품 보러가기</RouterLink>
    </div>

    <StatusBlock :loading="loading" :error="error" />

    <template v-if="dashboard">
      <section class="spot-summary-grid dashboard-summary-grid">
        <article class="metric-card">
          <span>목표 달성 가능성</span>
          <strong>{{ formatPercent(goal.success_probability) }}</strong>
        </article>
        <article class="metric-card">
          <span>목표 금액</span>
          <strong>{{ formatMoney(goal.target_amount) }}</strong>
        </article>
        <article class="metric-card">
          <span>목표 기간</span>
          <strong>{{ goal.target_months }}개월</strong>
        </article>
        <article class="metric-card">
          <span>월 저축 가능 금액</span>
          <strong>{{ formatMoney(goal.monthly_saving) }}</strong>
        </article>
        <article class="metric-card">
          <span>예상 최고 만기 금액</span>
          <strong>{{ formatMoney(goal.best_expected_amount) }}</strong>
        </article>
        <article class="metric-card">
          <span>월 추가 필요 금액</span>
          <strong>{{ formatMoney(goal.gap_monthly) }}</strong>
        </article>
      </section>

      <section class="chart-panel professional-chart-panel dashboard-main-chart">
        <div class="chart-title-row">
          <div>
            <span>FinPick Dashboard API · 금융감독원 상품 데이터</span>
            <h2>예상 만기 금액 추이</h2>
          </div>
          <strong>{{ formatMoney(goal.best_expected_amount) }}</strong>
        </div>
        <canvas ref="maturityCanvas"></canvas>
        <p class="chart-footnote">추천 대상 상품의 기간과 우대금리를 기준으로 예상 만기 금액을 계산해 API 데이터로 그렸습니다.</p>
      </section>

      <section class="content-panel asset-status-panel">
        <div class="section-head compact-head">
          <h2>현재 재산현황</h2>
          <p>추천 진단에서 입력한 재산/소득 정보와 현재 저축 여력을 요약합니다.</p>
        </div>
        <div class="asset-status-grid">
          <div><span>소득</span><strong>{{ assetStatus.income_level }}</strong></div>
          <div><span>재산</span><strong>{{ assetStatus.asset_level }}</strong></div>
          <div><span>직업/상태</span><strong>{{ assetStatus.employment_status }}</strong></div>
          <div><span>저축 목적</span><strong>{{ assetStatus.saving_purpose }}</strong></div>
          <div><span>예상 원금</span><strong>{{ formatMoney(assetStatus.principal) }}</strong></div>
          <div><span>예상 이자</span><strong>{{ formatMoney(assetStatus.expected_interest) }}</strong></div>
          <div><span>목표 대비 월 저축 여력</span><strong>{{ formatPercent(assetStatus.monthly_capacity_rate) }}</strong></div>
          <div><span>예상 만기 자산</span><strong>{{ formatMoney(assetStatus.best_expected_amount) }}</strong></div>
        </div>
      </section>

      <section class="content-panel dashboard-recommend-panel">
        <div class="section-head compact-head">
          <h2>맞춤 추천 상품</h2>
          <p>추천점수와 추천 이유가 높은 상품입니다.</p>
        </div>
        <div class="dashboard-recommend-list">
          <RouterLink v-for="item in topRecommendations" :key="item.product.id" class="dashboard-recommend-item" :to="`/products/${item.product.id}`">
            <div>
              <span>{{ item.product.bank_name }}</span>
              <strong>{{ item.product.name }}</strong>
              <p>{{ item.reasons?.[0] }} · {{ item.reasons?.[1] }}</p>
            </div>
            <em>{{ item.score }}점</em>
          </RouterLink>
        </div>
      </section>

      <!-- <section class="dashboard-chart-grid">
        <article class="content-panel dashboard-sub-chart">
          <div class="chart-title-row compact-chart-head">
            <div>
              <span>Rate compare</span>
              <h2>상품별 금리 비교</h2>
            </div>
          </div>
          <canvas ref="rateCanvas"></canvas>
        </article>
        <article class="content-panel dashboard-sub-chart">
          <div class="chart-title-row compact-chart-head">
            <div>
              <span>Condition ease</span>
              <h2>우대조건 쉬움</h2>
            </div>
          </div>
          <canvas ref="conditionCanvas"></canvas>
        </article>
      </section> -->
    </template>
  </main>
</template>

