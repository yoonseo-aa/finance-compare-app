import os
import re
import secrets
from urllib.parse import urlencode

import requests
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework.exceptions import APIException, ValidationError


class SocialAuthError(APIException):
    status_code = 400
    default_detail = "Social login failed."
    default_code = "social_login_failed"


def provider_error_message(provider, response):
    try:
        payload = response.json()
    except ValueError:
        payload = {"error": response.text[:200]}

    detail = (
        payload.get("error_description")
        or payload.get("error")
        or payload.get("msg")
        or payload.get("message")
        or "Unknown provider error."
    )
    detail = re.sub(r"code=[^\s&]+", "code=[hidden]", str(detail))
    return f"{provider} token exchange failed ({response.status_code}): {detail}"

PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "profile_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "client_id_env": "GOOGLE_CLIENT_ID",
        "client_secret_env": "GOOGLE_CLIENT_SECRET",
        "scope": "openid email profile",
    },
    "kakao": {
        "auth_url": "https://kauth.kakao.com/oauth/authorize",
        "token_url": "https://kauth.kakao.com/oauth/token",
        "profile_url": "https://kapi.kakao.com/v2/user/me",
        "client_id_env": "KAKAO_REST_API_KEY",
        "client_secret_env": "KAKAO_CLIENT_SECRET",
        "scope": "profile_nickname",
    },
    "naver": {
        "auth_url": "https://nid.naver.com/oauth2.0/authorize",
        "token_url": "https://nid.naver.com/oauth2.0/token",
        "profile_url": "https://openapi.naver.com/v1/nid/me",
        "client_id_env": "NAVER_CLIENT_ID",
        "client_secret_env": "NAVER_CLIENT_SECRET",
        "scope": "name email nickname",
    },
}


def get_provider(provider):
    provider = (provider or "").lower()
    if provider not in PROVIDERS:
        raise ValidationError({"provider": "Unsupported social provider."})
    return provider, PROVIDERS[provider]


def get_redirect_uri(provider, explicit_redirect_uri=None):
    if explicit_redirect_uri:
        return explicit_redirect_uri
    frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5173").rstrip("/")
    return f"{frontend_base_url}/social/callback/{provider}"


def build_authorization_url(provider, redirect_uri=None):
    provider, config = get_provider(provider)
    client_id = os.getenv(config["client_id_env"], "")
    if not client_id:
        raise ValidationError({"detail": f"{config['client_id_env']} is not configured."})

    state = secrets.token_urlsafe(24)
    redirect_uri = get_redirect_uri(provider, redirect_uri)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    if config.get("scope"):
        params["scope"] = config["scope"]
    return {
        "provider": provider,
        "authorization_url": f"{config['auth_url']}?{urlencode(params)}",
        "state": state,
        "redirect_uri": redirect_uri,
    }


def request_token(provider, code, redirect_uri, state=None):
    provider, config = get_provider(provider)
    client_id = os.getenv(config["client_id_env"], "")
    client_secret = os.getenv(config["client_secret_env"], "")
    if not client_id:
        raise ValidationError({"detail": f"{config['client_id_env']} is not configured."})
    if provider in {"google", "naver"} and not client_secret:
        raise ValidationError({"detail": f"{config['client_secret_env']} is not configured."})

    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    if client_secret:
        data["client_secret"] = client_secret
    if provider == "naver" and state:
        data["state"] = state

    response = requests.post(config["token_url"], data=data, timeout=10)
    if response.status_code >= 400:
        raise SocialAuthError(provider_error_message(provider, response))
    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise SocialAuthError("Social provider did not return an access token.")
    return access_token


def request_profile(provider, access_token):
    provider, config = get_provider(provider)
    response = requests.get(
        config["profile_url"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if response.status_code >= 400:
        raise SocialAuthError("Could not load social profile.")
    payload = response.json()

    if provider == "google":
        return {
            "social_id": payload.get("sub"),
            "email": payload.get("email", ""),
            "nickname": payload.get("name") or payload.get("given_name") or "Google User",
        }

    if provider == "kakao":
        account = payload.get("kakao_account", {})
        profile = account.get("profile", {})
        return {
            "social_id": str(payload.get("id")),
            "email": account.get("email", ""),
            "nickname": profile.get("nickname") or "Kakao User",
        }

    naver_profile = payload.get("response", {})
    return {
        "social_id": naver_profile.get("id"),
        "email": naver_profile.get("email", ""),
        "nickname": naver_profile.get("nickname") or naver_profile.get("name") or "Naver User",
    }


def unique_username(base):
    User = get_user_model()
    cleaned = slugify(base).replace("-", "_") or "social_user"
    username = cleaned[:130]
    suffix = 1
    candidate = username
    while User.objects.filter(username=candidate).exists():
        suffix_text = f"_{suffix}"
        candidate = f"{username[:150 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return candidate


def get_or_create_social_user(provider, profile):
    User = get_user_model()
    social_id = profile.get("social_id")
    if not social_id:
        raise SocialAuthError("Social profile is missing an id.")

    username = f"{provider}_{social_id}"
    user = User.objects.filter(username=username).first()
    if not user and profile.get("email"):
        user = User.objects.filter(email=profile["email"]).first()

    if not user:
        user = User(
            username=unique_username(username),
            email=profile.get("email", ""),
            nickname=profile.get("nickname", ""),
        )
        user.set_unusable_password()
        user.save()
    else:
        changed = False
        if profile.get("email") and not user.email:
            user.email = profile["email"]
            changed = True
        if profile.get("nickname") and not user.nickname:
            user.nickname = profile["nickname"]
            changed = True
        if changed:
            user.save(update_fields=["email", "nickname"])
    return user


def authenticate_social(provider, code, redirect_uri=None, state=None):
    provider, _ = get_provider(provider)
    redirect_uri = get_redirect_uri(provider, redirect_uri)
    access_token = request_token(provider, code, redirect_uri, state)
    profile = request_profile(provider, access_token)
    return get_or_create_social_user(provider, profile)



