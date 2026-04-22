# Market Info — Design System
> 버전: v1.0 | 작성일: 2026-04-21 | 플랫폼: Flutter (iOS / Android)

---

## 목차
0. [디자인 툴 체인](#0-디자인-툴-체인)
1. [색상 시스템](#1-색상-시스템)
2. [타이포그래피](#2-타이포그래피)
3. [간격 & 레이아웃 토큰](#3-간격--레이아웃-토큰)
4. [컴포넌트 스펙](#4-컴포넌트-스펙)
5. [아이콘 스타일](#5-아이콘-스타일)
6. [모션 & 인터랙션](#6-모션--인터랙션)
7. [접근성 기준](#7-접근성-기준)

---

## 0. 디자인 툴 체인

### 0.1 작업 순서 (고정)
1. **Stitch AI**: 화면 구조/레이아웃 초안 생성 (정보 구조, 섹션 우선순위, 카드 밀도 검증)
2. **Figma**: 컴포넌트/오토레이아웃/토큰/인터랙션 정밀화
3. **Flutter 반영**: Figma 확정안 기준으로 개발 구현

### 0.2 역할 분리 원칙
- Stitch AI는 아이디어 탐색과 빠른 레이아웃 실험에만 사용한다.
- 최종 시안, 컴포넌트 규격, 토큰 값, 인터랙션 기준은 Figma를 단일 기준(SSOT)으로 사용한다.
- 핸드오프는 Figma Frame/Component/Variant 이름을 API 및 Screen ID와 동일하게 맞춘다.

### 0.3 파일/버전 운영
- Figma 페이지 권장: `00_Foundation`, `01_Components`, `02_Screens_MVP`, `03_Prototype`, `99_Handoff`
- Stitch AI 산출물은 Figma `Exploration` 페이지에 보관하고 최종 페이지와 분리한다.
- 릴리스 태그: `vMAJOR.MINOR.PATCH` (예: `v1.1.0-mvp-ui-freeze`)

## 1. 색상 시스템

### 1.1 컬러 램프 (4개 팔레트)

#### Primary — Forest Green
브랜드 아이덴티티 컬러. CTA 버튼, 탭 활성, 구독 토글, 핵심 액션에 사용.

| Token | Hex | 용도 |
|---|---|---|
| `green-50` | `#F2F7EC` | 화면 배경, 보조 영역 fill |
| `green-100` | `#D4E8BA` | 상태 배지 "있음·예정", subtle fill |
| `green-200` | `#A8D175` | 보조 border, 구분선 강조 |
| `green-400` | `#72AA34` | 미사용 (중간 톤 참조용) |
| `green-600` | `#4A7D1A` | **Primary CTA 버튼 bg**, 탭 활성 아이콘 |
| `green-800` | `#2F5710` | 가격 텍스트, 강조 본문 |
| `green-900` | `#1A3408` | 섹션 헤드라인 (세리프 위 텍스트 최강조) |

#### Accent — Warm Ivory
카드 배경, 행사·스포트라이트 섹션, 온기 있는 서브 톤.

| Token | Hex | 용도 |
|---|---|---|
| `ivory-50` | `#FDFBF5` | 메인 카드 배경 (White 대신) |
| `ivory-100` | `#F5EDD4` | 점포 스포트라이트 카드 bg |
| `ivory-200` | `#EAD8A3` | 아이콘 컨테이너 배경 |
| `ivory-400` | `#D4B466` | 행사 border, 구분선 |
| `ivory-600` | `#A8852E` | 보조 텍스트 (Ivory 배경 위) |
| `ivory-800` | `#7A5E18` | 스포트라이트 본문 텍스트 |
| `ivory-900` | `#4D3A0A` | 스포트라이트 강조 타이틀 |

#### Drop Highlight — Terracotta
드랍(입고 이벤트) 전용 포인트 컬러. 히어로 카드, 마감임박 배지, 드랍 CTA에만 집중 사용.

| Token | Hex | 용도 |
|---|---|---|
| `terra-50` | `#FBF0EA` | 드랍 카드 배경 (예정 상태) |
| `terra-100` | `#F5CDB5` | 드랍 border |
| `terra-200` | `#EBA57D` | 드랍 섹션 구분선 |
| `terra-400` | `#D4663A` | **드랍 CTA 버튼 bg** |
| `terra-600` | `#A34220` | 드랍 배지 텍스트, 지연 알림 텍스트 |
| `terra-800` | `#6E2B12` | 드랍 상세 가격 텍스트 |
| `terra-900` | `#3F1808` | 드랍 카드 타이틀 (Terracotta 배경 위) |

#### Neutral — Stone
본문 텍스트, 구분선, 비활성 상태. 순수 회색 대신 따뜻한 Stone 톤 사용.

| Token | Hex | 용도 |
|---|---|---|
| `stone-50` | `#F7F6F3` | 상인 홈 배경, 보조 화면 bg |
| `stone-100` | `#E8E5DE` | 구분선, Skeleton 베이스 |
| `stone-200` | `#C8C4BB` | 비활성 border |
| `stone-400` | `#928E84` | 보조 텍스트 (Caption 등) |
| `stone-600` | `#625E55` | 보조 정보 텍스트 (Body 2) |
| `stone-800` | `#3D3B34` | 본문 텍스트 (Body 1) |
| `stone-900` | `#1E1D18` | 강조 본문, 상품명 |

---

### 1.2 의미 기반 색상 매핑

#### 상태 배지 — 재고

| 상태 | 배경 | 텍스트 | Token |
|---|---|---|---|
| 있음 (in_stock) | `green-100` `#D4E8BA` | `green-800` `#2F5710` | badge-stock-available |
| 적음 (low_stock) | `ivory-100` `#F5EDD4` | `ivory-800` `#7A5E18` | badge-stock-low |
| 품절 (out_of_stock) | `stone-100` `#E8E5DE` | `stone-800` `#3D3B34` | badge-stock-none |

#### 상태 배지 — 드랍

| 상태 | 배경 | 텍스트 | Token |
|---|---|---|---|
| 예정 (scheduled) | `green-100` `#D4E8BA` | `green-800` `#2F5710` | badge-drop-scheduled |
| 확정 (arrived) | `green-600` `#4A7D1A` | `green-50` `#F2F7EC` | badge-drop-arrived |
| 마감 (sold_out) | `stone-100` `#E8E5DE` | `stone-800` `#3D3B34` | badge-drop-soldout |

> MVP 상태 소스는 DB/API 기준(`scheduled`, `arrived`, `sold_out`)을 따른다.  
> `delayed`, `cancelled` 상태는 추후 API 확장(또는 운영 이벤트 타입 분리) 시 추가한다.

#### 콘텐츠 태그

| 태그 | 배경 | 텍스트 |
|---|---|---|
| 마감임박 | `terra-400` `#D4663A` | `terra-50` `#FBF0EA` |
| 신규 | `green-600` `#4A7D1A` | `green-50` `#F2F7EC` |
| 인기 | `ivory-100` `#F5EDD4` | `ivory-800` `#7A5E18` |
| 갱신필요 | `stone-100` `#E8E5DE` | `stone-800` `#3D3B34` |

---

### 1.3 화면 유형별 배경 색상

| 화면 | 배경 | 카드 배경 |
|---|---|---|
| 소비자 홈 (SCR-C-01) | `green-50` | `ivory-50` |
| 드랍 리스트 (SCR-C-04) | `terra-50` (히어로 섹션) / `green-50` (리스트) | `ivory-50` |
| 점포 스포트라이트 (SCR-C-11) | `green-50` | `ivory-100` |
| 검색 / 상세 (SCR-C-02/03) | white | `ivory-50` |
| 상인 홈 (SCR-M-01) | `stone-50` | white |
| 로그인 (SCR-A-01) | white | `ivory-50` |

---

## 2. 타이포그래피

### 2.1 폰트 패밀리

| 역할 | 폰트 | 굵기 | Figma 연결 방법 |
|---|---|---|---|
| Headline / Display / H1–H2 | Jua | Regular(400) | Figma Google Fonts |
| H3 / Body / UI / Label | Noto Sans | Regular(400), Medium(500), Bold(700) | Figma Google Fonts |
| Fallback (웹/코드) | `'Noto Sans', 'Apple SD Gothic Neo', sans-serif` | — | — |

> **폰트 소스**: Google Fonts (`Noto Sans`, `Jua`) 사용.

---

### 2.2 타입 스케일 (Flutter sp 기준)

| Role | 폰트 | Size | Weight | Line Height | Letter Spacing | 사용 위치 |
|---|---|---|---|---|---|---|
| `display` | Jua | 28sp | 400 | 1.20 | -0.01em | 섹션 히어로 제목, 드랍 히어로 |
| `h1` | Jua | 22sp | 400 | 1.25 | -0.01em | 화면 주요 타이틀 |
| `h2` | Jua | 18sp | 400 | 1.30 | 0 | 서브 타이틀, 점포명 강조 |
| `h3` | Noto Sans | 16sp | 700 | 1.40 | 0 | 섹션 레이블, 카드 그룹명 |
| `body1` | Noto Sans | 15sp | 400 | 1.60 | 0 | 상품명, 가격, 주요 정보 |
| `body2` | Noto Sans | 13sp | 400 | 1.60 | 0 | 보조 정보 (점포명, 시각, 상태 설명) |
| `caption` | Noto Sans | 12sp | 400 | 1.50 | 0 | 업데이트 시각, 힌트 텍스트 |
| `label` | Noto Sans | 11sp | 700 | 1.40 | +0.04em | 배지, 태그, 탭 레이블 |
| `button` | Noto Sans | 15sp | 700 | 1.00 | 0 | 버튼 텍스트 |
| `button-sm` | Noto Sans | 13sp | 700 | 1.00 | 0 | 소형 버튼 (인라인 CTA) |

---

### 2.3 텍스트 색상 규칙

- 기본 본문: `stone-900` (`#1E1D18`)
- 보조 정보: `stone-600` (`#625E55`)
- 힌트 / Caption: `stone-400` (`#928E84`)
- 가격 강조: `green-800` (`#2F5710`)
- 에러 / 경고 텍스트: `terra-600` (`#A34220`)
- 컬러 배경 위 텍스트: 반드시 같은 계열 800/900 또는 50 stop 사용

---

## 3. 간격 & 레이아웃 토큰

### 3.1 기본 간격 토큰

| Token | Value | 사용처 |
|---|---|---|
| `spacing-4` | 4dp | 배지 내부 수직 패딩 |
| `spacing-8` | 8dp | 인라인 아이콘 ↔ 텍스트 간격 |
| `spacing-12` | 12dp | 카드 리스트 간격 (list gap) |
| `spacing-16` | 16dp | 화면 좌우 여백, 카드 내부 패딩 |
| `spacing-24` | 24dp | 섹션 간격 |
| `spacing-32` | 32dp | 주요 섹션 블록 간격 |
| `spacing-48` | 48dp | 화면 상단 여백 (safe area 제외) |

### 3.2 컴포넌트 크기 토큰

| Token | Value | 사용처 |
|---|---|---|
| `touch-target-min` | 44dp | 모든 탭 가능한 요소 최소 크기 |
| `button-height-lg` | 48dp | Primary CTA (full-width) |
| `button-height-md` | 44dp | Secondary 버튼 |
| `button-height-sm` | 40dp | Accent 버튼 (드랍 등) |
| `button-height-xs` | 36dp | Tertiary / 취소 버튼 |
| `bottom-nav-height` | 56dp + safe area | 하단 탭바 |
| `app-bar-height` | 56dp | 상단 앱바 |
| `icon-size-default` | 24dp | 기본 아이콘 |
| `icon-size-sm` | 16dp | 배지 내 아이콘 |

### 3.3 모서리 반경 토큰

| Token | Value | 사용처 |
|---|---|---|
| `radius-sm` | 6dp | 배지, 태그 pill |
| `radius-md` | 8dp | 소형 버튼, 입력 필드 |
| `radius-lg` | 12dp | 카드 (리스트 카드, 이벤트 카드) |
| `radius-xl` | 16dp | 히어로 카드, 드랍 카드 |
| `radius-sheet` | 20dp | 바텀시트 상단 (top-only) |

---

## 4. 컴포넌트 스펙

### 4.1 버튼 시스템

#### Primary CTA
```
height: 48dp
border-radius: radius-lg (12dp)
background: green-600 (#4A7D1A)
text-color: green-50 (#F2F7EC)
text-style: button (15sp, 700)
padding: 0 24dp
상태: hover brightness(0.93), press scale(0.96), disabled opacity(0.4)
```

#### Secondary (Outlined)
```
height: 44dp
border-radius: radius-lg (12dp)
background: green-50 (#F2F7EC)
border: 1.5dp solid green-600 (#4A7D1A)
text-color: green-800 (#2F5710)
text-style: button (15sp, 700)
```

#### Accent — Drop
```
height: 40dp
border-radius: radius-lg (12dp)
background: terra-400 (#D4663A)
text-color: terra-50 (#FBF0EA)
text-style: button-sm (13sp, 700)
```

#### Accent — Drop (Subtle)
```
height: 40dp
border-radius: radius-lg (12dp)
background: terra-50 (#FBF0EA)
text-color: terra-600 (#A34220)
text-style: button-sm (13sp, 700)
```

#### Tertiary
```
height: 36dp
border-radius: radius-md (8dp)
background: stone-100 (#E8E5DE) 또는 transparent
text-color: stone-600 (#625E55)
text-style: button-sm (13sp, 400)
```

---

### 4.2 리스트 카드

#### 기본 카드 구조
```
background: ivory-50 (#FDFBF5)
border: 0.5dp solid stone-100 (#E8E5DE)
border-radius: radius-lg (12dp)
padding: spacing-16 (all sides)
```

#### 드랍 카드 (이벤트 강조)
```
background: terra-50 (#FBF0EA)
border: 0.5dp solid terra-100 (#F5CDB5)
border-radius: radius-xl (16dp)
padding: spacing-16
```

#### 스포트라이트 카드
```
background: ivory-100 (#F5EDD4)
border: 0.5dp solid ivory-400 (#D4B466)
border-radius: radius-lg (12dp)
padding: spacing-16
```

#### 카드 내부 구조
```
[이미지] (optional) — 너비 64dp, 높이 64dp, radius-md
[타이틀] — body1 (15sp, 700), stone-900
[보조 정보] — body2 (13sp, 400), stone-600
[가격] — body1 (15sp, 700), green-800
[상태 배지] — label (11sp, 700), 규정 색상
[업데이트 시각] — caption (12sp, 400), stone-400
[CTA 버튼] — 오른쪽 정렬 또는 하단 full-width
```

---

### 4.3 상태 배지 컴포넌트

```
height: 22dp
padding: 3dp 10dp
border-radius: radius-sm (6dp)
text-style: label (11sp, 700)
색상: 1.2 매핑 테이블 참조
```

---

### 4.4 검색바

```
height: 44dp
border-radius: radius-md (8dp)
background: white (light) / stone-50 (dark)
border: 0.5dp solid stone-200 (#C8C4BB)
focus-border: 1.5dp solid green-600 (#4A7D1A)
padding: 0 spacing-16
icon: 검색 아이콘 (24dp, stone-400)
placeholder-color: stone-400 (#928E84)
text-style: body1 (15sp, 400)
```

---

### 4.5 하단 탭바

```
height: 56dp + bottom safe area
background: white (opacity 0.95, blur 없음)
border-top: 0.5dp solid stone-100 (#E8E5DE)
탭 개수: 5 (홈 / 검색 / 장보기 / 지도 / 마이)
아이콘: 24dp, stroke 2dp
활성 아이콘: green-600 (#4A7D1A)
비활성 아이콘: stone-400 (#928E84)
활성 레이블: label (11sp, 700), green-600
비활성 레이블: label (11sp, 400), stone-400
```

---

### 4.6 바텀시트

```
border-radius: 20dp 20dp 0 0 (상단만)
background: white
handle: 4dp × 32dp, stone-200, 상단 8dp 여백
dim-overlay: stone-900 opacity 0.45
drag-dismiss: 아래로 120dp 이상 드래그 시 닫힘
```

---

### 4.7 에러 / 빈 상태 컴포넌트 (SCR-A-02)

```
아이콘: 48dp, stone-300
타이틀: h3 (16sp, 700, sans), stone-800
설명: body2 (13sp, 400), stone-600
CTA 버튼 1 (Primary): "다시 시도하기"
CTA 버튼 2 (Tertiary): "인근 시장 보기" 또는 상황별
간격: 타이틀 ↔ 설명 8dp, 설명 ↔ 버튼 24dp
```

---

### 4.8 스켈레톤 로딩

```
base-color: stone-100 (#E8E5DE)
shimmer-color: stone-50 (#F7F6F3)
shimmer-direction: left → right
shimmer-duration: 1400ms, linear, infinite
shimmer-sync: 화면 단위 동기화 (카드별 개별 shimmer 금지)
콘텐츠 진입: skeleton fadeOut 150ms → content fadeIn 200ms (stagger 40ms/카드)
```

---

## 5. 아이콘 스타일

### 5.1 원칙

- **스타일**: Outlined (선형), 2dp stroke, rounded join/linecap
- **기본 크기**: 24 × 24dp
- **소형**: 16 × 16dp (배지, 인라인)
- **색상**: 컨텍스트에 따라 green-600, terra-400, ivory-600, stone-400 중 선택
- **키치 요소 금지**: 그라데이션 fill, 과도한 장식선, 그림자 없음
- **Figma 소스**: `Lucide Icons` 플러그인 (기본 UI 아이콘) + 전통시장 전용 아이콘 직접 제작

### 5.2 아이콘 목록

#### 하단 탭 아이콘

| 아이콘 | Lucide 이름 | 비고 |
|---|---|---|
| 홈 | `Home` | — |
| 검색 | `Search` | — |
| 장보기 | `ShoppingBag` | — |
| 지도 | `MapPin` | — |
| 마이 | `User` | — |

#### 기능 아이콘

| 아이콘 | Lucide 이름 / 비고 |
|---|---|
| 알림 (벨) | `Bell` / `BellRing` (구독 시) |
| 드랍 (상승 트렌드) | `TrendingUp` |
| 캘린더 | `Calendar` |
| 장바구니 | `ShoppingCart` |
| 인증/뱃지 | `Shield` + `Check` 합성 |
| 업데이트 시각 | `Clock` |
| 상품 등록 | `FilePlus` |
| 즐겨찾기 | `Heart` |

#### 전통시장 전용 아이콘 (직접 제작)

| 아이콘 | 설명 |
|---|---|
| 시장 찾기 | MapPin + 하단 사람 실루엣, 2dp stroke |
| 점포 | 간략화된 가게 정면 (지붕+입구), 2dp stroke |
| 상인 | 인물 타원형 + 앞치마 암시, 2dp stroke |
| 추천 동선 | MapPin + 경로 점선, 2dp stroke |
| 스포트라이트 | 별(5각) outline, 2dp stroke |

---

## 6. 모션 & 인터랙션

### 6.1 화면 전환 (Navigation Transition)

| 전환 유형 | 상황 | 커브 | Duration |
|---|---|---|---|
| Push (slideInRight) | 카드·리스트 → 상세 | easeOutCubic (0.33, 1, 0.68, 1) | 280ms |
| Pop (slideOutRight) | 뒤로 가기 | easeInCubic (0.32, 0, 0.67, 0) | 240ms |
| Tab Switch | 하단 탭 전환 | easeOut | fade 200ms + scale 0.97→1.0 |
| Bottom Sheet | 드랍 상세, 알림 설정 | Spring (damping 0.8, stiffness 200) | 320ms |
| Modal / Overlay | 에러, 확인 다이얼로그 | easeOutBack | 220ms + scale 0.95→1.0 |

> Flutter 구현: `PageRouteBuilder` (Push/Pop), `showModalBottomSheet` (Sheet), `AnimationController + CurvedAnimation`

---

### 6.2 마이크로 인터랙션

#### 버튼 탭 피드백
```
trigger: onTapDown
animation: scale 1.0 → 0.96 → 1.0
duration: 120ms, easeInOut
적용 범위: 모든 탭 가능한 요소 (GestureDetector / InkWell)
```

#### 알림 토글 (드랍 구독)
```
ON:
  - border fill: stone-200 → green-600, 200ms easeOut
  - 아이콘: Bell → BellRing, scale 1.0→1.2→1.0, 300ms spring
  - 햅틱: HapticFeedback.mediumImpact (iOS) / HapticFeedback.vibrate (Android)

OFF:
  - fill → transparent, 180ms easeIn
  - 아이콘: BellRing → Bell, scale 1.0→0.85→1.0, 220ms
```

#### 상태 배지 전환
```
드랍 상태 변경 (예정→확정 등):
  - crossfade: old fadeOut 150ms → new fadeIn 200ms
  - 배경색 전환: 200ms easeInOut
  - "확정" 진입 시 pulse 1회: scale 1→1.08→1, 400ms easeInOut

재고 상태 변경:
  - in_stock → low_stock: 배지 색상 전환 200ms
  - low_stock → out_of_stock: 텍스트 fadeOut + strikethrough 애니메이션
```

#### 장보기 리스트 체크
```
아이템 체크:
  - 체크박스 fill: 200ms easeOut (green-600)
  - 텍스트 strikethrough: width 0→100%, 200ms
  - 행 opacity: 1.0→0.5, 250ms
  - 햅틱: HapticFeedback.lightImpact

전체 완료:
  - 완료 배너 slideDown 300ms + green-50 배경 fadeIn
```

---

### 6.3 로딩 & 피드백

#### 스켈레톤 로딩
```
shimmer: left→right, 1400ms linear infinite
base: stone-100, highlight: stone-50
화면 단위 동기화
콘텐츠 진입 stagger: 카드별 40ms 딜레이 (최대 4장)
```

#### 토스트 알림
```
성공 토스트:
  - slideUp 240ms easeOut
  - auto-dismiss: 2200ms
  - slideDown 200ms
  - 배경: green-50, 아이콘: check

에러 토스트:
  - slideUp 240ms
  - auto-dismiss: 3500ms (재시도 버튼 있을 시 dismiss 없음)
  - 배경: terra-50

로딩 인디케이터:
  - circular, stroke green-600
  - rotate 1080ms linear infinite
  - 3초 초과 시 진행 메시지 텍스트 fadeIn
```

---

### 6.4 주요 흐름별 전환 시퀀스

#### 드랍 흐름 (핵심 경로)
```
홈 히어로카드 [Push →] 드랍 리스트 [Push →] 드랍 상세 Sheet [토글 마이크로] 알림 ON [토스트 피드백] 알림함
```

#### 검색 → 동선 흐름
```
검색바 expand 240ms [Push →] 검색 결과 [Push →] 상품 상세 [Push →] 장보기 리스트 [체크 마이크로] [Push →] 지도/동선
```

#### 상인 등록 흐름
```
상인 홈 FAB [Sheet UP →] 사진/음성 입력 [Push →] AI 분석 중 [로딩 인디케이터 →] crossfade 결과 검토 [성공 토스트 + Pop →] 상인 홈
```

---

### 6.5 모션 원칙 요약

| 원칙 | 내용 |
|---|---|
| **목적 중심** | 모든 애니메이션은 계층·방향·상태 전달 목적. 장식 모션 금지. |
| **속도 3단계** | 마이크로 100–150ms / 컴포넌트 200–280ms / 화면 전환 280–320ms |
| **커브 규칙** | 진입: easeOut(0.33,1,0.68,1) / 퇴장: easeIn(0.32,0,0.67,0) / 스프링: 바텀시트·토글만 |
| **감속 착지** | 모든 진입 애니메이션은 easeOut — 빠르게 시작, 부드럽게 착지 |

---

## 7. 접근성 기준

| 항목 | 기준 |
|---|---|
| 터치 타겟 | 최소 44 × 44dp |
| 본문 대비 명도 | 4.5:1 이상 (WCAG AA) |
| 상태 배지 | 색상 단독 의존 금지 — 텍스트 레이블 병행 필수 |
| 음성 입력 대체 | 텍스트 입력 폼 항상 병행 제공 |
| 로딩 피드백 | 3초 초과 시 진행 상태 메시지 노출 |
| 모션 접근성 | `prefers-reduced-motion: reduce` 감지 시 모든 duration 0ms — 상태 변화는 즉시, 정보 손실 없음 |
| 스크린 리더 | 배지·아이콘에 semanticsLabel 또는 Tooltip 필수 |

---

> **참고 문서**
> - `UIUX_Speification.md` — 화면별 컴포넌트 명세
> - `Fuctional_Specification.md` — 기능 요구사항 및 상태 정의
> - `Frontend_Execution_Plan.md` — Flutter 구현 액션 플랜
