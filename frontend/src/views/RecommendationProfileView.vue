<script setup>
import { reactive, ref } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const error = ref("");
const success = ref("");
const saving = ref(false);

const form = reactive({
  age_group: auth.user?.age_group || "",
  marital_status: auth.user?.marital_status || "",
  has_children: auth.user?.has_children ?? null,
  region: auth.user?.region || "",
  income_level: auth.user?.income_level || "",
  asset_level: auth.user?.asset_level || "",
  employment_status: auth.user?.employment_status || "",
  saving_purpose: auth.user?.saving_purpose || "",
  risk_tolerance: auth.user?.risk_tolerance || "stable",
  savings_goal: auth.user?.savings_goal || 1000000,
  monthly_saving: auth.user?.monthly_saving || 400000,
  preferred_term: auth.user?.preferred_term || 12
});

async function submit() {
  error.value = "";
  success.value = "";
  saving.value = true;
  try {
    await auth.updateProfile(form);
    success.value = "추천 진단 정보가 저장되었습니다.";
  } catch (err) {
    error.value = err.message;
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <main class="container recommend-flow-page">
    <section class="recommend-hero-local">
      <h1>예적금 추천 진단</h1>
      <p>현재 상황을 입력하면 금리, 기간, 생애주기, 목적을 함께 계산해 추천 점수와 이유를 보여드립니다.</p>
    </section>

    <form class="recommend-profile-form-local" @submit.prevent="submit">
      <div class="recommend-top-grid-local">
        <section class="recommend-card-local situation-card-local">
          <div class="recommend-card-head-local">
            <span aria-hidden="true">◉</span>
            <div><h2>나의 현재 상황</h2><p>현재 생활 환경과 저축 목적을 알려주세요.</p></div>
          </div>
          <div class="situation-grid-local">
            <label>나이대
              <select v-model="form.age_group">
                <option value="">선택 안 함</option>
                <option value="child">어린이</option>
                <option value="youth">청년</option>
                <option value="middle">중장년</option>
                <option value="senior">시니어</option>
              </select>
            </label>
            <label>결혼 유무
              <select v-model="form.marital_status">
                <option value="">선택 안 함</option>
                <option value="single">미혼</option>
                <option value="married">기혼</option>
              </select>
            </label>
            <label>자녀 유무
              <select v-model="form.has_children">
                <option :value="null">선택 안 함</option>
                <option :value="true">있음</option>
                <option :value="false">없음</option>
              </select>
            </label>
            <label>지역<input v-model="form.region" placeholder="예: 서울, 부산, 경남"></label>
            <label>소득
              <select v-model="form.income_level">
                <option value="">선택 안 함</option>
                <option value="low">낮음</option>
                <option value="middle">보통</option>
                <option value="high">높음</option>
              </select>
            </label>
            <label>재산
              <select v-model="form.asset_level">
                <option value="">선택 안 함</option>
                <option value="low">적음</option>
                <option value="middle">보통</option>
                <option value="high">많음</option>
              </select>
            </label>
            <label>직업/상태
              <select v-model="form.employment_status">
                <option value="">선택 안 함</option>
                <option value="student">학생</option>
                <option value="employee">직장인</option>
                <option value="self_employed">자영업자</option>
                <option value="retired">은퇴/퇴직</option>
              </select>
            </label>
            <label>저축 목적
              <select v-model="form.saving_purpose">
                <option value="">선택 안 함</option>
                <option value="emergency">비상금</option>
                <option value="housing">주거/내 집 마련</option>
                <option value="education">교육/자녀</option>
                <option value="retirement">노후 준비</option>
                <option value="travel">여행/목돈</option>
              </select>
            </label>
            <label>성향
              <select v-model="form.risk_tolerance">
                <option value="stable">안정형</option>
                <option value="balanced">균형형</option>
                <option value="aggressive">수익형</option>
              </select>
            </label>
          </div>
        </section>

        <aside class="recommend-card-local example-card-local">
          <div class="recommend-card-head-local">
            <span aria-hidden="true">▥</span>
            <div><h2>가입 상품 예시</h2><p>입력한 정보를 바탕으로 추천 점수를 계산합니다.</p></div>
          </div>
          <div class="example-chart-local" aria-label="예적금 추천 점수 예시">
            <div class="chart-lines-local"><span>5.0</span><span>4.0</span><span>3.0</span><span>2.0</span><span>1.0</span></div>
            <div class="chart-bar-local"><span>예적금 추천 점수</span></div>
          </div>
          <div class="example-note-local"><strong>ⓘ 예시 점수입니다</strong><span>입력 정보를 바탕으로 실제 추천 점수가 계산됩니다.</span></div>
        </aside>
      </div>

      <section class="recommend-card-local savings-card-local">
        <div class="recommend-card-head-local">
          <span aria-hidden="true">₩</span>
          <div><h2>저축 기준</h2><p>추천 결과에 반영할 목표와 저축 가능 금액을 설정하세요.</p></div>
        </div>
        <div class="savings-grid-local">
          <label>목표 금액<div class="suffix-input-local"><input v-model.number="form.savings_goal" type="number" min="0"><span>원</span></div></label>
          <label>월 저축 가능 금액<div class="suffix-input-local"><input v-model.number="form.monthly_saving" type="number" min="0"><span>원</span></div></label>
          <label>선호 기간<div class="suffix-input-local"><input v-model.number="form.preferred_term" type="number" min="1"><span>개월</span></div></label>
        </div>
      </section>

      <p v-if="error" class="form-error recommend-message-local">{{ error }}</p>
      <p v-if="success" class="form-success recommend-message-local">{{ success }}</p>
      <div class="recommend-actions-local">
        <button class="btn primary large" type="submit" :disabled="saving">{{ saving ? "저장 중" : "저장" }}</button>
        <button class="btn ghost large" type="button" @click="$router.back()">돌아가기</button>
      </div>
    </form>
  </main>
</template>

<style scoped>
.recommend-flow-page { max-width: 1240px; min-height: calc(100vh - 72px); padding-top: 2.8rem; padding-bottom: 4rem; }
.recommend-hero-local { margin-bottom: 1.7rem; }
.recommend-hero-local h1 { color: #102a4b; font-size: 2rem; letter-spacing: -.045em; margin: 0; }
.recommend-hero-local p { color: #687b93; margin: .55rem 0 0; }
.recommend-profile-form-local { display: grid; gap: 1.15rem; }
.recommend-top-grid-local { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(290px, .8fr); gap: 1.15rem; align-items: stretch; }
.recommend-card-local { border: 1px solid #dce6f2; border-radius: 16px; background: #fff; box-shadow: 0 10px 24px rgba(29,55,88,.055); padding: 1.3rem; }
.recommend-card-head-local { display: flex; align-items: start; gap: .7rem; margin-bottom: 1.1rem; }
.recommend-card-head-local > span { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 10px; background: #eaf3ff; color: #1d6dea; font-weight: 900; }
.recommend-card-head-local h2 { color: #183250; font-size: 1.18rem; letter-spacing: -.025em; margin: 0; }
.recommend-card-head-local p { color: #708198; font-size: .82rem; margin: .28rem 0 0; }
.situation-grid-local { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .95rem 1.1rem; }
.situation-grid-local label, .savings-grid-local label { display: grid; gap: .42rem; color: #243d5a; font-size: .86rem; font-weight: 850; }
.situation-grid-local select, .situation-grid-local input, .suffix-input-local { min-height: 44px; border: 1px solid #d6e2f0; border-radius: 9px; background: #fbfdff; color: #183250; font: inherit; outline: none; padding: 0 .75rem; }
.situation-grid-local select:focus, .situation-grid-local input:focus, .suffix-input-local:focus-within { border-color: #4c8bf5; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }
.example-card-local { display: grid; grid-template-rows: auto 1fr auto; }
.example-chart-local { position: relative; display: grid; grid-template-columns: 34px 1fr; align-items: stretch; min-height: 205px; border-bottom: 1px solid #d9e4ef; padding-top: .3rem; }
.chart-lines-local { display: flex; flex-direction: column; justify-content: space-between; color: #708198; font-size: .72rem; padding: .1rem 0 1.2rem; }
.chart-bar-local { position: relative; display: grid; align-items: end; justify-items: center; border-left: 1px solid #cfdbe8; background: repeating-linear-gradient(to bottom, transparent 0, transparent 39px, #edf2f7 40px); }
.chart-bar-local::before { width: 42%; height: 72%; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, #3f86f5, #1e68e8); box-shadow: 0 7px 14px rgba(37,99,235,.18); content: ""; }
.chart-bar-local span { color: #64768e; font-size: .75rem; margin-top: .45rem; transform: translateY(1.55rem); }
.example-note-local { display: grid; gap: .32rem; border-radius: 10px; background: #edf5ff; color: #246fe5; font-size: .78rem; line-height: 1.5; margin-top: 1.8rem; padding: .8rem; }
.example-note-local strong { font-size: .82rem; }
.savings-card-local { padding-bottom: 1.4rem; }
.savings-grid-local { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.suffix-input-local { display: flex; align-items: center; overflow: hidden; padding: 0; }
.suffix-input-local input { width: 100%; min-width: 0; border: 0; background: transparent; color: #183250; font: inherit; font-weight: 750; outline: none; padding: 0 .75rem; }
.suffix-input-local span { align-self: stretch; display: grid; min-width: 42px; place-items: center; border-left: 1px solid #d6e2f0; background: #f1f5f9; color: #526780; font-size: .82rem; font-weight: 800; }
.recommend-message-local { margin: 0; }
.recommend-actions-local { display: flex; justify-content: center; gap: .8rem; margin-top: .45rem; }
.recommend-actions-local .btn { min-width: 164px; min-height: 48px; border-radius: 10px; }
@media (max-width: 900px) { .recommend-top-grid-local { grid-template-columns: 1fr; } .example-chart-local { min-height: 160px; } }
@media (max-width: 640px) { .recommend-flow-page { padding-top: 1.75rem; } .situation-grid-local, .savings-grid-local { grid-template-columns: 1fr; } .recommend-card-local { padding: 1.05rem; } .recommend-actions-local { flex-direction: column; } .recommend-actions-local .btn { width: 100%; } }
</style>
