import { defineStore } from "pinia";

import { apiFetch, setToken } from "../api/client";

function socialRedirectUri(provider) {
  return `${window.location.origin}/social/callback/${provider}`;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    loading: false
  }),
  getters: {
    isAuthenticated: state => Boolean(state.user)
  },
  actions: {
    async bootstrap() {
      if (!localStorage.getItem("finpick-token")) return;
      try {
        this.user = await apiFetch("/auth/me/");
      } catch {
        setToken("");
        this.user = null;
      }
    },
    async login(payload) {
      const data = await apiFetch("/auth/login/", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setToken(data.token);
      this.user = data.user;
    },
    async signup(payload) {
      const data = await apiFetch("/auth/signup/", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setToken(data.token);
      this.user = data.user;
    },
    async loginWithSocial(provider) {
      const redirectUri = socialRedirectUri(provider);
      const data = await apiFetch(`/auth/social/${provider}/login/?redirect_uri=${encodeURIComponent(redirectUri)}`);
      sessionStorage.setItem(`finpick-social-state-${provider}`, data.state);
      window.location.href = data.authorization_url;
    },
    async completeSocialLogin(provider, payload) {
      const redirectUri = socialRedirectUri(provider);
      const data = await apiFetch(`/auth/social/${provider}/callback/`, {
        method: "POST",
        body: JSON.stringify({
          ...payload,
          redirect_uri: redirectUri
        })
      });
      setToken(data.token);
      this.user = data.user;
    },
    async logout() {
      try {
        await apiFetch("/auth/logout/", { method: "POST" });
      } finally {
        setToken("");
        this.user = null;
      }
    },
    async updateProfile(payload) {
      const isFormData = payload instanceof FormData;
      this.user = await apiFetch("/auth/me/", {
        method: "PATCH",
        body: isFormData ? payload : JSON.stringify(payload)
      });
    },
    setUser(user) {
      this.user = user;
    }
  }
});
