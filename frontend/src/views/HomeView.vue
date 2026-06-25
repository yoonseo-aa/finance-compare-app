<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import { useCommunityStore } from "../stores/community";

const router = useRouter();
const community = useCommunityStore();
const query = ref("");
const searchedQuery = ref("");
const loading = ref(false);
const products = ref([]);
const loans = ref([]);
const news = ref([]);
const videos = ref([]);
const searchErrors = ref({ products: "", news: "", videos: "" });

const suggestions = ["예금", "적금", "주택담보대출", "전세자금대출", "삼성전자", "금리 전망", "ETF"];
const categories = [
  { icon: "⌂", label: "금융회사 개요", to: "/banks" },
  { icon: "▣", label: "정기예금", to: "/products?group=deposit&type=deposit" },
  { icon: "▤", label: "적금", to: "/products?group=deposit&type=saving" },
  { icon: "₩", label: "연금저축", to: "/products?group=deposit&type=pension" },
  { icon: "⌂", label: "주택담보대출", to: "/products?group=loan&type=mortgage" },
  { icon: "⌂", label: "전세자금대출", to: "/products?group=loan&type=rent" },
  { icon: "◉", label: "개인신용대출", to: "/products?group=loan&type=credit" }
];
const features = [
  { icon: "⌕", title: "추천 비교", text: "내게 맞는 금융상품을 추천받고 한눈에 비교해보세요.", to: "/recommend-profile" },
  { icon: "♥", title: "관심 상품", text: "관심 목록에 담은 예적금 상품을 다시 확인해보세요.", to: "/favorites" },
  { icon: "⌂", title: "금융사 검색", text: "원하는 금융회사의 상품과 정보를 빠르게 찾아보세요.", to: "/banks" }
];

const communityResults = computed(() => {
  const keyword = searchedQuery.value.trim().toLowerCase();
  if (!keyword) return [];
  return community.posts.filter(post => [post.title, post.content, post.author, ...(post.tags || [])]
    .join(" ").toLowerCase().includes(keyword)).slice(0, 3);
});

function cleanText(value = "") {
  const element = document.createElement("textarea");
  element.innerHTML = value;
  return element.value.replace(/<[^>]*>/g, "");
}

async function search(value = query.value) {
  const keyword = value.trim();
  if (!keyword) return;
  router.push({ name: "search", query: { q: keyword } });
}

function openLoanResults() {
  router.push({ path: "/products", query: { group: "loan", type: "credit", q: searchedQuery.value } });
}
</script>

<template>
  <main class="home-page">
    <section class="container home-hero">
      <div class="hero-copy">
        <p class="hero-badge">◆ 오픈 API로 더 투명하고 정확한 비교</p>
        <h1>한눈에 비교하는<br>금융상품</h1>
        <p>예금 · 적금 · 연금저축 · 주택담보대출 · 전세자금대출 · 개인신용대출까지 쉽고 빠르게 비교해보세요.</p>
        <div class="hero-actions"><RouterLink class="btn primary home-cta" to="/products">전체 상품 보러가기</RouterLink><RouterLink class="btn ghost home-cta" to="/dashboard">맞춤 상품 보러가기</RouterLink></div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="art-chart"><span></span><span></span><span></span><i></i></div><div class="art-bank">⌂</div><div class="art-card">▰</div><div class="art-coins">●<br>●<br>●</div><div class="art-shield">✓</div>
      </div>
    </section>

    <section class="container home-search-wrap">
      <form class="home-search" @submit.prevent="search()"><span aria-hidden="true">⌕</span><input v-model="query" placeholder="상품명, 은행명, 종목, 금융 키워드를 검색해보세요"><button class="btn primary" :disabled="loading">{{ loading ? "검색 중" : "검색" }}</button></form>
      <div class="home-chips"><button v-for="word in suggestions" :key="word" type="button" @click="search(word)">{{ word }}</button></div>
    </section>

    <section v-if="searchedQuery" class="container search-results">
      <div class="search-result-title"><p>통합 검색 결과</p><h2>“{{ searchedQuery }}”에 대한 결과</h2></div>
      <div class="result-grid">
        <section class="result-section"><div class="result-head"><h3>관련 금융 상품</h3><RouterLink :to="`/products?q=${encodeURIComponent(searchedQuery)}`">더보기 →</RouterLink></div><p v-if="searchErrors.products" class="result-message">{{ searchErrors.products }}</p><div v-else-if="products.length || loans.length" class="result-cards"><RouterLink v-for="product in products" :key="product.id" class="mini-card" :to="`/products/${product.id}`"><span>{{ product.product_type_label || product.product_type }}</span><strong>{{ product.name }}</strong><small>{{ product.bank_name }} · 최고 {{ Number(product.max_rate || 0).toFixed(2) }}%</small></RouterLink><button v-for="loan in loans" :key="loan.product_code" class="mini-card loan-mini" type="button" @click="openLoanResults"><span>{{ loan.loan_type_label }}</span><strong>{{ loan.name }}</strong><small>{{ loan.bank_name }} · {{ loan.rate_min ? `최저 ${loan.rate_min.toFixed(2)}%` : "금리 확인" }}</small></button></div><p v-else class="result-message">관련 결과가 없습니다.</p></section>
        <section class="result-section"><div class="result-head"><h3>관련 뉴스 기사</h3><RouterLink :to="`/videos?q=${encodeURIComponent(searchedQuery)}`">더보기 →</RouterLink></div><p v-if="searchErrors.news" class="result-message">{{ searchErrors.news }}</p><div v-else-if="news.length" class="result-cards"><a v-for="article in news" :key="article.url" class="mini-card" :href="article.url" target="_blank" rel="noopener noreferrer"><span>{{ cleanText(article.source) }}</span><strong>{{ cleanText(article.title) }}</strong><small>{{ article.published_at }}</small></a></div><p v-else class="result-message">관련 결과가 없습니다.</p></section>
        <section class="result-section"><div class="result-head"><h3>관련 유튜브 영상</h3><RouterLink :to="`/videos?q=${encodeURIComponent(searchedQuery)}`">더보기 →</RouterLink></div><p v-if="searchErrors.videos" class="result-message">{{ searchErrors.videos }}</p><div v-else-if="videos.length" class="result-cards"><a v-for="video in videos" :key="video.video_id" class="mini-card video-mini" :href="`https://www.youtube.com/watch?v=${video.video_id}`" target="_blank" rel="noopener noreferrer"><img :src="video.thumbnail" alt=""><strong>{{ cleanText(video.title) }}</strong><small>{{ cleanText(video.channel) }}</small></a></div><p v-else class="result-message">관련 결과가 없습니다.</p></section>
        <section class="result-section"><div class="result-head"><h3>커뮤니티 글</h3><RouterLink :to="`/community?q=${encodeURIComponent(searchedQuery)}`">더보기 →</RouterLink></div><div v-if="communityResults.length" class="result-cards"><RouterLink v-for="post in communityResults" :key="post.id" class="mini-card" :to="`/community/${post.id}`"><span>{{ post.category }}</span><strong>{{ post.title }}</strong><small>{{ post.author }} · 댓글 {{ post.comments }}</small></RouterLink></div><p v-else class="result-message">관련 결과가 없습니다.</p></section>
      </div>
    </section>

    <section class="container home-section"><div class="section-title"><h2>오픈 API 기반 상품 카테고리</h2><RouterLink to="/products">전체 카테고리 보기 ›</RouterLink></div><div class="category-grid"><RouterLink v-for="category in categories" :key="category.label" :to="category.to" class="category-card"><span>{{ category.icon }}</span><strong>{{ category.label }}</strong></RouterLink></div></section>
    <section class="container home-section"><div class="feature-grid"><RouterLink v-for="feature in features" :key="feature.title" :to="feature.to" class="home-feature"><span>{{ feature.icon }}</span><div><h2>{{ feature.title }}</h2><p>{{ feature.text }}</p></div><b>›</b></RouterLink></div></section>
    <section class="container trust-bar"><span>◇ 오픈 API 기반 데이터 제공</span><span>▣ 보안 인증으로 안전한 서비스</span><span>↻ 실시간 업데이트</span><span>ⓘ 금융상품 비교 플랫폼</span></section>
  </main>
</template>

<style scoped>
.home-page { min-height:calc(100vh - 72px); padding:2rem 0 3.5rem; }.home-hero { align-items:center; background:radial-gradient(circle at 78% 38%,#dbeaff 0,rgba(219,234,255,.35) 18%,transparent 42%),linear-gradient(135deg,#eef6ff,#fafcff); border-radius:24px; display:grid; grid-template-columns:1fr .85fr; min-height:386px; overflow:hidden; padding:3.25rem 4.2rem; }.hero-copy { max-width:600px; z-index:1; }.hero-badge { background:#fff; border-radius:999px; color:#2c5d9e; display:inline-block; font-size:.82rem; font-weight:850; margin:0 0 1.15rem; padding:.55rem .8rem; }.hero-copy h1 { color:#102a4b; font-size:clamp(2.5rem,5vw,4rem); letter-spacing:-.065em; line-height:1.13; margin:0; }.hero-copy>p:not(.hero-badge) { color:#526b89; font-size:1.05rem; line-height:1.85; margin:1rem 0 1.65rem; }.hero-actions { display:flex; flex-wrap:wrap; gap:.65rem; }.home-cta { min-height:54px; padding-inline:1.4rem; }.hero-art { height:300px; position:relative; }.art-chart,.art-card,.art-bank,.art-shield { box-shadow:0 18px 30px rgba(57,104,178,.15); }.art-chart { background:linear-gradient(145deg,#fff,#e8f1ff); border:1px solid #d9e6f7; border-radius:18px; height:132px; left:25px; padding:34px 18px 15px; position:absolute; top:2px; transform:rotate(-7deg); width:205px; }.art-chart span { background:#5f9cff; border-radius:3px 3px 0 0; bottom:18px; display:inline-block; margin-right:13px; position:relative; width:14px; }.art-chart span:nth-child(1){height:30px}.art-chart span:nth-child(2){height:58px}.art-chart span:nth-child(3){height:42px}.art-chart i { border-top:3px solid #236ee8; display:block; position:absolute; right:16px; top:36px; transform:rotate(-23deg); width:115px; }.art-bank { background:linear-gradient(145deg,#4385f7,#1256cb); border-radius:19px; color:#fff; font-size:6.8rem; height:155px; line-height:145px; position:absolute; right:75px; text-align:center; top:66px; transform:skewY(-3deg); width:185px; }.art-card { background:linear-gradient(145deg,#73a9ff,#2465db); border-radius:15px; color:#dbe9ff; font-size:4rem; height:106px; line-height:95px; position:absolute; right:0; text-align:center; top:95px; transform:rotate(6deg); width:170px; }.art-coins { color:#e5a42d; font-size:2rem; font-weight:900; letter-spacing:-10px; line-height:.4; position:absolute; right:82px; text-shadow:3px 3px #bd7917; top:190px; transform:rotate(7deg); }.art-shield { background:#edf6ff; border-radius:50%; bottom:12px; color:#236ee8; font-size:2.3rem; height:74px; left:0; line-height:74px; position:absolute; text-align:center; width:74px; }.home-search-wrap { margin-top:1rem; }.home-search { align-items:center; background:#fff; border:1px solid #dbe6f3; border-radius:17px; box-shadow:0 10px 24px rgba(29,55,88,.09); display:grid; gap:.8rem; grid-template-columns:auto 1fr auto; padding:.65rem .7rem .65rem 1.2rem; }.home-search>span { color:#1f70e8; font-size:1.5rem; }.home-search input { border:0; color:#183250; font:inherit; font-weight:650; outline:0; padding:.75rem 0; }.home-search .btn { border-radius:11px; min-width:94px; }.home-chips { display:flex; flex-wrap:wrap; gap:.45rem; padding:.8rem .4rem 0; }.home-chips button { background:#fff; border:1px solid #dbe6f2; border-radius:99px; color:#526b89; cursor:pointer; font-weight:750; padding:.4rem .72rem; }.home-chips button:hover { border-color:#8fb7ff; color:#176bea; }.home-section,.search-results { margin-top:2.65rem; }.section-title,.result-head { align-items:center; display:flex; justify-content:space-between; gap:1rem; }.section-title h2,.search-result-title h2 { color:#183250; font-size:1.35rem; letter-spacing:-.035em; margin:0; }.section-title a,.result-head a { color:#246fe5; font-size:.85rem; font-weight:850; text-decoration:none; }.category-grid { display:grid; gap:.75rem; grid-template-columns:repeat(7,minmax(0,1fr)); margin-top:1rem; }.category-card { align-items:center; background:#fff; border:1px solid #dce6f2; border-radius:16px; color:#203854; display:flex; flex-direction:column; gap:.8rem; min-height:145px; justify-content:center; text-align:center; text-decoration:none; transition:.18s ease; }.category-card:hover,.home-feature:hover,.mini-card:hover { border-color:#9dc0ff; box-shadow:0 12px 25px rgba(38,100,220,.09); transform:translateY(-2px); }.category-card span { align-items:center; background:#eef5ff; border-radius:50%; color:#1e6ce4; display:flex; font-size:1.75rem; height:58px; justify-content:center; width:58px; }.category-card strong { font-size:.9rem; }.feature-grid { display:grid; gap:1rem; grid-template-columns:repeat(3,minmax(0,1fr)); }.home-feature { align-items:center; background:linear-gradient(135deg,#eef5ff,#fafcff); border:1px solid #dce6f2; border-radius:16px; color:inherit; display:flex; gap:1rem; min-height:114px; padding:1rem 1.2rem; text-decoration:none; transition:.18s ease; }.home-feature:nth-child(2){background:linear-gradient(135deg,#eef9f8,#fbffff)}.home-feature:nth-child(3){background:linear-gradient(135deg,#f3f2ff,#fbfbff)}.home-feature>span { align-items:center; background:#fff; border-radius:14px; color:#236ee8; display:flex; font-size:1.7rem; height:52px; justify-content:center; width:52px; }.home-feature h2 { color:#183250; font-size:1.05rem; margin:0 0 .35rem; }.home-feature p { color:#61748c; font-size:.82rem; line-height:1.5; margin:0; }.home-feature b { color:#1d69e2; font-size:1.7rem; margin-left:auto; }.trust-bar { background:#f4f7fb; border-radius:12px; color:#536a84; display:flex; flex-wrap:wrap; font-size:.8rem; font-weight:700; gap:1.5rem 3rem; justify-content:center; margin-top:2rem; padding:1rem; }.search-result-title p { color:#1d70e8; font-size:.8rem; font-weight:900; letter-spacing:.08em; margin:0 0 .35rem; }.result-grid { display:grid; gap:1.1rem; grid-template-columns:repeat(2,minmax(0,1fr)); margin-top:1.1rem; }.result-section { background:#f8fbff; border:1px solid #dce6f2; border-radius:16px; padding:1rem; }.result-head h3 { color:#183250; font-size:1.05rem; margin:0; }.result-cards { display:grid; gap:.65rem; margin-top:.8rem; }.mini-card { background:#fff; border:1px solid #e0e8f2; border-radius:11px; color:inherit; cursor:pointer; display:grid; gap:.3rem; padding:.75rem .8rem; text-align:left; text-decoration:none; transition:.18s ease; }.mini-card span { color:#177867; font-size:.72rem; font-weight:850; }.mini-card strong { color:#1a3554; font-size:.9rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.mini-card small { color:#74869a; font-size:.75rem; }.loan-mini { font:inherit; width:100%; }.video-mini { grid-template-columns:72px 1fr; }.video-mini img { border-radius:7px; grid-row:span 2; height:48px; object-fit:cover; width:72px; }.result-message { background:#fff; border-radius:10px; color:#75879a; font-size:.84rem; margin:.8rem 0 0; padding:.8rem; }@media (max-width:980px){.home-hero{grid-template-columns:1fr;padding:2.6rem}.hero-art{display:none}.category-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.result-grid{grid-template-columns:1fr}}@media (max-width:620px){.home-page{padding-top:1rem}.home-hero{border-radius:18px;padding:2.2rem 1.35rem}.hero-copy h1{font-size:2.55rem}.home-search{grid-template-columns:auto 1fr}.home-search .btn{grid-column:1/-1;width:100%}.category-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.feature-grid{grid-template-columns:1fr}.trust-bar{align-items:start;flex-direction:column;gap:.65rem}.section-title{align-items:start;flex-direction:column}.home-section,.search-results{margin-top:2rem}}
</style>
