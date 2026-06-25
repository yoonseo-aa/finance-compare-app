import { apiFetch } from "./client";

export function sendChatbotMessage({ message, contextType = "general" }) {
  return apiFetch("/chatbot/message/", {
    method: "POST",
    body: JSON.stringify({ message, contextType })
  });
}
