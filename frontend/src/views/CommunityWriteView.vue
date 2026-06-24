<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";

import { useCommunityStore, writeCategories } from "../stores/community";

const router = useRouter();
const community = useCommunityStore();

const form = reactive({
  category: "",
  title: "",
  content: "",
  tags: ""
});

function submit() {
  if (!form.category) {
    alert("카테고리를 선택해주세요.");
    return;
  }
  if (!form.title.trim()) {
    alert("제목을 입력해주세요.");
    return;
  }
  if (!form.content.trim()) {
    alert("내용을 입력해주세요.");
    return;
  }

  try {
    community.addPost({
      category: form.category,
      title: form.title.trim(),
      content: form.content.trim(),
      tags: form.tags.split(",").map(tag => tag.trim()).filter(Boolean)
    });
    router.push("/community");
  } catch {
    alert("게시글 등록에 실패했습니다.");
  }
}

function cancel() {
  router.push("/community");
}
</script>

<template>
  <main class="container community-write-page">
    <section class="write-hero">
      <div>
        <p class="eyebrow">Community write</p>
        <h1>게시글 작성</h1>
        <p>금융 상품 후기나 재테크 고민을 편하게 남겨보세요.</p>
      </div>
    </section>

    <form class="content-panel write-form" @submit.prevent="submit">
      <label>
        카테고리
        <select v-model="form.category">
          <option value="">카테고리 선택</option>
          <option v-for="category in writeCategories" :key="category" :value="category">{{ category }}</option>
        </select>
      </label>

      <label>
        제목
        <input v-model="form.title" placeholder="제목을 입력해주세요">
      </label>

      <label>
        내용
        <textarea v-model="form.content" rows="10" placeholder="내용을 입력해주세요"></textarea>
      </label>

      <label>
        태그
        <input v-model="form.tags" placeholder="예: 사회초년생, 적금, 목돈모으기">
      </label>

      <div class="write-actions">
        <button class="btn primary large" type="submit">등록</button>
        <button class="btn ghost large" type="button" @click="cancel">취소</button>
      </div>
    </form>
  </main>
</template>

<style scoped>
.community-write-page {
  padding-top: 2.4rem;
}

.write-hero {
  margin-bottom: 1rem;
}

.write-hero h1 {
  margin: .2rem 0 .45rem;
  font-size: clamp(2rem, 4.5vw, 3.2rem);
}

.write-hero p {
  margin: 0;
  color: var(--muted);
}

.write-form {
  display: grid;
  gap: 1rem;
  width: min(820px, 100%);
}

.write-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .7rem;
}
</style>