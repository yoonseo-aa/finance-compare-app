<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <main class="container">
    <RouterLink class="back-link" to="/videos">검색</RouterLink>
    <section class="video-detail">
      <div class="video-frame">
        <iframe :src="`https://www.youtube.com/embed/${route.params.id}`" :title="route.query.title || '관심 종목 영상'" allowfullscreen></iframe>
      </div>
      <h1>{{ route.query.title || "관심 종목 영상" }}</h1>
      <p class="muted">{{ route.query.channel || "YouTube" }} <span v-if="route.query.published_at">· {{ route.query.published_at }}</span></p>
    </section>
  </main>
</template>
