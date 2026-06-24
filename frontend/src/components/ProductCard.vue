<script setup>
defineProps({
  product: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <RouterLink class="product-card" :to="`/products/${product.id}`">
    <span>{{ product.product_type_label }}</span>
    <h3>{{ product.name }}</h3>
    <p>{{ product.bank_name }}</p>
    <strong>최고 {{ product.best_rate || 0 }}%</strong>
  </RouterLink>
</template>
