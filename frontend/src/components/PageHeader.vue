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
  position: relative;
  width: 100%;
  max-width: none;
  margin: 0 0 1.05rem;
  padding-top: 0;
  text-align: left;
}

.page-header::before {
  content: "";
  display: block;
  width: 42px;
  height: 3px;
  margin-bottom: .7rem;
  border-radius: 999px;
  background: linear-gradient(90deg, #2f80ed 0%, #7db5ff 100%);
}

.page-header h1 {
  margin: 0;
  color: #102b50;
  font-size: clamp(2rem, 3.2vw, 2.45rem);
  font-weight: 900;
  line-height: 1.12;
  letter-spacing: -.045em;
}

.page-header__description {
  max-width: 760px;
  margin: .45rem 0 0;
  color: #68788d;
  font-size: .95rem;
  font-weight: 650;
  line-height: 1.55;
}

@media (max-width: 640px) {
  .page-header {
    margin-bottom: .85rem;
  }

  .page-header::before {
    width: 34px;
    margin-bottom: .55rem;
  }

  .page-header h1 {
    font-size: 1.85rem;
  }

  .page-header__description {
    font-size: .9rem;
  }
}
</style>
