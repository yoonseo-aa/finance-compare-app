<script setup>
import { computed } from "vue";

const props = defineProps({
  elapsedSeconds: { type: Number, default: 0 },
  title: { type: String, default: "AI 뉴스 추천 중" }
});

const message = computed(() => {
  if (props.elapsedSeconds >= 6) return "조금만 더 기다려주세요. 외부 API 응답을 기다리는 중입니다.";
  if (props.elapsedSeconds >= 3) return "AI가 검색어와 관련성이 높은 기사를 선별하고 있습니다.";
  return "뉴스 후보를 불러오고 있습니다.";
});
</script>

<template>
  <div class="ai-news-loading" role="status" aria-live="polite">
    <div class="pulse-dots" aria-hidden="true"><i></i><i></i><i></i></div>
    <div><strong>{{ title }}</strong><p>{{ message }}</p><small>검색 경과 {{ elapsedSeconds }}초</small></div>
  </div>
</template>

<style scoped>
.ai-news-loading{align-items:center;background:#fff;border:1px solid #cfe0f5;border-radius:14px;box-shadow:0 8px 20px rgba(29,55,88,.06);display:flex;gap:1rem;padding:1rem 1.15rem}.pulse-dots{display:flex;gap:.3rem}.pulse-dots i{animation:pulse 1.15s ease-in-out infinite;background:#2372e8;border-radius:50%;height:10px;width:10px}.pulse-dots i:nth-child(2){animation-delay:.16s}.pulse-dots i:nth-child(3){animation-delay:.32s}.ai-news-loading strong{color:#183250}.ai-news-loading p{color:#647891;font-size:.84rem;margin:.3rem 0}.ai-news-loading small{color:#1f70e8;font-weight:800}@keyframes pulse{0%,100%{opacity:.28;transform:translateY(0)}50%{opacity:1;transform:translateY(-4px)}}
</style>
