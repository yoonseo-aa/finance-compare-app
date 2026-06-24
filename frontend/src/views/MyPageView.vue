<script setup>
import { onMounted } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

onMounted(() => auth.bootstrap());
</script>

<template>
  <main class="container mypage-page">
    <section class="flow-hero">
      <div>
        <span class="form-eyebrow">MY FINPICK</span>
        <h1>마이페이지</h1>
        <p>{{ auth.user?.display_name || auth.user?.username }}님의 추천 정보와 가입 상품을 한곳에서 관리합니다.</p>
      </div>
      <RouterLink class="btn primary" to="/recommend-profile">예적금 추천 진단</RouterLink>
    </section>

    <section class="mypage-grid" v-if="auth.user">
      <RouterLink class="mypage-card highlight" to="/recommend-profile">
        <span>추천 준비</span>
        <strong>내 상황 입력하기</strong>
        <p>나이대, 결혼/자녀, 소득, 재산, 저축 목적을 바탕으로 추천 점수를 계산합니다.</p>
      </RouterLink>
      <RouterLink class="mypage-card" to="/recommendations">
        <span>추천 결과</span>
        <strong>맞춤 예적금 보기</strong>
        <p>상품별 추천점수와 추천 이유를 확인합니다.</p>
      </RouterLink>
      <RouterLink class="mypage-card" to="/profile">
        <span>정보 관리</span>
        <strong>프로필 수정</strong>
        <p>대시보드 기준과 추천 프로필을 다시 조정합니다.</p>
      </RouterLink>
      <RouterLink class="mypage-card" to="/dashboard">
        <span>분석</span>
        <strong>개인화 대시보드</strong>
        <p>목표 달성률과 예상 만기 금액을 확인합니다.</p>
      </RouterLink>
    </section>

    <section class="content-panel" v-if="auth.user">
      <div class="section-head compact-head">
        <h2>내 추천 프로필</h2>
        <p>추천 결과에 반영되는 현재 입력값입니다.</p>
      </div>
      <dl class="profile-summary-list">
        <div><dt>나이대</dt><dd>{{ auth.user.age_group || '미입력' }}</dd></div>
        <div><dt>결혼</dt><dd>{{ auth.user.marital_status || '미입력' }}</dd></div>
        <div><dt>자녀</dt><dd>{{ auth.user.has_children === null ? '미입력' : (auth.user.has_children ? '있음' : '없음') }}</dd></div>
        <div><dt>지역</dt><dd>{{ auth.user.region || '미입력' }}</dd></div>
        <div><dt>소득</dt><dd>{{ auth.user.income_level || '미입력' }}</dd></div>
        <div><dt>재산</dt><dd>{{ auth.user.asset_level || '미입력' }}</dd></div>
        <div><dt>직업/상태</dt><dd>{{ auth.user.employment_status || '미입력' }}</dd></div>
        <div><dt>저축 목적</dt><dd>{{ auth.user.saving_purpose || '미입력' }}</dd></div>
      </dl>
    </section>
  </main>
</template>
