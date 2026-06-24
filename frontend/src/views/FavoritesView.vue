<script setup>
import { computed, onMounted, ref } from "vue";

import { apiFetch } from "../api/client";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const removingId = ref(null);
const error = ref("");
const favorites = computed(() => auth.user?.joined_products || []);

async function removeFavorite(productId) {
  removingId.value = productId;
  error.value = "";
  try {
    const user = await apiFetch(`/products/${productId}/join/`, { method: "DELETE" });
    auth.setUser(user);
  } catch (err) {
    error.value = err.message || "관심 상품을 해제하지 못했습니다.";
  } finally {
    removingId.value = null;
  }
}

onMounted(async () => {
  if (!auth.user) await auth.bootstrap();
});
</script>

<template>
  <main class="container favorites-page-local">
    <section class="favorites-hero-local">
      <div>
        <span>MY FINPICK</span>
        <h1>관심 목록</h1>
        <p>관심 목록에 추가한 예적금 상품을 한곳에서 확인합니다.</p>
      </div>
      <RouterLink class="btn ghost" to="/products">상품 둘러보기</RouterLink>
    </section>

    <p v-if="error" class="favorites-error-local">{{ error }}</p>

    <section v-if="favorites.length" class="favorite-grid-local">
      <article v-for="product in favorites" :key="product.id" class="favorite-card-local">
        <div class="favorite-card-top-local">
          <span class="favorite-type-local">{{ product.product_type_label }}</span>
          <button type="button" :disabled="removingId === product.id" @click="removeFavorite(product.id)">
            {{ removingId === product.id ? "해제 중" : "♥ 관심 해제" }}
          </button>
        </div>
        <h2>{{ product.name }}</h2>
        <p>{{ product.bank_name }}</p>
        <div class="favorite-card-bottom-local">
          <strong>최고 {{ product.best_rate || 0 }}%</strong>
          <RouterLink :to="`/products/${product.id}`">상품 상세보기 <span>›</span></RouterLink>
        </div>
      </article>
    </section>

    <section v-else class="favorites-empty-local">
      <span aria-hidden="true">♡</span>
      <h2>아직 관심 상품이 없습니다.</h2>
      <p>마음에 드는 예적금 상품을 관심 목록에 추가해보세요.</p>
      <RouterLink class="btn primary" to="/products">상품 둘러보기</RouterLink>
    </section>
  </main>
</template>

<style scoped>
.favorites-page-local { min-height: calc(100vh - 72px); padding-top: 2.8rem; padding-bottom: 4rem; }
.favorites-hero-local { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; }
.favorites-hero-local > div > span { color: #139e9a; font-size: .82rem; font-weight: 900; letter-spacing: .04em; }
.favorites-hero-local h1 { margin: .35rem 0; color: #102a4b; font-size: 2rem; letter-spacing: -.045em; }
.favorites-hero-local p { margin: 0; color: var(--muted); }
.favorite-grid-local { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.favorite-card-local { display: grid; min-height: 190px; border: 1px solid #dbe6f2; border-radius: 16px; background: #fff; box-shadow: 0 8px 20px rgba(29, 55, 88, .05); padding: 1.15rem; }
.favorite-card-top-local { display: flex; justify-content: space-between; align-items: start; }
.favorite-type-local { border-radius: 999px; background: #dcf5ed; color: #148260; font-size: .75rem; font-weight: 900; padding: .3rem .55rem; }
.favorite-card-top-local button { border: 0; background: transparent; color: #2b70e8; cursor: pointer; font-size: .78rem; font-weight: 850; }
.favorite-card-top-local button:disabled { color: #93a4b8; cursor: wait; }
.favorite-card-local h2 { align-self: end; margin: 1rem 0 .35rem; color: #183250; font-size: 1.12rem; letter-spacing: -.025em; }
.favorite-card-local > p { margin: 0; color: #6b7d93; font-size: .86rem; font-weight: 750; }
.favorite-card-bottom-local { display: flex; align-items: center; justify-content: space-between; border-top: 1px dashed #dbe5f0; margin-top: 1rem; padding-top: .85rem; }
.favorite-card-bottom-local strong { color: #176be9; font-size: 1.25rem; letter-spacing: -.04em; }
.favorite-card-bottom-local a { border: 1px solid #bdd3ff; border-radius: 8px; color: #246fe5; font-size: .78rem; font-weight: 850; padding: .38rem .55rem; text-decoration: none; }
.favorite-card-bottom-local a span { font-size: 1.1rem; }
.favorites-empty-local { display: grid; justify-items: center; gap: .65rem; border: 1px dashed #c6d8ed; border-radius: 18px; background: #fff; padding: 4rem 1rem; text-align: center; }
.favorites-empty-local > span { color: #2873ed; font-size: 2.4rem; }
.favorites-empty-local h2 { margin: 0; color: #183250; font-size: 1.25rem; }
.favorites-empty-local p { margin: 0; color: #6b7d93; }
.favorites-error-local { border: 1px solid #f1c6c6; border-radius: 10px; background: #fff6f6; color: #af3737; margin-bottom: 1rem; padding: .8rem 1rem; }
@media (max-width: 980px) { .favorite-grid-local { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .favorites-page-local { padding-top: 1.75rem; } .favorites-hero-local { align-items: start; flex-direction: column; } .favorite-grid-local { grid-template-columns: 1fr; } }
</style>
