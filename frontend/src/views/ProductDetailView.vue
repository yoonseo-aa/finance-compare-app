<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const product = ref(null);
const loading = ref(true);
const error = ref("");
const isJoined = computed(() => auth.user?.joined_products?.some(item => Number(item.id) === Number(route.params.id)));

async function toggleFavorite() {
  if (!auth.isAuthenticated) {
    router.push({ name: "login", query: { next: route.fullPath } });
    return;
  }
  const user = await apiFetch(`/products/${route.params.id}/join/`, {
    method: isJoined.value ? "DELETE" : "POST"
  });
  auth.setUser(user);
}

onMounted(async () => {
  try {
    product.value = await apiFetch(`/products/${route.params.id}/`);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="container">
    <StatusBlock :loading="loading" :error="error" />

    <section v-if="product" class="detail-layout">
      <article class="content-panel">
        <span class="badge">{{ product.product_type_label }}</span>
        <h1>{{ product.name }}</h1>
        <p class="muted">{{ product.bank_name }}</p>

        <dl class="info-list">
          <dt>가입 방법</dt>
          <dd>{{ product.join_way || "정보 없음" }}</dd>

          <dt>가입 대상</dt>
          <dd>{{ product.join_member || "정보 없음" }}</dd>

          <dt>우대 조건</dt>
          <dd>{{ product.special_condition || "정보 없음" }}</dd>

          <dt>기타 안내</dt>
          <dd>{{ product.etc_note || "정보 없음" }}</dd>
        </dl>

        <div class="detail-actions">
          <button class="btn primary" type="button" @click="toggleFavorite">
            {{ isJoined ? "관심 목록에서 삭제" : "관심 목록에 추가" }}
          </button>

          <button class="btn ghost large" type="button" @click="$router.back()">
            돌아가기
          </button>
        </div>
      </article>

      <aside class="content-panel">
        <h2>금리 옵션</h2>

        <table>
          <thead>
            <tr>
              <th>기간</th>
              <th>기본</th>
              <th>우대</th>
              <th>유형</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="option in product.options" :key="option.id">
              <td>{{ option.save_term }}개월</td>
              <td>{{ option.intr_rate }}%</td>
              <td>
                <strong>{{ option.intr_rate2 }}%</strong>
              </td>
              <td>{{ option.rate_type }}</td>
            </tr>
          </tbody>
        </table>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.detail-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.detail-actions .btn {
  width: auto;
}
</style>
