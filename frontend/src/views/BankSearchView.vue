<script setup>
import { nextTick, onMounted, ref } from "vue";

import { apiFetch } from "../api/client";

const keyword = ref("멀티캠퍼스 역삼");
const kakaoKey = ref("");
const message = ref("");
const mapEl = ref(null);
const banks = ref([]);
let map = null;
let geocoder = null;
let places = null;
let markers = [];
let routeLine = null;
const start = { lat: 37.5012743, lng: 127.039585 };

function loadKakaoScript(key) {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps?.services) {
      resolve();
      return;
    }

    const existing = document.querySelector("script[data-kakao-map]");
    if (existing) {
      existing.addEventListener("load", () => window.kakao.maps.load(resolve), { once: true });
      existing.addEventListener("error", reject, { once: true });
      return;
    }

    const script = document.createElement("script");
    script.dataset.kakaoMap = "true";
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${key}&libraries=services&autoload=false`;
    script.onload = () => window.kakao.maps.load(resolve);
    script.onerror = () => reject(new Error("Kakao Maps SDK를 불러오지 못했습니다."));
    document.head.appendChild(script);
  });
}

function clearMap() {
  markers.forEach(marker => marker.setMap(null));
  markers = [];
  if (routeLine) {
    routeLine.setMap(null);
    routeLine = null;
  }
}

function drawRoute(bank) {
  if (!map || !window.kakao) return;
  const kakao = window.kakao;
  const from = new kakao.maps.LatLng(start.lat, start.lng);
  const to = new kakao.maps.LatLng(Number(bank.y), Number(bank.x));
  if (routeLine) routeLine.setMap(null);
  routeLine = new kakao.maps.Polyline({
    path: [from, to],
    strokeWeight: 5,
    strokeColor: "#2f80ed",
    strokeOpacity: 0.9,
    strokeStyle: "solid"
  });
  routeLine.setMap(map);
  map.panTo(to);
}

function renderBanks(data) {
  const kakao = window.kakao;
  clearMap();
  banks.value = data.slice(0, 10);
  if (!banks.value.length) {
    message.value = "주변 은행을 찾지 못했습니다. 검색어를 조금 더 구체적으로 입력해보세요.";
    return;
  }

  message.value = "";
  const bounds = new kakao.maps.LatLngBounds();
  banks.value.forEach(bank => {
    const position = new kakao.maps.LatLng(Number(bank.y), Number(bank.x));
    const marker = new kakao.maps.Marker({ map, position });
    markers.push(marker);
    bounds.extend(position);
    kakao.maps.event.addListener(marker, "click", () => drawRoute(bank));
  });
  map.setBounds(bounds);
}

function searchPlacesByKeyword(searchKeyword, fallbackPosition) {
  places.keywordSearch("은행", (data, searchStatus) => {
    if (searchStatus === window.kakao.maps.services.Status.OK) {
      renderBanks(data);
      return;
    }
    map.setCenter(fallbackPosition);
    renderBanks([]);
  }, { location: fallbackPosition, radius: 1800 });
}

function searchBanks() {
  if (!places || !geocoder || !map) {
    message.value = "지도가 아직 준비되지 않았습니다.";
    return;
  }

  const kakao = window.kakao;
  const fallbackCenter = new kakao.maps.LatLng(start.lat, start.lng);
  const query = keyword.value.trim();

  if (!query) {
    map.setCenter(fallbackCenter);
    searchPlacesByKeyword("은행", fallbackCenter);
    return;
  }

  geocoder.addressSearch(query, (result, status) => {
    if (status === kakao.maps.services.Status.OK && result.length) {
      const center = new kakao.maps.LatLng(Number(result[0].y), Number(result[0].x));
      map.setCenter(center);
      searchPlacesByKeyword("은행", center);
      return;
    }

    places.keywordSearch(query, (placeResult, placeStatus) => {
      const center = placeStatus === kakao.maps.services.Status.OK && placeResult.length
        ? new kakao.maps.LatLng(Number(placeResult[0].y), Number(placeResult[0].x))
        : fallbackCenter;
      map.setCenter(center);
      searchPlacesByKeyword("은행", center);
    });
  });
}

onMounted(async () => {
  try {
    const data = await apiFetch("/map/config/");
    kakaoKey.value = data.kakao_js_key;
    if (!kakaoKey.value) {
      message.value = "KAKAO_JS_KEY가 없습니다. backend/.env에 Kakao JavaScript 키를 등록해주세요.";
      return;
    }

    await loadKakaoScript(kakaoKey.value);
    await nextTick();

    const kakao = window.kakao;
    map = new kakao.maps.Map(mapEl.value, {
      center: new kakao.maps.LatLng(start.lat, start.lng),
      level: 4
    });
    geocoder = new kakao.maps.services.Geocoder();
    places = new kakao.maps.services.Places();
    searchBanks();
  } catch (err) {
    const origin = window.location.origin;
    message.value = `${err.message} Kakao Developers의 Web 플랫폼에 ${origin} 도메인이 등록되어 있는지 확인해주세요. 키를 바꿨다면 백엔드 서버도 다시 시작해야 합니다.`;
  }
});
</script>

<template>
  <main class="container">
    <div class="section-head">
      <h1>근처 은행 찾기</h1>
      <p>Kakao Maps API로 입력한 위치 주변 은행을 지도에 표시합니다.</p>
    </div>
    <div class="filter-bar two">
      <input v-model="keyword" placeholder="위치 또는 주소" @keyup.enter="searchBanks">
      <button class="btn primary" type="button" @click="searchBanks">검색</button>
    </div>
    <p v-if="message" class="status-block warning">{{ message }}</p>
    <section class="map-layout">
      <div ref="mapEl" class="map-box">
        <div v-if="!kakaoKey" class="map-placeholder">Kakao 지도 영역</div>
      </div>
      <div class="content-panel">
        <h2>검색 결과</h2>
        <p class="muted">은행을 선택하면 멀티캠퍼스 역삼 기준 경로가 표시됩니다.</p>
        <ul class="plain-list result-list">
          <li v-for="bank in banks" :key="bank.id">
            <strong>{{ bank.place_name }}</strong>
            <span>{{ bank.road_address_name || bank.address_name }}</span>
            <button class="btn ghost small" type="button" @click="drawRoute(bank)">경로 보기</button>
          </li>
          <li v-if="!banks.length" class="muted">위치를 검색하면 주변 은행이 표시됩니다.</li>
        </ul>
      </div>
    </section>
  </main>
</template>
