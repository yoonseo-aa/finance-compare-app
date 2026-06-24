<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import AiNewsLoading from "../components/AiNewsLoading.vue";
import { useCommunityStore } from "../stores/community";

const route = useRoute();
const router = useRouter();
const community = useCommunityStore();
const input = ref("");
const keyword = ref("");
const loading = ref(false);
const isNewsLoading = ref(false);
const newsElapsedSeconds = ref(0);
let newsTimer = null;
let activeNewsRequest = 0;
const deposits = ref([]);
const loans = ref([]);
const news = ref([]);
const videos = ref([]);
const errors = ref({ products: "", news: "", videos: "" });
const suggestions = ["예금", "적금", "주택담보대출", "전세자금대출", "삼성전자", "금리 전망", "ETF"];

const communityPosts = computed(() => {
  const term = keyword.value.toLowerCase();
  if (!term) return [];
  return community.posts.filter(post => [post.title, post.content, post.author, ...(post.tags || [])]
    .join(" ").toLowerCase().includes(term)).slice(0, 4);
});
const hasResults = computed(() => deposits.value.length || loans.value.length || news.value.length || videos.value.length || communityPosts.value.length);

function cleanText(value = "") {
  const area = document.createElement("textarea");
  area.innerHTML = value;
  return area.value.replace(/<[^>]*>/g, "");
}

async function loadSearch(value) {
  const term = String(value || "").trim();
  keyword.value = term;
  input.value = term;
  deposits.value = []; loans.value = []; news.value = []; videos.value = [];
  errors.value = { products: "", news: "", videos: "" };
  if (!term) return;
  loading.value = true;
  isNewsLoading.value = true;
  newsElapsedSeconds.value = 0;
  const requestId = ++activeNewsRequest;
  if (newsTimer) clearInterval(newsTimer);
  newsTimer = setInterval(() => { newsElapsedSeconds.value += 1; }, 1000);
  apiFetch(`/search/news/?query=${encodeURIComponent(term)}`).then(data => {
    if (requestId !== activeNewsRequest) return;
    news.value = (data.results || []).slice(0, 4);
    errors.value.news = data.error || "";
  }).catch(() => { if (requestId === activeNewsRequest) errors.value.news = "뉴스를 불러오지 못했습니다."; }).finally(() => {
    if (requestId !== activeNewsRequest) return;
    isNewsLoading.value = false;
    if (newsTimer) { clearInterval(newsTimer); newsTimer = null; }
  });
  const [productResult, loanResult, videoResult] = await Promise.allSettled([
    apiFetch(`/products/?q=${encodeURIComponent(term)}`),
    apiFetch(`/loans/?type=all&q=${encodeURIComponent(term)}`),
    apiFetch(`/videos/?q=${encodeURIComponent(term)}`)
  ]);
  deposits.value = productResult.status === "fulfilled" ? productResult.value.slice(0, 4) : [];
  loans.value = loanResult.status === "fulfilled" ? (loanResult.value.results || []).slice(0, 4) : [];
  videos.value = videoResult.status === "fulfilled" ? (videoResult.value.results || []).slice(0, 4) : [];
  errors.value = {
    products: productResult.status === "rejected" ? "상품을 불러오지 못했습니다." : loanResult.status === "rejected" ? "일부 대출 결과를 불러오지 못했습니다." : "",
    news: "",
    videos: videoResult.status === "rejected" ? "영상을 불러오지 못했습니다." : ""
  };
  loading.value = false;
}

function submitSearch(value = input.value) {
  const term = value.trim();
  if (!term) return;
  router.push({ name: "search", query: { q: term } });
}

function loanMore() {
  router.push({ path: "/products", query: { group: "loan", type: "credit", q: keyword.value } });
}

watch(() => route.query.q, value => loadSearch(value), { immediate: true });
onBeforeUnmount(() => { if (newsTimer) clearInterval(newsTimer); });
</script>

<template>
  <main class="container search-page">
    <header class="search-header"><p>FINPICK SEARCH</p><h1>통합 검색</h1><span>상품, 뉴스, 영상, 커뮤니티 글을 한 번에 검색합니다.</span></header>
    <form class="search-form" @submit.prevent="submitSearch()"><span aria-hidden="true">⌕</span><input v-model="input" placeholder="상품명, 은행명, 종목, 금융 키워드 검색"><button class="btn primary" :disabled="loading">{{ loading ? "검색 중" : "검색" }}</button></form>
    <div class="chips"><button v-for="word in suggestions" :key="word" type="button" @click="submitSearch(word)">{{ word }}</button></div>

    <section v-if="!keyword" class="empty"><span>⌕</span><h2>검색어를 입력해 상품, 뉴스, 영상, 커뮤니티 글을 찾아보세요.</h2></section>
    <template v-else>
      <div class="result-title"><p>SEARCH RESULTS</p><h2>“{{ keyword }}” 검색 결과</h2></div>
      <p v-if="loading" class="loading">각 영역의 결과를 검색 중입니다...</p>
      <section v-if="!loading && !hasResults && !errors.products && !errors.news && !errors.videos" class="empty"><span>⌕</span><h2>검색 결과가 없습니다.</h2><p>다른 키워드로 검색해보세요.</p></section>
      <div v-else class="sections">
        <section class="result-section"><header><div><p>FINANCIAL PRODUCTS</p><h2>관련 금융 상품</h2></div><RouterLink :to="`/products?q=${encodeURIComponent(keyword)}`">상품 더보기 →</RouterLink></header><p v-if="errors.products" class="message">{{ errors.products }}</p><div v-else-if="deposits.length || loans.length" class="card-grid"><RouterLink v-for="item in deposits" :key="item.id" class="result-card" :to="`/products/${item.id}`"><span>{{ item.product_type_label || item.product_type }}</span><h3>{{ item.name }}</h3><p>{{ item.bank_name }}</p><strong>최고 {{ Number(item.max_rate || 0).toFixed(2) }}%</strong><em>상품 상세보기 →</em></RouterLink><RouterLink v-for="item in loans" :key="`${item.loan_type}-${item.product_code}`" class="result-card loan-card" :to="{ name: 'loan-detail', params: { type: item.loan_type, code: item.product_code } }"><span>{{ item.loan_type_label }}</span><h3>{{ item.name }}</h3><p>{{ item.bank_name }}</p><strong>{{ item.rate_min ? `최저 ${item.rate_min.toFixed(2)}%` : "금리 정보 확인" }}</strong><em>상품 상세보기 →</em></RouterLink></div><p v-else class="message">관련 상품이 없습니다.</p></section>
        <section class="result-section"><header><div><p>NEWS</p><h2>관련 뉴스 기사</h2></div><RouterLink :to="`/videos?q=${encodeURIComponent(keyword)}`">뉴스 더보기 →</RouterLink></header><AiNewsLoading v-if="isNewsLoading" :elapsed-seconds="newsElapsedSeconds" /><p v-else-if="errors.news" class="message">{{ errors.news }}</p><div v-else-if="news.length" class="card-grid"><a v-for="item in news" :key="item.url" class="result-card" :href="item.url" target="_blank" rel="noopener noreferrer"><span>{{ cleanText(item.source) }} <b v-if="item.reason">AI 추천</b></span><h3>{{ cleanText(item.title) }}</h3><p>{{ cleanText(item.description) }}</p><small>{{ item.published_at }}</small><em v-if="item.reason">{{ item.reason }}</em></a></div><p v-else class="message">관련 뉴스가 없습니다.</p></section>
        <section class="result-section"><header><div><p>VIDEOS</p><h2>관련 유튜브 영상</h2></div><a :href="`https://www.youtube.com/results?search_query=${encodeURIComponent(keyword)}`" target="_blank" rel="noopener noreferrer">영상 더보기 →</a></header><p v-if="errors.videos" class="message">{{ errors.videos }}</p><div v-else-if="videos.length" class="card-grid"><a v-for="item in videos" :key="item.video_id" class="result-card video-card" :href="`https://www.youtube.com/watch?v=${item.video_id}`" target="_blank" rel="noopener noreferrer"><img :src="item.thumbnail" alt=""><div><h3>{{ cleanText(item.title) }}</h3><p>{{ cleanText(item.channel) }}</p><small>{{ item.published_at }}</small></div></a></div><p v-else class="message">관련 영상이 없습니다.</p></section>
        <section class="result-section"><header><div><p>COMMUNITY</p><h2>관련 커뮤니티 글</h2></div><RouterLink :to="`/community?q=${encodeURIComponent(keyword)}`">커뮤니티 더보기 →</RouterLink></header><div v-if="communityPosts.length" class="card-grid"><RouterLink v-for="post in communityPosts" :key="post.id" class="result-card" :to="`/community/${post.id}`"><span>{{ post.category }}</span><h3>{{ post.title }}</h3><p>{{ post.content }}</p><small>{{ post.author }} · {{ post.createdAt }} · 댓글 {{ post.comments }}</small></RouterLink></div><p v-else class="message">관련 커뮤니티 글이 없습니다.</p></section>
      </div>
    </template>
  </main>
</template>

<style scoped>
.search-page{min-height:calc(100vh - 72px);padding:3rem 0 4.5rem}.search-header{text-align:center}.search-header>p,.result-title>p,.result-section header p{color:#196fe9;font-size:.78rem;font-weight:900;letter-spacing:.1em;margin:0}.search-header h1{color:#112d4f;font-size:clamp(2rem,4vw,3rem);letter-spacing:-.06em;margin:.5rem 0}.search-header span{color:#6b7d93}.search-form{align-items:center;background:#fff;border:1px solid #cbdcf2;border-radius:17px;box-shadow:0 12px 27px rgba(29,55,88,.08);display:grid;gap:.7rem;grid-template-columns:auto 1fr auto;margin:1.6rem auto 0;max-width:920px;padding:.6rem .65rem .6rem 1.05rem}.search-form>span{color:#216fea;font-size:1.45rem}.search-form input{border:0;color:#1a3657;font:inherit;font-weight:700;outline:0;padding:.7rem 0}.search-form .btn{border-radius:10px;min-width:88px}.chips{display:flex;flex-wrap:wrap;gap:.45rem;justify-content:center;margin-top:.8rem}.chips button{background:#fff;border:1px solid #dce6f2;border-radius:99px;color:#597089;cursor:pointer;font-weight:750;padding:.38rem .7rem}.result-title{margin-top:2.7rem}.result-title h2{color:#183250;font-size:1.5rem;letter-spacing:-.04em;margin:.35rem 0}.loading,.message{background:#f4f8fd;border-radius:10px;color:#63778f;margin:.85rem 0 0;padding:.85rem}.sections{display:grid;gap:1.6rem;margin-top:1.15rem}.result-section{background:#f8fbff;border:1px solid #dce6f2;border-radius:18px;padding:1.2rem}.result-section header{align-items:end;display:flex;gap:1rem;justify-content:space-between}.result-section header h2{color:#183250;font-size:1.2rem;margin:.3rem 0 0}.result-section header>a{color:#246fe5;font-size:.84rem;font-weight:850;text-decoration:none}.card-grid{display:grid;gap:.8rem;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:1rem}.result-card{background:#fff;border:1px solid #dce6f2;border-radius:13px;color:inherit;display:flex;flex-direction:column;gap:.42rem;min-height:154px;padding:.9rem;text-align:left;text-decoration:none;transition:.18s ease}.result-card:hover{border-color:#9bc0ff;box-shadow:0 12px 24px rgba(38,100,220,.09);transform:translateY(-2px)}.result-card>span{color:#16816f;font-size:.72rem;font-weight:900}.result-card span b{background:#eaf3ff;border-radius:99px;color:#206fe8;margin-left:.25rem;padding:.18rem .35rem}.result-card h3{color:#193554;display:-webkit-box;font-size:.95rem;line-height:1.45;margin:0;overflow:hidden;-webkit-box-orient:vertical;-webkit-line-clamp:2}.result-card p{color:#6a7d94;display:-webkit-box;font-size:.8rem;line-height:1.45;margin:0;overflow:hidden;-webkit-box-orient:vertical;-webkit-line-clamp:2}.result-card strong{color:#176ce7;margin-top:auto}.result-card em,.result-card small{color:#75889e;font-size:.74rem;font-style:normal}.loan-card{cursor:pointer;font:inherit;width:100%}.video-card{padding:0}.video-card img{aspect-ratio:16/9;background:#eaf0f7;border-radius:12px 12px 0 0;object-fit:cover;width:100%}.video-card div{display:flex;flex:1;flex-direction:column;gap:.42rem;padding:.85rem}.empty{align-items:center;background:#fff;border:1px dashed #cbd9e9;border-radius:18px;color:#6d8097;display:flex;flex-direction:column;gap:.4rem;justify-content:center;margin-top:2rem;min-height:240px;text-align:center}.empty span{color:#2473e8;font-size:2rem}.empty h2{color:#1a3656;font-size:1.15rem;margin:0}.empty p{margin:0}@media(max-width:980px){.card-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.search-page{padding-top:1.75rem}.search-form{grid-template-columns:auto 1fr}.search-form .btn{grid-column:1/-1;width:100%}.result-section header{align-items:start;flex-direction:column}.card-grid{grid-template-columns:1fr}}
</style>
