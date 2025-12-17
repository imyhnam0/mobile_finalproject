# 안드로이드 클라이언트 - 낙상 감지 시스템

이 앱은 서버에 저장된 낙상 이벤트를 조회하고 이미지 리스트로 표시하는 안드로이드 클라이언트입니다.

## 주요 기능

- **낙상 이벤트 목록 조회**: 서버에서 모든 낙상 이벤트를 가져와 RecyclerView로 표시
- **이미지 표시**: 각 이벤트의 이미지를 Glide를 사용하여 로드 및 표시
- **기간별 필터링**: 날짜 범위로 이벤트 필터링 (API 지원)
- **새로고침**: FAB 버튼을 통한 목록 새로고침

## 프로젝트 구조

```
app/src/main/java/com/example/mobile/
├── api/
│   ├── FallEvent.java          # 낙상 이벤트 모델
│   ├── ApiService.java          # Retrofit API 인터페이스
│   └── RetrofitClient.java      # Retrofit 클라이언트 설정
├── ui/
│   └── FallEventAdapter.java    # RecyclerView 어댑터
└── MainActivity.java            # 메인 액티비티

app/src/main/res/layout/
├── activity_fall_events.xml     # 메인 레이아웃
└── item_fall_event.xml          # 리스트 아이템 레이아웃
```

## 사용된 라이브러리

- **Retrofit 2.11.0**: HTTP RESTful API 클라이언트
- **Gson**: JSON 직렬화/역직렬화
- **RecyclerView**: 리스트 표시
- **Glide 4.16.0**: 이미지 로딩 및 캐싱
- **CardView**: 카드 스타일 UI

## 설정

### 1. 서버 URL 설정

`RetrofitClient.java` 파일에서 서버 주소를 변경하세요:

```java
// Android 에뮬레이터용 (localhost)
private static final String BASE_URL = "http://10.0.2.2:8000/";

// 실제 디바이스 또는 다른 서버
// private static final String BASE_URL = "http://YOUR_SERVER_IP:8000/";
```

### 2. 인터넷 권한

`AndroidManifest.xml`에 인터넷 권한이 추가되어 있습니다:

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 3. 네트워크 보안 설정 (HTTP 사용 시)

HTTP를 사용하는 경우 `AndroidManifest.xml`의 `<application>` 태그에 추가:

```xml
<application
    ...
    android:usesCleartextTraffic="true">
```

## API 엔드포인트

### 낙상 이벤트 목록 조회
```
GET /api/fall-events/list/
```

### 기간별 필터링
```
GET /api/fall-events/list/?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z
```

## 빌드 및 실행

1. 프로젝트를 Android Studio에서 엽니다
2. Gradle 동기화를 수행합니다
3. 서버가 실행 중인지 확인합니다 (기본: http://localhost:8000)
4. 앱을 빌드하고 실행합니다

## 문제 해결

### 이미지가 표시되지 않는 경우
- 서버의 `image_url`이 올바른지 확인
- 네트워크 연결 확인
- Glide 로그 확인: `adb logcat | grep Glide`

### API 호출 실패
- 서버 URL이 올바른지 확인
- 서버가 실행 중인지 확인
- 네트워크 권한이 올바르게 설정되었는지 확인

### 빌드 오류
- `libs.versions.toml`에 필요한 라이브러리 버전이 모두 추가되었는지 확인
- Gradle 캐시 정리: `./gradlew clean`
