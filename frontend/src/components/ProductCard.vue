<script setup>
import { computed } from "vue";

const props = defineProps({
  product: { type: Object, required: true },
  isJoined: Boolean
});

const productType = computed(() => props.product.product_type_label || props.product.product_type || "금융상품");
const termText = computed(() => props.product.options?.length ? `${Math.max(...props.product.options.map(option => Number(option.save_term || 0)))}개월까지` : "가입기간 확인");
const conditionText = computed(() => props.product.special_condition || props.product.etc_note || "우대 조건을 확인해보세요");
</script>

<template>
  <article class="product-card-local">
    <div class="product-card-top-local">
      <span class="type-badge-local">{{ productType }}</span>
      <RouterLink class="product-interest-local" :class="{ active: isJoined }" :to="`/products/${product.id}`" aria-label="관심상품 상세보기">
        {{ isJoined ? "♥" : "♡" }}
      </RouterLink>
    </div>
    <RouterLink class="product-card-body-local" :to="`/products/${product.id}`">
      <h3>{{ product.name }}</h3>
      <p class="product-bank-local">{{ product.bank_name }}</p>
      <div class="product-meta-local">
        <span>▣ {{ termText }}</span>
        <span>☆ {{ conditionText }}</span>
      </div>
      <div class="product-rate-local">
        <strong>최고 {{ product.best_rate || 0 }}%</strong>
        <span>상품 상세보기 <b>›</b></span>
      </div>
    </RouterLink>
  </article>
</template>

<style scoped>
.product-card-local { display: grid; gap: .85rem; min-height: 190px; border: 1px solid #dce6f2; border-radius: 14px; background: #fff; box-shadow: 0 6px 16px rgba(31, 59, 94, .045); padding: 1rem 1.05rem; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
.product-card-local:hover { border-color: #9ec2ff; box-shadow: 0 13px 24px rgba(37, 99, 235, .09); transform: translateY(-2px); }
.product-card-top-local { display: flex; align-items: center; justify-content: space-between; }
.type-badge-local { border-radius: 6px; background: #dcf5ed; color: #138261; font-size: .73rem; font-weight: 900; padding: .28rem .48rem; }
.product-interest-local { color: #637b98; font-size: 1.55rem; line-height: 1; text-decoration: none; }
.product-interest-local.active { color: #2670eb; }
.product-card-body-local { display: grid; min-width: 0; color: inherit; text-decoration: none; }
.product-card-body-local h3 { overflow: hidden; color: #163251; font-size: 1.08rem; letter-spacing: -.025em; margin: 0; text-overflow: ellipsis; white-space: nowrap; }
.product-bank-local { color: #657991; font-size: .82rem; font-weight: 750; margin: .28rem 0 .7rem; }
.product-meta-local { display: grid; gap: .4rem; border-bottom: 1px dashed #dce6f0; color: #6c7f96; font-size: .76rem; line-height: 1.35; padding-bottom: .8rem; }
.product-meta-local span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.product-rate-local { display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding-top: .75rem; }
.product-rate-local strong { color: #176be9; font-size: 1.22rem; letter-spacing: -.035em; }
.product-rate-local span { border: 0; background: transparent; color: #1f6ee8; font-size: .78rem; font-weight: 850; padding: 0; }
.product-rate-local b { font-size: 1.05rem; }
</style>
