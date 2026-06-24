<script setup>
import { ref } from "vue";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";

const query = ref("");
const videos = ref([]);
const loading = ref(false);
const error = ref("");

async function search() {
  loading.value = true;
  error.value = "";
  try {
    const data = await apiFetch(`/videos/?q=${encodeURIComponent(query.value)}`);
    videos.value = data.results;
    error.value = data.error || "";
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>관심 종목 검색</h1>
      <p>YouTube Data API로 금융/종목 관련 영상을 찾습니다.</p>
    </div>
    <form class="filter-bar two" @submit.prevent="search">
      <input v-model="query" placeholder="예: 삼성전자, 금리 전망, ETF">
      <button class="btn primary" type="submit">검색</button>
    </form>
    <StatusBlock :loading="loading" :error="error" :empty="query && !loading && !videos.length ? '검색 결과가 없습니다.' : ''" />
    <div class="card-grid">
      <RouterLink
        v-for="video in videos"
        :key="video.video_id"
        class="video-card"
        :to="{ name: 'video-detail', params: { id: video.video_id }, query: { title: video.title, channel: video.channel, published_at: video.published_at } }"
      >
        <img :src="video.thumbnail" alt="">
        <div>
          <h3>{{ video.title }}</h3>
          <p>{{ video.channel }} · {{ video.published_at }}</p>
        </div>
      </RouterLink>
    </div>
  </main>
</template>
