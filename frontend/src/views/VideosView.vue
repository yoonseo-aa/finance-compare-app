<script setup>
import { onBeforeUnmount, ref } from "vue";

import { apiFetch } from "../api/client";
import AiNewsLoading from "../components/AiNewsLoading.vue";

const query = ref("");
const searchedQuery = ref("");
const news = ref([]);
const videos = ref([]);
const newsError = ref("");
const videoError = ref("");
const loading = ref(false);
const isNewsLoading = ref(false);
const newsElapsedSeconds = ref(0);
let newsTimer = null;
let activeNewsRequest = 0;
const suggestions = ["삼성전자", "금리 인하", "ETF", "환율", "미국 증시", "2차전지"];

function cleanText(value = "") {
  const element = document.createElement("textarea");
  element.innerHTML = value;
  return element.value.replace(/<[^>]*>/g, "");
}

async function search(value = query.value) {
  const keyword = value.trim();
  if (!keyword) return;
  query.value = keyword;
  searchedQuery.value = keyword;
  loading.value = true;
  isNewsLoading.value = true;
  newsElapsedSeconds.value = 0;
  const requestId = ++activeNewsRequest;
  if (newsTimer) clearInterval(newsTimer);
  newsTimer = setInterval(() => { newsElapsedSeconds.value += 1; }, 1000);
  newsError.value = "";
  videoError.value = "";
  const newsRequest = apiFetch(`/search/news/?query=${encodeURIComponent(keyword)}`).then(data => {
    if (requestId !== activeNewsRequest) return;
    news.value = (data.results || []).slice(0, 4); newsError.value = data.error || "";
  }).catch(err => { if (requestId === activeNewsRequest) newsError.value = err.message || "뉴스를 불러오지 못했습니다."; }).finally(() => {
    if (requestId !== activeNewsRequest) return;
    isNewsLoading.value = false; if (newsTimer) { clearInterval(newsTimer); newsTimer = null; }
  });
  const videoRequest = apiFetch(`/videos/?q=${encodeURIComponent(keyword)}`).then(data => {
    videos.value = (data.results || []).slice(0, 4); videoError.value = data.error || "";
  }).catch(err => { videoError.value = err.message || "영상을 불러오지 못했습니다."; });
  await Promise.allSettled([newsRequest, videoRequest]);
  loading.value = false;
}

onBeforeUnmount(() => { if (newsTimer) clearInterval(newsTimer); });

function youtubeSearchUrl() {
  return `https://www.youtube.com/results?search_query=${encodeURIComponent(searchedQuery.value)}`;
}
</script>

<template>
  <main class="container content-search-page">
    <section class="search-hero">
      <p class="search-eyebrow">FINPICK CONTENT SEARCH</p>
      <h1>관심 종목 검색</h1>
      <p>금융/종목 키워드를 검색하면 관련 뉴스와 영상을 한 번에 보여드립니다.</p>
      <form class="content-search-form" @submit.prevent="search()">
        <span aria-hidden="true">⌕</span><input v-model="query" placeholder="예: 삼성전자, 금리 인하, ETF, 미국 증시"><button class="btn primary" :disabled="loading">{{ loading ? "검색 중" : "검색" }}</button>
      </form>
      <div class="suggestion-chips"><button v-for="word in suggestions" :key="word" type="button" @click="search(word)">{{ word }}</button></div>
    </section>

    <section v-if="!searchedQuery" class="search-empty-state">
      <span>⌕</span><h2>관심 있는 금융 키워드를 검색해보세요.</h2><p>뉴스와 유튜브 영상을 한 번에 모아볼 수 있습니다.</p>
    </section>

    <template v-else>
      <section class="content-result-section">
        <div class="result-section-head"><div><p>추천 뉴스</p><h2>“{{ searchedQuery }}” 관련 뉴스</h2></div><span>{{ news.length }}개 결과</span></div>
        <AiNewsLoading v-if="isNewsLoading" :elapsed-seconds="newsElapsedSeconds" />
        <p v-else-if="newsError" class="content-error">{{ newsError }}</p>
        <div v-else-if="news.length" class="news-grid">
          <a v-for="article in news" :key="article.url" class="news-card" :href="article.url" target="_blank" rel="noopener noreferrer"><span>{{ cleanText(article.source) }}</span><h3>{{ cleanText(article.title) }}</h3><p>{{ cleanText(article.description) }}</p><small>{{ article.published_at }}</small><em>{{ article.reason }}</em></a>
        </div>
        <p v-else-if="!loading" class="no-result">검색 결과가 없습니다. 다른 키워드로 검색해보세요.</p>
      </section>

      <section class="content-result-section">
        <div class="result-section-head"><div><p>관련 유튜브 영상</p><h2>금융 콘텐츠</h2></div><a :href="youtubeSearchUrl()" target="_blank" rel="noopener noreferrer">더보기 →</a></div>
        <p v-if="videoError" class="content-error">{{ videoError }}</p>
        <div v-if="videos.length" class="video-search-grid">
          <a v-for="video in videos" :key="video.video_id" class="video-search-card" :href="`https://www.youtube.com/watch?v=${video.video_id}`" target="_blank" rel="noopener noreferrer"><img :src="video.thumbnail" alt=""><div><h3>{{ cleanText(video.title) }}</h3><p>{{ cleanText(video.channel) }} · {{ video.published_at }}</p></div></a>
        </div>
        <p v-else-if="!loading && !videoError" class="no-result">검색 결과가 없습니다. 다른 키워드로 검색해보세요.</p>
      </section>
    </template>
  </main>
</template>

<style scoped>
.content-search-page { min-height: calc(100vh - 72px); padding-top: 3rem; padding-bottom: 4rem; }.search-hero { max-width: 900px; margin: 0 auto 2rem; text-align: center; }.search-eyebrow,.result-section-head p { color: #1970eb; font-size: .8rem; font-weight: 900; letter-spacing: .08em; margin: 0; }.search-hero h1 { color: #102a4b; font-size: clamp(2rem,4vw,3rem); letter-spacing: -.05em; margin: .5rem 0; }.search-hero > p:not(.search-eyebrow) { color: #677a92; }.content-search-form { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: .65rem; border: 1px solid #cadcf4; border-radius: 16px; background: #fff; box-shadow: 0 12px 28px rgba(29,55,88,.08); margin-top: 1.5rem; padding: .55rem .6rem .55rem 1rem; }.content-search-form > span { color: #2874ed; font-size: 1.35rem; }.content-search-form input { border: 0; color: #183250; font: inherit; outline: 0; padding: .7rem 0; }.content-search-form .btn { min-width: 86px; border-radius: 10px; }.suggestion-chips { display: flex; justify-content: center; flex-wrap: wrap; gap: .5rem; margin-top: .9rem; }.suggestion-chips button { border: 1px solid #d8e4f1; border-radius: 999px; background: #fff; color: #486079; cursor: pointer; font-weight: 750; padding: .4rem .72rem; }.suggestion-chips button:hover { border-color: #91b9ff; color: #176bea; }.search-empty-state { display: grid; justify-items: center; border: 1px dashed #ccdaeb; border-radius: 18px; background: #fff; color: #6c7f96; padding: 4rem 1rem; text-align: center; }.search-empty-state > span { color: #2874ed; font-size: 2rem; }.search-empty-state h2 { color: #1a3554; margin: .6rem 0 .3rem; }.search-empty-state p { margin: 0; }.content-result-section { margin-top: 2rem; }.result-section-head { display: flex; justify-content: space-between; align-items: end; gap: 1rem; margin-bottom: .9rem; }.result-section-head h2 { color: #183250; font-size: 1.3rem; margin: .28rem 0 0; }.result-section-head > span,.result-section-head > a { color: #246fe5; font-weight: 850; text-decoration: none; }.news-grid,.video-search-grid { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: .9rem; }.news-card,.video-search-card { border: 1px solid #dce6f2; border-radius: 14px; background: #fff; box-shadow: 0 7px 17px rgba(29,55,88,.04); color: inherit; overflow: hidden; padding: 1rem; text-decoration: none; transition: .18s ease; }.news-card:hover,.video-search-card:hover { border-color: #9fc2ff; box-shadow: 0 14px 24px rgba(37,99,235,.09); transform: translateY(-2px); }.news-card > span { color: #1970eb; font-size: .76rem; font-weight: 900; }.news-card h3,.video-search-card h3 { color: #183250; display: -webkit-box; font-size: 1rem; line-height: 1.45; margin: .55rem 0; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }.news-card p { color: #6b7d93; display: -webkit-box; font-size: .83rem; line-height: 1.55; margin: 0; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 3; }.news-card small { color: #8a99aa; display: block; margin-top: .8rem; }.news-card em { color: #168260; display: block; font-size: .72rem; font-style: normal; margin-top: .45rem; }.video-search-card { padding: 0; }.video-search-card img { aspect-ratio: 16 / 9; background: #e8eff7; display: block; object-fit: cover; width: 100%; }.video-search-card div { padding: .85rem; }.video-search-card h3 { margin: 0 0 .45rem; }.video-search-card p { color: #6b7d93; font-size: .78rem; margin: 0; }.content-error,.no-result { border-radius: 10px; background: #fff7f7; color: #a84646; padding: .8rem; }.no-result { background: #f5f8fc; color: #6b7d93; }@media (max-width:980px){.news-grid,.video-search-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}@media (max-width:620px){.content-search-page{padding-top:1.75rem}.content-search-form{grid-template-columns:auto 1fr}.content-search-form .btn{grid-column:1/-1;width:100%}.news-grid,.video-search-grid{grid-template-columns:1fr}.result-section-head{align-items:start;flex-direction:column;}}
</style>
