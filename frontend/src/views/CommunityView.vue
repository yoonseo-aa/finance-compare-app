<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFetch } from "../api/client";
import StatusBlock from "../components/StatusBlock.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const posts = ref([]);
const selected = ref(null);
const loading = ref(true);
const error = ref("");
const postForm = reactive({ title: "", content: "" });
const comment = ref("");

const canWrite = computed(() => auth.isAuthenticated);

async function loadPosts() {
  loading.value = true;
  try {
    posts.value = await apiFetch("/posts/");
    if (selected.value) {
      selected.value = posts.value.find(post => post.id === selected.value.id) || null;
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function createPost() {
  const post = await apiFetch("/posts/", {
    method: "POST",
    body: JSON.stringify(postForm)
  });
  posts.value.unshift(post);
  selected.value = post;
  postForm.title = "";
  postForm.content = "";
}

async function removePost(post) {
  await apiFetch(`/posts/${post.id}/`, { method: "DELETE" });
  posts.value = posts.value.filter(item => item.id !== post.id);
  if (selected.value?.id === post.id) selected.value = null;
}

async function addComment() {
  if (!selected.value || !comment.value.trim()) return;
  selected.value = await apiFetch(`/posts/${selected.value.id}/comments/`, {
    method: "POST",
    body: JSON.stringify({ content: comment.value })
  });
  comment.value = "";
  await loadPosts();
}

async function removeComment(commentId) {
  await apiFetch(`/comments/${commentId}/`, { method: "DELETE" });
  selected.value.comments = selected.value.comments.filter(item => item.id !== commentId);
}

onMounted(loadPosts);
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>커뮤니티</h1>
      <p>금융 상품 리뷰와 정보를 나눕니다.</p>
    </div>
    <StatusBlock :loading="loading" :error="error" />
    <section class="community-layout">
      <div class="content-panel">
        <form v-if="canWrite" class="stack-form" @submit.prevent="createPost">
          <h2>게시글 작성</h2>
          <label>제목<input v-model="postForm.title" required></label>
          <label>내용<textarea v-model="postForm.content" rows="4" required></textarea></label>
          <button class="btn primary" type="submit">등록</button>
        </form>
        <p v-else class="muted">로그인 후 글을 작성할 수 있습니다.</p>
        <div class="post-list">
          <button v-for="post in posts" :key="post.id" class="post-row" type="button" @click="selected = post">
            <strong>{{ post.title }}</strong>
            <span>{{ post.author_name }} · 댓글 {{ post.comments_count }}</span>
          </button>
        </div>
      </div>
      <article class="content-panel" v-if="selected">
        <div class="split-head">
          <div>
            <h2>{{ selected.title }}</h2>
            <p class="muted">{{ selected.author_name }}</p>
          </div>
          <button v-if="selected.is_owner" class="btn danger" type="button" @click="removePost(selected)">삭제</button>
        </div>
        <p class="post-body">{{ selected.content }}</p>
        <form v-if="canWrite" class="comment-form" @submit.prevent="addComment">
          <input v-model="comment" placeholder="댓글 입력">
          <button class="btn primary" type="submit">등록</button>
        </form>
        <div class="comment-list">
          <div v-for="item in selected.comments" :key="item.id" class="comment-item">
            <strong>{{ item.author_name }}</strong>
            <p>{{ item.content }}</p>
            <button v-if="item.is_owner" class="link-danger" type="button" @click="removeComment(item.id)">삭제</button>
          </div>
        </div>
      </article>
      <div v-else class="status-block">게시글을 선택하세요.</div>
    </section>
  </main>
</template>
