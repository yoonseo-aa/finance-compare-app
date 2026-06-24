<script setup>
defineProps({
  loading: Boolean,
  error: String,
  empty: String
});
</script>

<template>
  <div v-if="loading" class="status-block">불러오는 중입니다.</div>
  <div v-else-if="error" class="status-block warning">{{ error }}</div>
  <div v-else-if="empty" class="status-block">{{ empty }}</div>
</template>
