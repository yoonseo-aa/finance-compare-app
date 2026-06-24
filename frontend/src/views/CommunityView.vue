<script setup>
import { computed, ref } from "vue";

import { communityCategories, useCommunityStore } from "../stores/community";

const community = useCommunityStore();
const activeCategory = ref("전체");
const searchQuery = ref("");

const posts = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase();
  const categoryPosts = community.filteredPosts(activeCategory.value);

  if (!keyword) return categoryPosts;

  return categoryPosts.filter(post => {
    const searchableText = [post.category, post.title, post.content, post.author, ...post.tags]
      .join(" ")
      .toLowerCase();
    return searchableText.includes(keyword);
  });
});
const popularPosts = computed(() => community.popularPosts);
</script>

<template>
  <main class="container community-page">
    <section class="community-hero">
      <div class="community-title-block">
        <span class="page-kicker">FinPick 라운지</span>
        <h1>커뮤니티</h1>
        <p>금융 상품 후기와 재테크 고민을 함께 나눠보세요.</p>
      </div>
      <RouterLink class="btn primary write-button" to="/community/write">글쓰기</RouterLink>
    </section>

    <section class="community-toolbar" aria-label="커뮤니티 검색 및 필터">
      <label class="community-search">
        <span>검색</span>
        <input
          v-model="searchQuery"
          type="search"
          placeholder="제목, 내용, 태그, 작성자로 검색"
        >
      </label>
      <button v-if="searchQuery" class="btn ghost reset-button" type="button" @click="searchQuery = ''">
        초기화
      </button>
    </section>

    <section class="category-tabs" aria-label="커뮤니티 카테고리">
      <button
        v-for="category in communityCategories"
        :key="category"
        type="button"
        :class="{ active: activeCategory === category }"
        @click="activeCategory = category"
      >
        {{ category }}
      </button>
    </section>

    <section class="community-grid">
      <div class="post-column">
        <div class="list-summary">
          <strong>{{ activeCategory }} 게시글</strong>
          <span>{{ posts.length }}개</span>
        </div>

        <div class="post-card-list">
          <RouterLink
            v-for="post in posts"
            :key="post.id"
            class="community-post-card"
            :to="`/community/${post.id}`"
          >
            <div class="post-card-top">
              <span class="category-badge">{{ post.category }}</span>
              <span class="post-time">{{ post.createdAt }}</span>
            </div>
            <div class="post-main-copy">
              <h2>{{ post.title }}</h2>
              <p>{{ post.content }}</p>
            </div>
            <div class="post-tags">
              <span v-for="tag in post.tags" :key="tag">#{{ tag }}</span>
            </div>
            <div class="post-meta">
              <span class="author">{{ post.author }}</span>
              <span>댓글 {{ post.comments }}</span>
              <span>조회 {{ post.views }}</span>
              <span>좋아요 {{ post.likes }}</span>
            </div>
          </RouterLink>

          <div v-if="!posts.length" class="status-block empty-state">
            검색 조건에 맞는 게시글이 없습니다.
          </div>
        </div>
      </div>

      <aside class="popular-panel">
        <div class="popular-card">
          <div class="section-head compact">
            <span class="panel-kicker">Weekly pick</span>
            <h2>인기 게시글</h2>
            <p>댓글과 좋아요 반응이 많은 글입니다.</p>
          </div>
          <RouterLink
            v-for="(post, index) in popularPosts"
            :key="post.id"
            class="popular-post"
            :to="`/community/${post.id}`"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="popular-copy">
              <em>{{ post.category }}</em>
              <strong>{{ post.title }}</strong>
              <small>좋아요 {{ post.likes }} · 댓글 {{ post.comments }}</small>
            </span>
          </RouterLink>
        </div>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.community-page {
  --community-ink: #152238;
  --community-subtle: #6b7890;
  --community-blue: #2f6fed;
  --community-mint: #12a594;
  --community-cream: #fff9ec;
  --community-border: #dbe6f2;
  --community-card: rgba(255, 255, 255, .92);
  padding-top: 3rem;
  padding-bottom: 4rem;
}

.community-hero {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1.5rem;
  margin-bottom: 1.4rem;
}

.community-title-block {
  display: grid;
  gap: .55rem;
}

.page-kicker,
.panel-kicker {
  color: var(--community-mint);
  font-size: .84rem;
  font-weight: 900;
  letter-spacing: 0;
}

.community-hero h1 {
  margin: 0;
  color: var(--community-ink);
  font-size: clamp(2.35rem, 4.8vw, 4rem);
  line-height: 1.08;
}

.community-hero p {
  margin: 0;
  color: var(--community-subtle);
  font-size: 1rem;
  line-height: 1.7;
}

.write-button {
  min-width: 104px;
  min-height: 46px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #2f6fed, #12a594);
  box-shadow: 0 14px 28px rgba(47, 111, 237, .22);
}

.community-toolbar {
  display: flex;
  gap: .75rem;
  align-items: stretch;
  margin-bottom: 1rem;
}

.community-search {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 720px;
  min-height: 54px;
  border: 1px solid var(--community-border);
  border-radius: 14px;
  background: var(--community-card);
  box-shadow: 0 16px 40px rgba(31, 44, 71, .06);
  overflow: hidden;
}

.community-search span {
  padding-left: 1rem;
  color: var(--community-mint);
  font-size: .9rem;
  font-weight: 900;
  white-space: nowrap;
}

.community-search input {
  width: 100%;
  min-height: 52px;
  border: 0;
  background: transparent;
  color: var(--community-ink);
  padding: 0 1rem;
  font-weight: 800;
  outline: none;
}

.community-search:focus-within {
  border-color: rgba(18, 165, 148, .55);
  box-shadow: 0 0 0 4px rgba(18, 165, 148, .11), 0 18px 44px rgba(31, 44, 71, .08);
}

.reset-button {
  min-height: 54px;
  border-radius: 14px;
  background: #fff;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: .65rem;
  margin-bottom: 1.6rem;
}

.category-tabs button {
  min-height: 40px;
  border: 1px solid var(--community-border);
  border-radius: 999px;
  background: #fff;
  color: var(--community-subtle);
  padding: .5rem 1rem;
  font-weight: 900;
  cursor: pointer;
  transition: transform .18s ease, border-color .18s ease, background .18s ease, color .18s ease;
}

.category-tabs button:hover {
  transform: translateY(-1px);
  border-color: rgba(18, 165, 148, .45);
}

.category-tabs button.active {
  border-color: transparent;
  background: #e9f8f5;
  color: #08786d;
  box-shadow: inset 0 0 0 1px rgba(18, 165, 148, .12);
}

.community-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 1.4rem;
  align-items: start;
}

.post-column {
  display: grid;
  gap: .85rem;
}

.list-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--community-subtle);
  font-weight: 900;
}

.list-summary strong {
  color: var(--community-ink);
  font-size: 1.04rem;
}

.post-card-list {
  display: grid;
  gap: 1rem;
}

.community-post-card {
  display: grid;
  gap: .8rem;
  border: 1px solid var(--community-border);
  border-radius: 18px;
  background: var(--community-card);
  padding: 1.35rem;
  color: inherit;
  text-decoration: none;
  box-shadow: 0 14px 36px rgba(28, 39, 61, .07);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}

.community-post-card:hover {
  transform: translateY(-2px);
  border-color: rgba(47, 111, 237, .28);
  box-shadow: 0 20px 46px rgba(28, 39, 61, .1);
}

.post-card-top,
.post-meta,
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: .55rem;
  align-items: center;
}

.post-card-top {
  justify-content: space-between;
}

.category-badge {
  display: inline-flex;
  border-radius: 999px;
  background: #edf7ff;
  color: #1e5bbf;
  padding: .34rem .7rem;
  font-size: .84rem;
  font-weight: 900;
}

.post-time {
  color: var(--community-subtle);
  font-size: .9rem;
  font-weight: 800;
}

.post-main-copy {
  display: grid;
  gap: .5rem;
}

.community-post-card h2 {
  margin: 0;
  color: var(--community-ink);
  font-size: 1.2rem;
  line-height: 1.4;
}

.community-post-card p {
  margin: 0;
  color: var(--community-subtle);
  line-height: 1.75;
}

.post-tags span {
  border-radius: 999px;
  background: var(--community-cream);
  color: #9a5b08;
  padding: .24rem .55rem;
  font-size: .82rem;
  font-weight: 900;
}

.post-meta {
  border-top: 1px solid #edf2f7;
  padding-top: .85rem;
  color: var(--community-subtle);
  font-size: .9rem;
  font-weight: 800;
}

.post-meta .author {
  color: var(--community-ink);
}

.popular-panel {
  position: sticky;
  top: 92px;
}

.popular-card {
  border: 1px solid var(--community-border);
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  padding: 1.25rem;
  box-shadow: 0 16px 40px rgba(28, 39, 61, .08);
}

.section-head.compact {
  display: grid;
  gap: .35rem;
  margin-bottom: .7rem;
}

.section-head.compact h2 {
  margin: 0;
  color: var(--community-ink);
  font-size: 1.35rem;
}

.section-head.compact p {
  margin: 0;
  color: var(--community-subtle);
  line-height: 1.55;
}

.popular-post {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: .75rem;
  padding: 1rem 0;
  border-top: 1px solid #e8eef6;
  color: inherit;
  text-decoration: none;
}

.rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #e9f8f5;
  color: #08786d;
  font-weight: 900;
}

.popular-copy {
  display: grid;
  gap: .28rem;
}

.popular-post em {
  color: var(--community-mint);
  font-size: .82rem;
  font-style: normal;
  font-weight: 900;
}

.popular-post strong {
  color: var(--community-ink);
  line-height: 1.45;
}

.popular-post small {
  color: var(--community-subtle);
  font-weight: 800;
}

.empty-state {
  min-height: 160px;
  border-radius: 18px;
  background: #fff;
}

@media (max-width: 900px) {
  .community-hero,
  .community-grid {
    display: grid;
  }

  .community-grid {
    grid-template-columns: 1fr;
  }

  .popular-panel {
    position: static;
  }
}

@media (max-width: 560px) {
  .community-page {
    padding-top: 2rem;
  }

  .community-toolbar,
  .community-search,
  .post-card-top {
    display: grid;
  }

  .community-search {
    max-width: none;
  }

  .community-search span {
    padding: .85rem 1rem 0;
  }

  .community-search input {
    min-height: 44px;
    padding-top: 0;
  }

  .write-button,
  .reset-button {
    width: 100%;
  }

  .community-post-card,
  .popular-card {
    border-radius: 16px;
    padding: 1rem;
  }
}
</style>
