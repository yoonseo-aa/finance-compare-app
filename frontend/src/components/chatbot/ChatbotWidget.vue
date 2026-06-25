<script setup>
import { nextTick, ref } from "vue";

import { sendChatbotMessage } from "../../api/chatbot";

const isOpen = ref(false);
const input = ref("");
const loading = ref(false);
const messageList = ref(null);
const messages = ref([
  {
    role: "assistant",
    content: "안녕하세요. FinPick AI 상담입니다. 금융상품 비교와 추천 결과를 쉽게 설명해드릴게요."
  }
]);

const suggestedQuestions = [
  "예적금 상품은 어떻게 비교하나요?",
  "내 추천 결과를 설명해줘",
  "비상금 준비형이 뭐야?",
  "금은시세는 어디서 확인하나요?",
  "관심상품은 어떻게 저장하나요?",
  "대출비교는 어떤 기준으로 보면 좋나요?"
];

function toggleOpen() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) scrollToBottom();
}

async function scrollToBottom() {
  await nextTick();
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight;
  }
}

function contextFromMessage(text) {
  if (text.includes("추천")) return "recommendation";
  if (text.includes("금") || text.includes("은") || text.includes("시세")) return "spot";
  if (text.includes("대출")) return "loan";
  if (text.includes("연금")) return "pension";
  if (text.includes("관심")) return "favorite";
  return "general";
}

async function sendMessage(text = input.value) {
  const content = text.trim();
  if (!content || loading.value) return;

  messages.value.push({ role: "user", content });
  input.value = "";
  loading.value = true;
  await scrollToBottom();

  try {
    const data = await sendChatbotMessage({
      message: content,
      contextType: contextFromMessage(content)
    });
    messages.value.push({ role: "assistant", content: data.answer });
  } catch (error) {
    messages.value.push({
      role: "assistant",
      content: "일시적으로 답변을 불러오지 못했어요. 잠시 후 다시 시도해주세요."
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}

function handleKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}
</script>

<template>
  <div class="chatbot-widget" :class="{ open: isOpen }">
    <button v-if="!isOpen" class="chatbot-floating-button" type="button" title="FinPick AI 상담" @click="toggleOpen">
      <span>AI</span>
      <strong>상담</strong>
    </button>

    <section v-else class="chatbot-panel" aria-label="FinPick AI 상담">
      <header class="chatbot-header">
        <div>
          <span>FINPICK AI</span>
          <h2>FinPick AI 상담</h2>
          <p>금융상품 비교와 추천 결과를 쉽게 설명해드릴게요.</p>
        </div>
        <button class="chatbot-close" type="button" aria-label="챗봇 닫기" @click="toggleOpen">닫기</button>
      </header>

      <div ref="messageList" class="chatbot-messages">
        <article
          v-for="(message, index) in messages"
          :key="`${message.role}-${index}`"
          class="chatbot-message"
          :class="message.role"
        >
          <p>{{ message.content }}</p>
        </article>
        <article v-if="loading" class="chatbot-message assistant loading">
          <p><span class="typing-dots"><i></i><i></i><i></i></span>빠르게 확인하고 있어요</p>
        </article>
      </div>

      <div v-if="messages.length <= 1" class="chatbot-suggestions">
        <button
          v-for="question in suggestedQuestions"
          :key="question"
          type="button"
          @click="sendMessage(question)"
        >
          {{ question }}
        </button>
      </div>

      <form class="chatbot-input-area" @submit.prevent="sendMessage()">
        <textarea
          v-model="input"
          rows="2"
          maxlength="1000"
          placeholder="궁금한 내용을 입력하세요"
          @keydown="handleKeydown"
        ></textarea>
        <button class="chatbot-send" type="submit" :disabled="loading || !input.trim()">
          전송
        </button>
      </form>
    </section>
  </div>
</template>

<style scoped>
.chatbot-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 80;
  font-family: Arial, "Noto Sans KR", sans-serif;
}

.chatbot-floating-button {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  min-height: 54px;
  border: 0;
  border-radius: 999px;
  background: #2f80ed;
  box-shadow: 0 16px 34px rgba(47, 128, 237, .28);
  color: #fff;
  cursor: pointer;
  padding: 0 1.1rem;
}

.chatbot-floating-button span {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, .18);
  font-size: .86rem;
  font-weight: 900;
}

.chatbot-floating-button strong {
  font-size: .96rem;
  font-weight: 900;
}

.chatbot-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto auto;
  width: min(390px, calc(100vw - 32px));
  height: min(620px, calc(100vh - 112px));
  overflow: hidden;
  border: 1px solid #dbe7f5;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 24px 60px rgba(15, 39, 72, .18);
}

.chatbot-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, #f3f8fd, #fff);
  border-bottom: 1px solid #dbe7f5;
  padding: 1.05rem 1.1rem;
}

.chatbot-header span {
  color: #2f80ed;
  font-size: .72rem;
  font-weight: 900;
  letter-spacing: .08em;
}

.chatbot-header h2 {
  margin: .22rem 0 .18rem;
  color: #0f2748;
  font-size: 1.12rem;
  font-weight: 900;
}

.chatbot-header p {
  margin: 0;
  color: #657083;
  font-size: .82rem;
  line-height: 1.45;
}

.chatbot-close {
  align-self: start;
  border: 1px solid #dbe7f5;
  border-radius: 999px;
  background: #fff;
  color: #657083;
  cursor: pointer;
  font-size: .78rem;
  font-weight: 850;
  padding: .38rem .62rem;
}

.chatbot-messages {
  display: flex;
  flex-direction: column;
  gap: .65rem;
  min-height: 0;
  overflow-y: auto;
  background: #f3f8fd;
  padding: 1rem;
}

.chatbot-message {
  max-width: 84%;
}

.chatbot-message p {
  white-space: pre-line;
  margin: 0;
  border-radius: 16px;
  color: #0f2748;
  font-size: .9rem;
  line-height: 1.55;
  padding: .75rem .85rem;
}

.chatbot-message.assistant {
  align-self: flex-start;
}

.chatbot-message.assistant p {
  border: 1px solid #dbe7f5;
  background: #fff;
}

.chatbot-message.user {
  align-self: flex-end;
}

.chatbot-message.user p {
  background: #2f80ed;
  color: #fff;
}

.chatbot-message.loading p {
  display: inline-flex;
  align-items: center;
  gap: .55rem;
  color: #657083;
}

.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: .22rem;
}

.typing-dots i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2f80ed;
  animation: chatbotPulse .9s infinite ease-in-out;
}

.typing-dots i:nth-child(2) {
  animation-delay: .14s;
}

.typing-dots i:nth-child(3) {
  animation-delay: .28s;
}

@keyframes chatbotPulse {
  0%, 80%, 100% { opacity: .35; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-3px); }
}

.chatbot-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: .45rem;
  border-top: 1px solid #e5eef8;
  background: #fff;
  padding: .75rem .9rem;
}

.chatbot-suggestions button {
  border: 1px solid #dbe7f5;
  border-radius: 999px;
  background: #fff;
  color: #2f80ed;
  cursor: pointer;
  font-size: .78rem;
  font-weight: 800;
  padding: .42rem .62rem;
}

.chatbot-suggestions button:hover {
  background: #f3f8fd;
}

.chatbot-input-area {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: .55rem;
  border-top: 1px solid #dbe7f5;
  background: #fff;
  padding: .8rem;
}

.chatbot-input-area textarea {
  min-height: 48px;
  max-height: 96px;
  resize: none;
  border: 1px solid #dbe7f5;
  border-radius: 14px;
  color: #0f2748;
  line-height: 1.45;
  outline: none;
  padding: .75rem .8rem;
}

.chatbot-input-area textarea:focus {
  border-color: #9fc5ff;
  box-shadow: 0 0 0 3px rgba(47, 128, 237, .1);
}

.chatbot-send {
  align-self: stretch;
  min-width: 68px;
  border: 0;
  border-radius: 14px;
  background: #2f80ed;
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.chatbot-send:disabled {
  cursor: not-allowed;
  opacity: .45;
}

@media (max-width: 640px) {
  .chatbot-widget {
    right: 12px;
    bottom: 12px;
    left: 12px;
  }

  .chatbot-floating-button {
    margin-left: auto;
  }

  .chatbot-panel {
    width: 100%;
    height: min(620px, calc(100vh - 82px));
    border-radius: 18px;
  }
}
</style>
