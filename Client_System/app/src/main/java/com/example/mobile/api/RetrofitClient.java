package com.example.mobile.api;

import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Retrofit 클라이언트 설정
 */
public class RetrofitClient {
    // 서버 기본 URL - 실제 서버 주소로 변경하세요
    private static final String BASE_URL = "http://10.0.2.2:8000/";  // Android 에뮬레이터용 localhost
    // 실제 디바이스나 에뮬레이터가 아닌 경우: "http://YOUR_SERVER_IP:8000/"

    private static Retrofit retrofit;
    private static ApiService apiService;

    /**
     * Retrofit 인스턴스 생성
     */
    public static Retrofit getRetrofitInstance() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }

    /**
     * ApiService 인스턴스 생성
     */
    public static ApiService getApiService() {
        if (apiService == null) {
            apiService = getRetrofitInstance().create(ApiService.class);
        }
        return apiService;
    }

    /**
     * BASE_URL 변경 (런타임에 서버 주소 변경 가능)
     */
    public static void setBaseUrl(String baseUrl) {
        retrofit = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        apiService = retrofit.create(ApiService.class);
    }
}
