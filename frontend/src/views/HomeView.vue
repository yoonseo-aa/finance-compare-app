<script setup>
const serviceHighlights = [
  {
    label: "STEP 1",
    title: "예적금 추천 진단",
    text: "나이대, 가족 상황, 소득, 재산, 저축 목적을 입력하고 추천 점수를 계산합니다.",
    to: "/recommend-profile",
    icon: "chart"
  },
  {
    label: "STEP 2",
    title: "맞춤 추천 결과",
    text: "상품별 추천점수와 나에게 맞는 이유를 함께 확인합니다.",
    to: "/recommendations",
    icon: "bank"
  },
  {
    label: "MY",
    title: "마이페이지",
    text: "추천 프로필, 가입 상품, 개인화 대시보드를 한곳에서 관리합니다.",
    to: "/mypage",
    icon: "user"
  }
];

const dashboardPreview = [
  { label: "추천점수", value: "116" },
  { label: "추천 이유", value: "3+" },
  { label: "API 상품", value: "96" }
];

const stockTop5 = [
  { rank: 1, name: "삼성전자", symbol: "005930", change: "+1.8%", theme: "반도체" },
  { rank: 2, name: "SK하이닉스", symbol: "000660", change: "+2.4%", theme: "AI 메모리" },
  { rank: 3, name: "NAVER", symbol: "035420", change: "+0.9%", theme: "플랫폼" },
  { rank: 4, name: "현대차", symbol: "005380", change: "+1.2%", theme: "모빌리티" },
  { rank: 5, name: "LG에너지솔루션", symbol: "373220", change: "+0.7%", theme: "2차전지" }
];
</script>

<template>
  <main>
    <section class="hero-band bank-hero">
      <div class="hero-copy">
        <p class="eyebrow">금융 상품 비교 애플리케이션</p>
        <h1>FinPick</h1>
        <p>회원가입은 간단하게, 예적금 추천은 별도 진단으로 정확하게. 내 현재 상황을 바탕으로 추천점수와 추천 이유를 보여주는 금융 추천 서비스입니다.</p>
        <div class="hero-actions">
          <RouterLink class="btn primary large" to="/recommend-profile">나에게 맞는 예적금 찾기</RouterLink>
          <RouterLink class="btn ghost large" to="/products">상품 비교</RouterLink>
        </div>
      </div>

      <div class="hero-visual service-highlight-panel">
        <RouterLink
          v-for="item in serviceHighlights"
          :key="item.title"
          class="market-tile service-tile"
          :to="item.to"
        >
          <span class="service-icon" :class="`icon-${item.icon}`" aria-hidden="true">
            <svg v-if="item.icon === 'bank'" viewBox="0 0 24 24"><path d="M3 9.5 12 4l9 5.5"/><path d="M5 10h14v9H5z"/><path d="M8 13v4M12 13v4M16 13v4"/></svg>
            <svg v-else-if="item.icon === 'chart'" viewBox="0 0 24 24"><path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 3-4 3 2 4-7"/></svg>
            <svg v-else viewBox="0 0 24 24"><path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>
          </span>
          <span>{{ item.label }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.text }}</p>
        </RouterLink>
      </div>
    </section>

    <section class="container compact-dashboard-section">
      <div class="section-head split-section-head">
        <div>
          <h2>개인화 추천 흐름</h2>
          <p>입력한 상황을 점수화해서 왜 이 상품이 맞는지까지 보여줍니다.</p>
        </div>
        <RouterLink class="text-link" to="/recommendations">추천 결과 보기</RouterLink>
      </div>
      <div class="dashboard-preview-layout">
        <article class="dashboard-graph-card">
          <div class="graph-head">
            <span>추천 점수 예시</span>
            <strong>116점</strong>
          </div>
          <svg class="home-line-chart" viewBox="0 0 420 180" role="img" aria-label="추천 점수 그래프">
            <defs>
              <linearGradient id="homeChartFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stop-color="#2f80ed" stop-opacity="0.28"/>
                <stop offset="1" stop-color="#2f80ed" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path class="chart-area" d="M24 146 C74 130, 96 118, 132 124 C172 130, 192 88, 232 94 C276 100, 292 52, 332 58 C362 62, 386 44, 404 32 L404 160 L24 160 Z"/>
            <path class="chart-line" d="M24 146 C74 130, 96 118, 132 124 C172 130, 192 88, 232 94 C276 100, 292 52, 332 58 C362 62, 386 44, 404 32"/>
            <circle cx="404" cy="32" r="7"/>
          </svg>
        </article>
        <div class="dashboard-preview-grid bank-summary-grid">
          <article v-for="item in dashboardPreview" :key="item.label" class="dashboard-preview-card">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </article>
        </div>
      </div>
    </section>

    <section class="container">
      <div class="section-head">
        <h2>서비스</h2>
        <p>추천, 비교, 대시보드, 현물 시세까지 한 흐름으로 확인합니다.</p>
      </div>
      <div class="feature-grid service-grid-bank">
        <RouterLink class="feature-card" to="/recommend-profile"><strong>예적금 추천 진단</strong><span>현재상황 입력과 추천점수 계산</span></RouterLink>
        <RouterLink class="feature-card" to="/products"><strong>예적금 비교</strong><span>은행 필터, 검색, 상세 금리</span></RouterLink>
        <RouterLink class="feature-card" to="/dashboard"><strong>개인화 대시보드</strong><span>목표 달성률과 추천 요약</span></RouterLink>
        <RouterLink class="feature-card" to="/mypage"><strong>마이페이지</strong><span>추천 프로필과 가입상품 관리</span></RouterLink>
        <RouterLink class="feature-card" to="/spot"><strong>현물 시각화</strong><span>금/은 API 기반 시세 차트</span></RouterLink>
        <RouterLink class="feature-card" to="/banks"><strong>은행 찾기</strong><span>Kakao 지도 기반 탐색</span></RouterLink>
      </div>
    </section>

    <section class="surface-band bank-surface">
      <div class="container">
        <div class="section-head">
          <h2>주식 종목 Top 5</h2>
          <p>관심 종목 흐름을 빠르게 확인합니다.</p>
        </div>
        <div class="stock-grid">
          <article v-for="stock in stockTop5" :key="stock.symbol" class="stock-card">
            <span class="stock-rank">{{ stock.rank }}</span>
            <div>
              <strong>{{ stock.name }}</strong>
              <p>{{ stock.symbol }} · {{ stock.theme }}</p>
            </div>
            <em>{{ stock.change }}</em>
          </article>
        </div>
      </div>
    </section>
  </main>
</template>
