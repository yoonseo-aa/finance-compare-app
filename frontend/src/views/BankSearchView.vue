<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";

import { apiFetch } from "../api/client";

const kakaoKey = ref("");
const message = ref("");
const loading = ref(true);
const mapEl = ref(null);
const banks = ref([]);
const activeBankId = ref("");
const currentAddress = ref("현재 위치를 확인하는 중입니다.");

let map = null;
let places = null;
let geocoder = null;
let currentMarker = null;
let bankMarkers = new Map();
const fallbackLocation = { lat: 37.5012743, lng: 127.039585 };
let currentLocation = { ...fallbackLocation };

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

function markerImage(active = false) {
  const kakao = window.kakao;
  const fill = active ? "#1d6ff2" : "#14a38b";
  const stroke = active ? "#dbeafe" : "#dff8f3";
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="42" height="50" viewBox="0 0 42 50"><path fill="${fill}" stroke="${stroke}" stroke-width="4" d="M21 3C11.1 3 3 10.9 3 20.7c0 12.8 18 26.3 18 26.3s18-13.5 18-26.3C39 10.9 30.9 3 21 3Z"/><path fill="#fff" d="M12 19.5 21 14l9 5.5v2H12v-2Zm2 3h3v7h-3v-7Zm5 0h4v7h-4v-7Zm6 0h3v7h-3v-7ZM12 31h18v2H12v-2Z"/></svg>`;
  const imageSrc = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  return new kakao.maps.MarkerImage(
    imageSrc,
    new kakao.maps.Size(42, 50),
    { offset: new kakao.maps.Point(21, 48) }
  );
}

function currentMarkerImage() {
  const kakao = window.kakao;
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 30 30"><circle cx="15" cy="15" r="12" fill="#3182f6" opacity=".18"/><circle cx="15" cy="15" r="7" fill="#3182f6" stroke="#fff" stroke-width="3"/></svg>';
  return new kakao.maps.MarkerImage(
    `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
    new kakao.maps.Size(30, 30),
    { offset: new kakao.maps.Point(15, 15) }
  );
}

function clearMarkers() {
  bankMarkers.forEach(marker => marker.setMap(null));
  bankMarkers = new Map();
}

function updateMarkerState() {
  bankMarkers.forEach((marker, bankId) => {
    marker.setImage(markerImage(bankId === activeBankId.value));
    marker.setZIndex(bankId === activeBankId.value ? 20 : 10);
  });
}

function selectBank(bankId, shouldPan = true) {
  const bank = banks.value.find(item => item._id === bankId);
  if (!bank || !map) return;

  activeBankId.value = bankId;
  updateMarkerState();

  if (shouldPan) {
    const kakao = window.kakao;
    map.panTo(new kakao.maps.LatLng(Number(bank.y), Number(bank.x)));
  }
}

function renderCurrentMarker(position) {
  const kakao = window.kakao;
  const latLng = new kakao.maps.LatLng(position.lat, position.lng);

  if (currentMarker) currentMarker.setMap(null);
  currentMarker = new kakao.maps.Marker({
    map,
    position: latLng,
    image: currentMarkerImage(),
    zIndex: 30
  });
}

function renderBanks(data) {
  const kakao = window.kakao;
  clearMarkers();

  banks.value = data.slice(0, 18).map((bank, index) => ({
    ...bank,
    _id: bank.id || `${bank.x}-${bank.y}-${index}`
  }));

  if (!banks.value.length) {
    activeBankId.value = "";
    message.value = "현재 위치 주변에서 은행을 찾지 못했습니다.";
    return;
  }

  message.value = "";
  const bounds = new kakao.maps.LatLngBounds();
  bounds.extend(new kakao.maps.LatLng(currentLocation.lat, currentLocation.lng));

  banks.value.forEach(bank => {
    const position = new kakao.maps.LatLng(Number(bank.y), Number(bank.x));
    const marker = new kakao.maps.Marker({
      map,
      position,
      image: markerImage(false),
      zIndex: 10
    });

    bankMarkers.set(bank._id, marker);
    bounds.extend(position);
    kakao.maps.event.addListener(marker, "click", () => selectBank(bank._id));
  });

  map.setBounds(bounds, 64, 64, 64, 64);
  selectBank(banks.value[0]._id, false);
}

function updateCurrentAddress(position) {
  if (!geocoder) return;

  geocoder.coord2Address(position.lng, position.lat, (result, status) => {
    if (status === window.kakao.maps.services.Status.OK && result.length) {
      currentAddress.value = result[0].road_address?.address_name || result[0].address.address_name;
      return;
    }
    currentAddress.value = "현재 위치 기준";
  });
}

function getCurrentPosition() {
  return new Promise(resolve => {
    if (!navigator.geolocation) {
      message.value = "브라우저에서 현재 위치를 사용할 수 없어 기본 위치 기준으로 보여드립니다.";
      resolve({ ...fallbackLocation });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      position => {
        resolve({ lat: position.coords.latitude, lng: position.coords.longitude });
      },
      () => {
        message.value = "현재 위치 권한을 허용하면 주변 은행을 더 정확하게 볼 수 있습니다. 지금은 기본 위치 기준입니다.";
        resolve({ ...fallbackLocation });
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
    );
  });
}

function searchNearbyBanks() {
  if (!places || !map) return;

  const kakao = window.kakao;
  const center = new kakao.maps.LatLng(currentLocation.lat, currentLocation.lng);
  map.setCenter(center);
  renderCurrentMarker(currentLocation);
  updateCurrentAddress(currentLocation);

  places.keywordSearch("은행", (data, status) => {
    loading.value = false;
    if (status === kakao.maps.services.Status.OK) {
      renderBanks(data);
      return;
    }
    renderBanks([]);
  }, {
    location: center,
    radius: 2500,
    sort: kakao.maps.services.SortBy.DISTANCE
  });
}

async function refreshCurrentLocation() {
  loading.value = true;
  currentAddress.value = "현재 위치를 확인하는 중입니다.";
  currentLocation = await getCurrentPosition();
  searchNearbyBanks();
}

onMounted(async () => {
  try {
    const data = await apiFetch("/map/config/");
    kakaoKey.value = data.kakao_js_key;
    if (!kakaoKey.value) {
      message.value = "KAKAO_JS_KEY가 없습니다. backend/.env에 Kakao JavaScript 키를 등록해주세요.";
      loading.value = false;
      return;
    }

    await loadKakaoScript(kakaoKey.value);
    await nextTick();

    const kakao = window.kakao;
    currentLocation = await getCurrentPosition();
    map = new kakao.maps.Map(mapEl.value, {
      center: new kakao.maps.LatLng(currentLocation.lat, currentLocation.lng),
      level: 4
    });
    map.setZoomable(true);
    geocoder = new kakao.maps.services.Geocoder();
    places = new kakao.maps.services.Places();
    searchNearbyBanks();
  } catch (err) {
    loading.value = false;
    const origin = window.location.origin;
    message.value = `${err.message} Kakao Developers의 Web 플랫폼에 ${origin} 도메인이 등록되어 있는지 확인해주세요. 키를 바꿨다면 백엔드 서버도 다시 시작해야 합니다.`;
  }
});

onBeforeUnmount(() => {
  clearMarkers();
  if (currentMarker) currentMarker.setMap(null);
});
</script>

<template>
  <main class="bank-page">
    <section class="bank-page-head">
      <div>
        <span class="page-kicker">Nearby banks</span>
        <h1>근처 은행 찾기</h1>
        <p>{{ currentAddress }}</p>
      </div>
      <button class="btn primary locate-button" type="button" @click="refreshCurrentLocation">
        현재 위치 새로고침
      </button>
    </section>

    <p v-if="message" class="status-block warning bank-message">{{ message }}</p>

    <section class="bank-map-shell">
      <div class="bank-map-card">
        <div ref="mapEl" class="bank-map-box">
          <div v-if="!kakaoKey || loading" class="map-placeholder">
            {{ loading ? "주변 은행을 찾는 중입니다." : "Kakao 지도 영역" }}
          </div>
        </div>
      </div>

      <aside class="bank-list-panel">
        <div class="bank-list-head">
          <div>
            <h2>주변 은행</h2>
            <p>가까운 순서로 최대 {{ banks.length }}개를 보여줍니다.</p>
          </div>
          <span>{{ banks.length }}곳</span>
        </div>

        <ul class="bank-result-list" aria-label="주변 은행 목록">
          <li v-for="bank in banks" :key="bank._id">
            <button
              class="bank-result-card"
              :class="{ active: activeBankId === bank._id }"
              type="button"
              @click="selectBank(bank._id)"
            >
              <span class="bank-icon" aria-hidden="true">{{ activeBankId === bank._id ? "●" : "○" }}</span>
              <span class="bank-copy">
                <strong>{{ bank.place_name }}</strong>
                <small>{{ bank.road_address_name || bank.address_name }}</small>
                <em v-if="bank.distance">현재 위치에서 {{ Number(bank.distance).toLocaleString() }}m</em>
              </span>
            </button>
          </li>
          <li v-if="!banks.length" class="empty-bank-list">
            {{ loading ? "은행 목록을 불러오고 있습니다." : "표시할 은행이 없습니다." }}
          </li>
        </ul>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.bank-page {
  --bank-ink: #172033;
  --bank-muted: #6f7c90;
  --bank-line: #dce7f2;
  --bank-blue: #3182f6;
  --bank-mint: #12a594;
  --bank-soft: #f5f8fc;
  width: min(1180px, calc(100% - 2rem));
  height: calc(100vh - 72px);
  min-height: 640px;
  margin: 0 auto;
  padding: 1.25rem 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: .85rem;
}

.bank-page-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  flex: 0 0 auto;
}

.page-kicker {
  color: var(--bank-mint);
  font-size: .84rem;
  font-weight: 900;
}

.bank-page-head h1 {
  margin: .2rem 0 .35rem;
  color: var(--bank-ink);
  font-size: clamp(1.9rem, 4vw, 3rem);
  line-height: 1.12;
}

.bank-page-head p {
  margin: 0;
  color: var(--bank-muted);
  font-weight: 700;
}

.locate-button {
  min-height: 44px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--bank-blue), var(--bank-mint));
  white-space: nowrap;
}

.bank-message {
  flex: 0 0 auto;
  margin: 0;
}

.bank-map-shell {
  min-height: 0;
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 1rem;
  align-items: stretch;
}

.bank-map-card,
.bank-list-panel {
  min-height: 0;
  border: 1px solid var(--bank-line);
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 14px 36px rgba(31, 44, 71, .07);
  overflow: hidden;
}

.bank-map-card {
  padding: .65rem;
}

.bank-map-box {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 460px;
  border-radius: 16px;
  overflow: hidden;
  background: #eef4f8;
}

.map-placeholder {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f7fbff, #edf7f5);
  color: var(--bank-muted);
  font-weight: 900;
}

.bank-list-panel {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.bank-list-head {
  display: flex;
  justify-content: space-between;
  gap: .8rem;
  align-items: start;
  padding-bottom: .8rem;
  border-bottom: 1px solid #edf2f7;
  flex: 0 0 auto;
}

.bank-list-head h2 {
  margin: 0 0 .25rem;
  color: var(--bank-ink);
  font-size: 1.35rem;
}

.bank-list-head p {
  margin: 0;
  color: var(--bank-muted);
  font-size: .9rem;
  font-weight: 700;
  line-height: 1.45;
}

.bank-list-head > span {
  border-radius: 999px;
  background: #edf7ff;
  color: #1d6ff2;
  padding: .28rem .58rem;
  font-weight: 900;
  white-space: nowrap;
}

.bank-result-list {
  list-style: none;
  margin: .85rem 0 0;
  padding: 0 .2rem 0 0;
  display: grid;
  gap: .62rem;
  max-height: calc((88px * 6) + (0.62rem * 5));
  overflow-y: auto;
  overscroll-behavior: contain;
}

.bank-result-list::-webkit-scrollbar {
  width: 8px;
}

.bank-result-list::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: #cbd7e6;
}

.bank-result-card {
  width: 100%;
  min-height: 88px;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: .7rem;
  align-items: center;
  border: 1px solid #e6edf5;
  border-radius: 16px;
  background: #fbfcfe;
  padding: .75rem;
  text-align: left;
  cursor: pointer;
  transition: border-color .16s ease, background .16s ease, box-shadow .16s ease, transform .16s ease;
}

.bank-result-card:hover {
  transform: translateY(-1px);
  border-color: rgba(18, 165, 148, .35);
  background: #fff;
}

.bank-result-card.active {
  border-color: rgba(49, 130, 246, .32);
  background: #f2f7ff;
  box-shadow: 0 10px 24px rgba(49, 130, 246, .12);
}

.bank-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #eaf8f5;
  color: var(--bank-mint);
  font-size: .9rem;
}

.bank-result-card.active .bank-icon {
  background: #e7f0ff;
  color: var(--bank-blue);
}

.bank-copy {
  min-width: 0;
  display: grid;
  gap: .22rem;
}

.bank-copy strong {
  color: var(--bank-ink);
  font-size: .98rem;
  line-height: 1.35;
}

.bank-copy small {
  color: var(--bank-muted);
  font-size: .84rem;
  line-height: 1.35;
}

.bank-copy em {
  color: #0b8f7c;
  font-size: .8rem;
  font-style: normal;
  font-weight: 900;
}

.empty-bank-list {
  display: grid;
  place-items: center;
  min-height: 160px;
  color: var(--bank-muted);
  font-weight: 800;
}

@media (max-width: 900px) {
  .bank-page {
    height: auto;
    min-height: calc(100vh - 72px);
    overflow: visible;
  }

  .bank-page-head,
  .bank-map-shell {
    display: grid;
  }

  .bank-map-shell {
    grid-template-columns: 1fr;
  }

  .bank-map-box {
    min-height: 420px;
  }

  .bank-result-list {
    max-height: 390px;
  }
}

@media (max-width: 560px) {
  .bank-page {
    width: min(100% - 1rem, 1180px);
    padding-top: 1rem;
  }

  .locate-button {
    width: 100%;
  }

  .bank-map-box {
    min-height: 340px;
  }
}
</style>
