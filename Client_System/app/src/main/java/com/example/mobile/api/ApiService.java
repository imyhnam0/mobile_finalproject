package com.example.mobile.api;

import java.util.List;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

/**
 * RESTful API 서비스 인터페이스
 * 낙상 이벤트 목록 및 상세 정보 조회
 */
public interface ApiService {
    /**
     * 모든 낙상 이벤트 목록 조회
     * GET /api/fall-events/list/
     */
    @GET("api/fall-events/list/")
    Call<List<FallEvent>> getFallEvents();

    /**
     * 기간별 필터링된 낙상 이벤트 목록 조회
     * GET /api/fall-events/list/?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z
     * 
     * @param startDate ISO 8601 형식의 시작 날짜 (예: "2025-12-01T00:00:00Z") - 선택적
     * @param endDate ISO 8601 형식의 종료 날짜 (예: "2025-12-31T23:59:59Z") - 선택적
     */
    @GET("api/fall-events/list/")
    Call<List<FallEvent>> getFallEvents(
            @Query("start_date") String startDate,
            @Query("end_date") String endDate
    );
}
