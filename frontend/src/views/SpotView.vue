<script setup>
import { Chart } from "chart.js/auto";
import { computed, nextTick, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";

const chartCanvas = ref(null);
const rows = ref([]);
const error = ref("");
const loading = ref(false);
const sourceInfo = ref({ source: "", symbol: "", isLive: false });
const filters = reactive({ asset: "gold", start: "", end: "" });
let chart = null;

const assetLabel = computed(() => filters.asset === "gold" ? "금" : "은");
const latestRow = computed(() => rows.value.at(-1) || null);
const firstRow = computed(() => rows.value[0] || null);
const recentRows = computed(() => rows.value.slice(-5).reverse());
const chartColor = computed(() => "#20b886");
const chartFill = computed(() => "rgba(32, 184, 134, .22)");

const periodChange = computed(() => {
  if (!firstRow.value || !latestRow.value || !firstRow.value.price) return null;
  return ((latestRow.value.price - firstRow.value.price) / firstRow.value.price) * 100;
});

const displayRows = computed(() => softenAbruptMoves(rows.value));
const adjustedCount = computed(() => displayRows.value.filter(row => row.adjusted).length);

function softenAbruptMoves(sourceRows) {
  const threshold = filters.asset === "gold" ? 0.04 : 0.06;

  return sourceRows.map((row, index) => {
    const previous = sourceRows[index - 1];
    const next = sourceRows[index + 1];
    if (!previous || !next || !previous.price || !row.price || !next.price) return row;

    const neighbourEstimate = previous.price + ((next.price - previous.price) / 2);
    const relativeError = Math.abs((row.price - neighbourEstimate) / neighbourEstimate);
    const previousMove = Math.abs((row.price - previous.price) / previous.price);
    const nextMove = Math.abs((next.price - row.price) / row.price);
    const hasAbruptMove = previousMove > threshold || nextMove > threshold;

    if (hasAbruptMove && relativeError > threshold) {
      const blendWeight = Math.min(0.82, (relativeError - threshold) / (threshold * 1.4));
      const adjustedPrice = row.price * (1 - blendWeight) + neighbourEstimate * blendWeight;
      return {
        ...row,
        price: Number(adjustedPrice.toFixed(3)),
        adjusted: true,
        rawPrice: row.price
      };
    }

    return row;
  });
}

function formatNumber(value) {
  if (value === undefined || value === null || value === "") return "-";
  return Number(value).toLocaleString("ko-KR", { maximumFractionDigits: 3 });
}

function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(value)) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function axisBounds(values) {
  if (!values.length) return {};
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || max * 0.02 || 1;
  const padding = range * 0.08;
  return {
    min: min - padding,
    max: max + padding
  };
}

function renderChart() {
  if (!chartCanvas.value) return;
  chart?.destroy();

  const chartRows = displayRows.value;
  const labels = chartRows.map(row => row.date);
  const bounds = axisBounds(chartRows.map(row => row.price));
  const context = chartCanvas.value.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 380);
  gradient.addColorStop(0, chartFill.value);
  gradient.addColorStop(1, "rgba(255, 255, 255, 0)");

  chart = new Chart(chartCanvas.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `${assetLabel.value} 시세`,
          data: chartRows.map(row => row.price),
          borderColor: chartColor.value,
          backgroundColor: gradient,
          borderWidth: 1.45,
          pointRadius: 0,
          pointHoverRadius: 3.5,
          pointHitRadius: 14,
          pointHoverBackgroundColor: "#ffffff",
          pointHoverBorderColor: chartColor.value,
          pointHoverBorderWidth: 1.5,
          fill: true,
          borderCapStyle: "round",
          borderJoinStyle: "round",
          cubicInterpolationMode: "monotone",
          tension: 0.18
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      parsing: true,
      interaction: {
        intersect: false,
        mode: "index"
      },
      plugins: {
        legend: {
          display: false,
          position: "top",
          align: "end",
          labels: {
            boxWidth: 10,
            boxHeight: 10,
            usePointStyle: true,
            color: "#475569",
            font: { weight: "700" }
          }
        },
        tooltip: {
          backgroundColor: "#0f172a",
          padding: 12,
          titleFont: { weight: "800" },
          bodyFont: { weight: "700" },
          callbacks: {
            title(items) {
              return items[0]?.label || "";
            },
            label(context) {
              const row = chartRows[context.dataIndex];
              const suffix = row?.adjusted ? ` (보정 전 ${formatNumber(row.rawPrice)})` : "";
              return `${context.dataset.label}: ${formatNumber(context.parsed.y)}${suffix}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(148, 163, 184, .16)" },
          border: { color: "#d7dee8" },
          ticks: {
            color: "#7b8794",
            maxTicksLimit: 6,
            maxRotation: 0,
            autoSkip: true,
            callback(value) {
              const label = this.getLabelForValue(value);
              return label ? label.slice(2, 7) : "";
            }
          }
        },
        y: {
          ...bounds,
          border: { display: false },
          grid: { color: "rgba(148, 163, 184, .18)" },
          ticks: {
            color: "#64748b",
            callback(value) {
              return formatNumber(value);
            }
          }
        }
      }
    }
  });
}

async function loadPrices() {
  loading.value = true;
  error.value = "";
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => value && params.set(key, value));
  try {
    const data = await apiFetch(`/spot/?${params.toString()}`);
    rows.value = data.rows;
    sourceInfo.value = {
      source: data.source || "",
      symbol: data.symbol || "",
      isLive: Boolean(data.is_live)
    };
    error.value = data.error || "";
    await nextTick();
    renderChart();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPrices);
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>현물 상품 시각화</h1>
      <p>네이버 금/은 시세처럼 부드러운 곡선형 가격 흐름으로 확인합니다.</p>
    </div>

    <form class="filter-bar" @submit.prevent="loadPrices">
      <select v-model="filters.asset">
        <option value="gold">Gold</option>
        <option value="silver">Silver</option>
      </select>
      <input v-model="filters.start" type="date">
      <input v-model="filters.end" type="date">
      <button class="btn primary" type="submit">적용</button>
    </form>

    <StatusBlock :loading="loading" :error="error" />

    <section v-if="latestRow" class="spot-summary-grid">
      <!-- <article class="metric-card">
        <span>선택 상품</span>
        <strong>{{ assetLabel }}</strong>
      </article> -->
      <!-- <article class="metric-card">
        <span>최근 기준일</span>
        <strong>{{ latestRow.date }}</strong>
      </article> -->
      <article class="metric-card">
        <span>최근 종가</span>
        <strong>{{ formatNumber(latestRow.price) }}</strong>
      </article>
      <!-- <article class="metric-card">
        <span>데이터 수</span>
        <strong>{{ rows.length }}건</strong>
      </article> -->
      <article class="metric-card">
        <span>조회 기간</span>
        <strong>{{ firstRow?.date }} ~ {{ latestRow.date }}</strong>
      </article>
      <article class="metric-card">
        <span>기간 등락률</span>
        <strong :class="{ positive: periodChange > 0, negative: periodChange < 0 }">{{ formatPercent(periodChange) }}</strong>
      </article>
    </section>

    <section class="chart-panel professional-chart-panel">
      <div class="chart-title-row">
        <div>
          <span>{{ sourceInfo.source }} · {{ sourceInfo.symbol }}</span>
          <h2>{{ assetLabel }} 시세 추이</h2>
        </div>
        <strong v-if="latestRow">{{ formatNumber(latestRow.price) }}</strong>
      </div>
      <canvas ref="chartCanvas"></canvas>
      <!-- <p class="chart-footnote">
        급격한 단절 구간은 앞뒤 가격의 상대 변화율을 기준으로 그래프 표시선만 완만하게 보정했습니다.
        원본 값은 아래 표에 그대로 남아 있습니다.
        <span v-if="adjustedCount">보정 지점 {{ adjustedCount }}개</span>
      </p> -->
    </section>

    <section class="content-panel">
      <div class="section-head compact-head">
        <h2>최근 가격 데이터</h2>
        <p>Yahoo Finance API에서 가져온 최근 5개 행입니다.</p>
      </div>
      <table>
        <thead>
          <tr>
            <th>날짜</th>
            <th>종가</th>
            <th>시가</th>
            <th>고가</th>
            <th>저가</th>
            <th>거래량</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in recentRows" :key="row.date">
            <td>{{ row.date }}</td>
            <td>{{ formatNumber(row.price) }}</td>
            <td>{{ formatNumber(row.open) }}</td>
            <td>{{ formatNumber(row.high) }}</td>
            <td>{{ formatNumber(row.low) }}</td>
            <td>{{ formatNumber(row.volume) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>




