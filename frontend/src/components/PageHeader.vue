<script setup>
defineProps({
  eyebrow: { type: String, default: "" },
  title: { type: String, required: true },
  description: { type: String, default: "" }
});
</script>

<template>
  <header class="page-header">
    <h1>{{ title }}</h1>
    <p v-if="description" class="page-header__description">{{ description }}</p>
  </header>
</template>

<style scoped>
.page-header {
  max-width: 1180px;
  margin: 0 auto 1.05rem;
  padding-top: clamp(1.1rem, 2vw, 1.65rem);
}

.page-header h1 {
  margin: 0;
  color: #0f2748;
  font-size: clamp(2rem, 3.2vw, 2.45rem);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: 0;
}

.page-header__description {
  max-width: 760px;
  margin: .55rem 0 0;
  color: #657083;
  font-size: .96rem;
  font-weight: 600;
  line-height: 1.62;
}

@media (max-width: 640px) {
  .page-header {
    padding-top: .95rem;
    margin-bottom: .85rem;
  }

  .page-header h1 {
    font-size: 1.85rem;
  }

  .page-header__description {
    font-size: .9rem;
  }
}
</style>
