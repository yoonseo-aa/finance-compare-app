<script setup>
import { Chart } from "chart.js/auto";
import { computed, nextTick, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import PageHeader from "../components/PageHeader.vue";
import StatusBlock from "../components/StatusBlock.vue";

const chartCanvas = ref(null);
const rows = ref([]);
const error = ref("");
const loading = ref(false);
const sourceInfo = ref({ source: "", symbol: "", isLive: false, exchangeRate: null, unit: "원/g" });
const filters = reactive({ asset: "gold", start: "", end: "" });
let chart = null;

const assetLabel = computed(() => filters.asset === "gold" ? "금" : "은");
const latestRow = computed(() => rows.value.at(-1) || null);
const previousRow = computed(() => rows.value.length > 1 ? rows.value.at(-2) : null);
const firstRow = computed(() => rows.value[0] || null);
const marketDirection = computed(() => latestChange.value?.direction || "flat");
const chartColor = computed(() => filters.asset === "gold" ? "#C59A3D" : "#8FA1B3");
const chartFill = computed(() => filters.asset === "gold" ? "rgba(197, 154, 61, .22)" : "rgba(143, 161, 179, .2)");
const assetToneClass = computed(() => [filters.asset === "gold" ? "is-gold" : "is-silver", `is-${marketDirection.value}`]);

const latestChange = computed(() => makeChange(rowPrice(latestRow.value), rowPrice(previousRow.value)));
const periodChange = computed(() => makeChange(rowPrice(latestRow.value), rowPrice(firstRow.value)));

const recentRows = computed(() => {
  const source = rows.value.slice(-6);
  return source.slice(-5).map((row, index) => {
    const originalIndex = rows.value.length - source.length + index + 1;
    const previous = rows.value[originalIndex - 1];
    return {
      ...row,
      change: makeChange(rowPrice(row), rowPrice(previous))
    };
  }).reverse();
});

const displayRows = computed(() => softenAbruptMoves(rows.value));
const adjustedCount = computed(() => displayRows.value.filter(row => row.adjusted).length);

function rowPrice(row, key = "krw_per_gram") {
  return Number(row?.[key] ?? row?.krw_price ?? row?.price ?? 0);
}

function makeChange(current, previous) {
  if (!current || !previous) return null;
  const amount = current - previous;
  return {
    amount,
    percent: (amount / previous) * 100,
    direction: amount > 0 ? "up" : amount < 0 ? "down" : "flat"
  };
}

function softenAbruptMoves(sourceRows) {
  const threshold = filters.asset === "gold" ? 0.04 : 0.06;

  return sourceRows.map((row, index) => {
    const previous = sourceRows[index - 1];
    const next = sourceRows[index + 1];
    const currentPrice = rowPrice(row);
    const previousPrice = rowPrice(previous);
    const nextPrice = rowPrice(next);
    if (!previous || !next || !previousPrice || !currentPrice || !nextPrice) return row;

    const neighbourEstimate = previousPrice + ((nextPrice - previousPrice) / 2);
    const relativeError = Math.abs((currentPrice - neighbourEstimate) / neighbourEstimate);
    const previousMove = Math.abs((currentPrice - previousPrice) / previousPrice);
    const nextMove = Math.abs((nextPrice - currentPrice) / currentPrice);
    const hasAbruptMove = previousMove > threshold || nextMove > threshold;

    if (hasAbruptMove && relativeError > threshold) {
      const blendWeight = Math.min(0.82, (relativeError - threshold) / (threshold * 1.4));
      const adjustedPrice = currentPrice * (1 - blendWeight) + neighbourEstimate * blendWeight;
      return {
        ...row,
        krw_per_gram: Math.round(adjustedPrice),
        adjusted: true,
        rawKrwPrice: currentPrice
      };
    }

    return row;
  });
}

function formatNumber(value) {
  if (value === undefined || value === null || value === "" || Number.isNaN(Number(value))) return "-";
  return Number(value).toLocaleString("ko-KR", { maximumFractionDigits: 0 });
}

function formatWon(value) {
  const formatted = formatNumber(value);
  return formatted === "-" ? "-" : `${formatted}원`;
}

function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(value)) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatChange(change) {
  if (!change) return "전일 데이터 없음";
  const amount = change.amount > 0 ? `+${formatWon(change.amount)}` : formatWon(change.amount);
  return `${amount} (${formatPercent(change.percent)})`;
}

function axisBounds(values) {
  if (!values.length) return {};
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || max * 0.02 || 1;
  const padding = range * 0.045;
  return { min: min - padding, max: max + padding };
}

function renderChart() {
  if (!chartCanvas.value) return;
  chart?.destroy();

  const chartRows = displayRows.value;
  const labels = chartRows.map(row => row.date);
  const data = chartRows.map(row => rowPrice(row));
  const bounds = axisBounds(data);
  const context = chartCanvas.value.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 380);
  gradient.addColorStop(0, chartFill.value);
  gradient.addColorStop(.7, filters.asset === "gold" ? "rgba(197, 154, 61, .06)" : "rgba(143, 161, 179, .06)");
  gradient.addColorStop(1, "rgba(255, 255, 255, 0)");

  chart = new Chart(chartCanvas.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `${assetLabel.value} 시세`,
          data,
          borderColor: chartColor.value,
          backgroundColor: gradient,
          borderWidth: 2.4,
          pointRadius: 0,
          pointHoverRadius: 4,
          pointHitRadius: 14,
          pointHoverBackgroundColor: "#ffffff",
          pointHoverBorderColor: chartColor.value,
          pointHoverBorderWidth: 2,
          fill: true,
          borderCapStyle: "round",
          borderJoinStyle: "round",
          cubicInterpolationMode: "monotone",
          tension: 0.24
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0F2748",
          padding: 12,
          titleFont: { weight: "800" },
          bodyFont: { weight: "700" },
          callbacks: {
            title(items) { return items[0]?.label || ""; },
            label(context) {
              const row = chartRows[context.dataIndex];
              const suffix = row?.adjusted ? ` (보정 전 ${formatWon(row.rawKrwPrice)})` : "";
              return `${context.dataset.label}: ${formatWon(context.parsed.y)}/g${suffix}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(219, 231, 245, .72)" },
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
          grid: { color: "rgba(219, 231, 245, .82)" },
          ticks: {
            color: "#64748b",
            callback(value) { return `${formatNumber(value)}원`; }
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
    rows.value = data.rows || [];
    sourceInfo.value = {
      source: data.source || "",
      symbol: data.symbol || "",
      isLive: Boolean(data.is_live),
      exchangeRate: data.exchange_rate || null,
      unit: data.unit || "원/g"
    };
    error.value = data.error || "";
    await nextTick();
    renderChart();
  } catch (err) {
    rows.value = [];
    error.value = err.message || "시세 정보를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadPrices);
</script>

<template>
  <main class="container spot-page" :class="assetToneClass">
    <PageHeader
      title="금은시세"
      description="금과 은의 현재 시세를 원화 기준으로 확인하고 변동 추이를 비교해보세요."
    />

    <form class="filter-bar spot-filter-toolbar" @submit.prevent="loadPrices">
      <select v-model="filters.asset" aria-label="상품 선택">
        <option value="gold">금</option>
        <option value="silver">은</option>
      </select>
      <input v-model="filters.start" type="date" aria-label="시작일">
      <input v-model="filters.end" type="date" aria-label="종료일">
      <button class="btn primary" type="submit">적용</button>
    </form>

    <StatusBlock :loading="loading" :error="error" />

    <section v-if="latestRow" class="spot-summary-grid">
      <article class="metric-card spot-primary-card">
        <span>{{ assetLabel }} 현재 시세</span>
        <strong>{{ formatWon(latestRow.krw_per_gram) }}</strong>
        <small :class="['change-pill', latestChange?.direction]">전일 대비 {{ formatChange(latestChange) }}</small>
      </article>
      <article class="metric-card">
        <span>{{ assetLabel }} 1돈당</span>
        <strong>{{ formatWon(latestRow.krw_per_don) }}</strong>
        <small>3.75g 기준</small>
      </article>
      <article class="metric-card">
        <span>{{ assetLabel }} 1oz당</span>
        <strong>{{ formatWon(latestRow.krw_per_oz) }}</strong>
        <small>트로이온스 기준</small>
      </article>
      <article class="metric-card period-card">
        <span>기간 등락률</span>
        <strong :class="{ positive: periodChange?.percent > 0, negative: periodChange?.percent < 0 }">{{ formatPercent(periodChange?.percent) }}</strong>
        <small :class="['change-pill', periodChange?.direction]">{{ formatChange(periodChange) }}</small>
      </article>
    </section>

    <section v-if="latestRow" class="chart-panel professional-chart-panel">
      <div class="chart-title-row">
        <div>
          <span>{{ sourceInfo.source }} · {{ sourceInfo.symbol }} · 환율 {{ sourceInfo.exchangeRate ? formatNumber(sourceInfo.exchangeRate) : '-' }}원/USD</span>
          <h2>금·은 시세 그래프 <small>({{ sourceInfo.unit }}, 원화 기준)</small></h2>
        </div>
        <div class="chart-price-badge">
          <strong>{{ assetLabel }} 1g {{ formatWon(latestRow.krw_per_gram) }}</strong>
          <small :class="['change-pill', latestChange?.direction]">{{ formatChange(latestChange) }}</small>
        </div>
      </div>
      <canvas ref="chartCanvas"></canvas>
      <p class="chart-footnote">
        원자료는 달러/트로이온스 기준이며, USD/KRW 환율을 적용해 원/g으로 변환했습니다.
        <span v-if="adjustedCount">그래프 보정 지점 {{ adjustedCount }}개</span>
      </p>
    </section>

    <section v-if="latestRow" class="content-panel spot-data-panel">
      <div class="section-head compact-head">
        <h2>일별 시세</h2>
        <p>최근 거래일의 종가와 전일 대비 흐름을 원/g 기준으로 표시합니다.</p>
      </div>
      <table>
        <thead>
          <tr>
            <th>날짜</th>
            <th>종가</th>
            <th>전일대비</th>
            <th>등락률</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in recentRows" :key="row.date">
            <td>{{ row.date }}</td>
            <td class="price-cell">{{ formatWon(row.krw_per_gram) }}</td>
            <td><span :class="['table-delta', row.change?.direction]">{{ row.change?.amount > 0 ? '▲' : row.change?.amount < 0 ? '▼' : '-' }} {{ row.change ? formatWon(Math.abs(row.change.amount)) : '-' }}</span></td>
            <td><span :class="['table-change-badge', row.change?.direction]">{{ formatPercent(row.change?.percent) }}</span></td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>


