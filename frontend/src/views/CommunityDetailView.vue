<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import { useCommunityStore } from "../stores/community";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const community = useCommunityStore();
const commentContent = ref("");
const editingCommentId = ref(null);
const editingContent = ref("");

const post = computed(() => community.getPostById(route.params.id));
const canComment = computed(() => auth.isAuthenticated || Boolean(localStorage.getItem("finpick-token")));
const commentAuthor = computed(() => {
  const user = auth.user || {};
  return user.display_name || user.nickname || user.username || user.email || "FinPick 사용자";
});
const currentUserKey = computed(() => {
  const user = auth.user || {};
  return String(user.id || user.pk || user.username || user.email || user.display_name || user.nickname || localStorage.getItem("finpick-token") || "");
});
const commentProfileImage = computed(() => {
  const user = auth.user || {};
  return user.profile_image || user.profileImage || user.avatar_url || user.avatar || "";
});
const commentProfileInitial = computed(() => commentAuthor.value.charAt(0));

onMounted(async () => {
  if (!auth.user && localStorage.getItem("finpick-token")) {
    await auth.bootstrap();
  }
  community.increaseViews(route.params.id);
});

function goList() {
  router.push("/community");
}

function goLogin() {
  router.push({ path: "/login", query: { next: route.fullPath } });
}

function toggleLike() {
  if (!post.value) return;
  community.toggleLike(post.value.id);
}

function submitComment() {
  if (!post.value) return;
  if (!canComment.value) {
    goLogin();
    return;
  }

  const content = commentContent.value.trim();
  if (!content) return;

  community.addComment(post.value.id, {
    author: commentAuthor.value,
    userKey: currentUserKey.value,
    profileImage: commentProfileImage.value,
    content
  });
  commentContent.value = "";
}

function isMyComment(comment) {
  return canComment.value && comment.userKey && comment.userKey === currentUserKey.value;
}

function startEditComment(comment) {
  editingCommentId.value = comment.id;
  editingContent.value = comment.content;
}

function cancelEditComment() {
  editingCommentId.value = null;
  editingContent.value = "";
}

function submitEditComment(comment) {
  const content = editingContent.value.trim();
  if (!post.value || !content) return;
  community.updateComment(post.value.id, comment.id, content);
  cancelEditComment();
}

function deleteComment(comment) {
  if (!post.value) return;
  community.deleteComment(post.value.id, comment.id);
  if (editingCommentId.value === comment.id) cancelEditComment();
}
</script>

<template>
  <main class="container community-detail-page">
    <button class="back-link detail-back" type="button" @click="goList">목록으로 돌아가기</button>

    <article v-if="post" class="detail-card">
      <div class="detail-topline">
        <span class="category-badge">{{ post.category }}</span>
        <button
          class="like-button"
          :class="{ active: post.liked }"
          type="button"
          :aria-pressed="post.liked"
          @click="toggleLike"
        >
          <span class="like-icon">{{ post.liked ? "💙" : "🤍" }}</span>
          <span>{{ post.likes }}</span>
        </button>
      </div>

      <header class="detail-title-block">
        <h2>{{ post.title }}</h2>
        <div class="detail-meta">
          <span>{{ post.author }}</span>
          <span>{{ post.createdAt }}</span>
          <span>조회 {{ post.views }}</span>
          <span>댓글 {{ post.comments }}</span>
        </div>
      </header>

      <div class="detail-divider"></div>

      <section class="detail-body-block">
        <p class="detail-content">{{ post.content }}</p>
        <div class="detail-tags">
          <span v-for="tag in post.tags" :key="tag">#{{ tag }}</span>
        </div>
      </section>

      <div class="detail-divider"></div>
    </article>

    <section v-if="post" class="comment-panel">
      <div class="comment-heading">
        <h2>댓글 {{ post.commentList.length }}</h2>
        <p>함께 나눈 의견을 확인해보세요.</p>
      </div>

      <form v-if="canComment" class="comment-composer" @submit.prevent="submitComment">
        <span class="comment-profile composer-profile" aria-hidden="true">
          <img v-if="commentProfileImage" :src="commentProfileImage" alt="">
          <span v-else>{{ commentProfileInitial }}</span>
        </span>
        <input
          v-model="commentContent"
          type="text"
          placeholder="지금 무슨 생각을 하고 있나요?"
        >
        <button class="composer-submit" type="submit" :disabled="!commentContent.trim()">
          작성
        </button>
      </form>

      <div v-else class="login-comment-box">
        <div>
          <strong>로그인이 필요합니다</strong>
          <p>댓글 작성은 로그인한 사용자만 가능합니다.</p>
        </div>
        <button class="btn ghost" type="button" @click="goLogin">로그인</button>
      </div>

      <div class="comment-list-local">
        <article v-for="comment in post.commentList" :key="comment.id" class="comment-card-local">
          <div class="comment-card-head">
            <div class="comment-author">
              <span class="comment-profile" aria-hidden="true">
                <img v-if="comment.profileImage" :src="comment.profileImage" alt="">
                <span v-else>{{ comment.author.charAt(0) }}</span>
              </span>
              <strong>{{ comment.author }}</strong>
              <small v-if="comment.updatedAt">{{ comment.updatedAt }}</small>
            </div>
            <div class="comment-side">
              <span>{{ comment.createdAt }}</span>
              <span v-if="isMyComment(comment)" class="comment-actions">
                <button type="button" @click="startEditComment(comment)">수정</button>
                <button type="button" @click="deleteComment(comment)">삭제</button>
              </span>
            </div>
          </div>

          <form
            v-if="editingCommentId === comment.id"
            class="comment-edit-form"
            @submit.prevent="submitEditComment(comment)"
          >
            <input v-model="editingContent" type="text" aria-label="댓글 수정 내용">
            <button type="submit" :disabled="!editingContent.trim()">저장</button>
            <button type="button" @click="cancelEditComment">취소</button>
          </form>
          <p v-else>{{ comment.content }}</p>
        </article>
      </div>
    </section>

    <div v-else class="status-block">게시글을 찾을 수 없습니다.</div>
  </main>
</template>

<style scoped>
.community-detail-page {
  --detail-ink: #161d2f;
  --detail-muted: #7a8495;
  --detail-soft: #f6f8fb;
  --detail-line: #e5ebf2;
  --detail-blue: #3182f6;
  --detail-blue-soft: #eef5ff;
  --detail-green: #00a889;
  padding-top: 2.6rem;
  padding-bottom: 4rem;
}

.detail-back {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  border: 1px solid var(--detail-line);
  border-radius: 999px;
  background: #fff;
  color: var(--detail-muted);
  padding: .45rem .9rem;
  font-weight: 800;
  cursor: pointer;
}

.detail-card,
.comment-panel {
  border: 1px solid var(--detail-line);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 12px 34px rgba(31, 44, 71, .06);
}

.detail-card {
  display: grid;
  gap: 1.25rem;
  margin-top: 1.1rem;
  padding: clamp(1.35rem, 3vw, 2.1rem);
}

.detail-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.category-badge {
  width: fit-content;
  border-radius: 999px;
  background: #f2f6fb;
  color: #536176;
  padding: .34rem .72rem;
  font-size: .84rem;
  font-weight: 800;
}

.like-button {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  min-height: 40px;
  border: 1px solid var(--detail-line);
  border-radius: 999px;
  background: #fff;
  color: var(--detail-muted);
  padding: .42rem .82rem;
  font-weight: 900;
  cursor: pointer;
  transition: background .18s ease, border-color .18s ease, color .18s ease, transform .18s ease;
}

.like-button:hover {
  transform: translateY(-1px);
  border-color: #c8d8ee;
  background: #f8fbff;
}

.like-button.active {
  border-color: rgba(49, 130, 246, .22);
  background: var(--detail-blue-soft);
  color: var(--detail-blue);
}

.like-icon {
  font-size: 1.06rem;
  line-height: 1;
}

.detail-title-block {
  display: grid;
  gap: .75rem;
}

.detail-title-block h2 {
  max-width: 920px;
  margin: 0;
  color: var(--detail-ink);
  font-size: clamp(1.9rem, 3.6vw, 3.1rem);
  font-weight: 900;
  line-height: 1.24;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: .45rem .85rem;
  color: var(--detail-muted);
  font-size: .94rem;
  font-weight: 700;
}

.detail-divider {
  height: 1px;
  background: var(--detail-line);
}

.detail-body-block {
  display: grid;
  gap: 1.1rem;
}

.detail-content {
  margin: 0;
  color: #283246;
  font-size: 1.02rem;
  line-height: 1.9;
  white-space: pre-wrap;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
}

.detail-tags span {
  border-radius: 999px;
  background: #f4faf8;
  color: #07816e;
  padding: .28rem .6rem;
  font-size: .86rem;
  font-weight: 800;
}

.comment-panel {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  padding: clamp(1.25rem, 3vw, 1.7rem);
}

.comment-heading {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
}

.comment-heading h2 {
  margin: 0;
  color: var(--detail-ink);
  font-size: 1.35rem;
  font-weight: 900;
}

.comment-heading p {
  margin: 0;
  color: var(--detail-muted);
  font-size: .94rem;
  font-weight: 700;
}

.comment-composer {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) auto;
  gap: .55rem;
  align-items: center;
  min-height: 44px;
  border: 1px solid #cfd6df;
  border-radius: 14px;
  background: #fbfcfe;
  padding: .25rem .45rem .25rem .55rem;
}

.comment-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #eef1f5;
  color: #c2c9d3;
  font-size: .82rem;
}

.comment-composer input {
  width: 100%;
  min-width: 0;
  height: 34px;
  border: 0;
  background: transparent;
  color: var(--detail-ink);
  font-weight: 700;
  outline: none;
}

.comment-composer input::placeholder {
  color: #a0a8b5;
}

.composer-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  height: 32px;
  border: 0;
  border-radius: 10px;
  background: var(--detail-blue);
  color: #fff;
  padding: 0 .75rem;
  font-weight: 900;
  cursor: pointer;
}

.composer-submit:not(:disabled):hover {
  background: #1f6fe5;
}

.composer-submit:disabled {
  background: #e3e8ef;
  color: #a4acb8;
  cursor: not-allowed;
}

.login-comment-box {
  display: flex;
  justify-content: space-between;
  gap: .9rem;
  align-items: center;
  border: 1px solid #dce7f6;
  border-radius: 14px;
  background: #f8fbff;
  padding: 1rem;
}

.login-comment-box strong {
  display: block;
  margin-bottom: .25rem;
  color: var(--detail-ink);
}

.login-comment-box p {
  margin: 0;
  color: var(--detail-muted);
  font-weight: 700;
}

.comment-list-local {
  display: grid;
  gap: .7rem;
}

.comment-card-local {
  display: grid;
  gap: .42rem;
  border: 1px solid var(--detail-line);
  border-radius: 14px;
  background: #fff;
  padding: .95rem 1rem;
}

.comment-card-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: var(--detail-muted);
  font-size: .9rem;
  font-weight: 700;
}


.comment-side {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: .65rem;
}

.comment-actions {
  display: inline-flex;
  gap: .35rem;
}

.comment-actions button,
.comment-edit-form button {
  border: 1px solid var(--detail-line);
  border-radius: 8px;
  background: #fff;
  color: var(--detail-muted);
  padding: .28rem .5rem;
  font-size: .82rem;
  font-weight: 800;
  cursor: pointer;
}

.comment-actions button:hover,
.comment-edit-form button:hover:not(:disabled) {
  border-color: #c8d8ee;
  background: #f8fbff;
  color: var(--detail-blue);
}

.comment-edit-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: .45rem;
  align-items: center;
}

.comment-edit-form input {
  width: 100%;
  min-height: 36px;
  border: 1px solid var(--detail-line);
  border-radius: 10px;
  padding: 0 .75rem;
  color: var(--detail-ink);
  font-weight: 700;
  outline: none;
}

.comment-edit-form input:focus {
  border-color: rgba(49, 130, 246, .45);
  box-shadow: 0 0 0 3px rgba(49, 130, 246, .1);
}

.comment-edit-form button:disabled {
  opacity: .45;
  cursor: not-allowed;
}
.comment-author {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
}

.comment-author small {
  color: #a0a8b5;
  font-size: .78rem;
  font-weight: 800;
}

.comment-profile {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #edf3fb;
  color: #536176;
  font-size: .82rem;
  font-weight: 900;
  overflow: hidden;
}

.comment-profile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.composer-profile {
  background: #eef1f5;
  color: #536176;
}

.comment-card-local strong {
  color: var(--detail-ink);
}

.comment-card-local p {
  margin: 0;
  color: #283246;
  line-height: 1.65;
}

@media (max-width: 700px) {
  .community-detail-page {
    padding-top: 2rem;
  }

  .detail-topline,
  .comment-heading,
  .login-comment-box,
  .comment-card-head {
    display: grid;
    justify-content: stretch;
  }

  .like-button {
    width: fit-content;
  }
}

@media (max-width: 520px) {
  .comment-composer {
    grid-template-columns: 28px minmax(0, 1fr) auto;
  }

  .comment-edit-form {
    grid-template-columns: 1fr;
  }
}
</style>



