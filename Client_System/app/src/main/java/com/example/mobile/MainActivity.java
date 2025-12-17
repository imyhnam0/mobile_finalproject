package com.example.mobile;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.mobile.api.ApiService;
import com.example.mobile.api.FallEvent;
import com.example.mobile.api.RetrofitClient;
import com.example.mobile.ui.FallEventAdapter;
import com.example.mobile.ui.ImageZoomDialog;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {
    private RecyclerView recyclerView;
    private FallEventAdapter adapter;
    private ProgressBar progressBar;
    private TextView errorTextView;
    private TextView emptyTextView;
    private FloatingActionButton fabRefresh;
    
    private Handler handler;
    private Runnable checkNewEventsRunnable;
    private static final long CHECK_INTERVAL = 10000; // 10초마다 체크
    private int lastEventId = -1; // 마지막으로 확인한 이벤트 ID

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fall_events);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // UI 초기화
        recyclerView = findViewById(R.id.recyclerView);
        progressBar = findViewById(R.id.progressBar);
        errorTextView = findViewById(R.id.errorTextView);
        emptyTextView = findViewById(R.id.emptyTextView);
        fabRefresh = findViewById(R.id.fabRefresh);

        // RecyclerView 설정
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new FallEventAdapter();
        adapter.setOnItemClickListener(new FallEventAdapter.OnItemClickListener() {
            @Override
            public void onItemClick(FallEvent event) {
                // 아이템 클릭 시 상세 정보 표시 (선택사항)
                Toast.makeText(MainActivity.this, "이벤트 ID: " + event.id, Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onImageClick(FallEvent event, String imageUrl) {
                // 이미지 클릭 시 확대 보기
                ImageZoomDialog dialog = new ImageZoomDialog(MainActivity.this, imageUrl);
                dialog.show();
            }
        });
        recyclerView.setAdapter(adapter);

        // 새로고침 버튼 클릭 리스너
        fabRefresh.setOnClickListener(v -> loadFallEvents());

        // Handler 초기화
        handler = new Handler(Looper.getMainLooper());
        
        // 초기 데이터 로드
        loadFallEvents();
        
        // 주기적으로 새 이벤트 체크 시작
        startCheckingNewEvents();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Handler 정리
        if (handler != null && checkNewEventsRunnable != null) {
            handler.removeCallbacks(checkNewEventsRunnable);
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // 화면이 백그라운드로 갈 때 체크 중지
        stopCheckingNewEvents();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // 화면이 다시 보일 때 체크 재개
        startCheckingNewEvents();
    }

    /**
     * 서버에서 낙상 이벤트 목록 가져오기
     */
    private void loadFallEvents() {
        // 로딩 상태 표시
        progressBar.setVisibility(View.VISIBLE);
        errorTextView.setVisibility(View.GONE);
        emptyTextView.setVisibility(View.GONE);

        // API 호출
        ApiService apiService = RetrofitClient.getApiService();
        Call<List<FallEvent>> call = apiService.getFallEvents();

        call.enqueue(new Callback<List<FallEvent>>() {
            @Override
            public void onResponse(Call<List<FallEvent>> call, Response<List<FallEvent>> response) {
                progressBar.setVisibility(View.GONE);

                if (response.isSuccessful() && response.body() != null) {
                    List<FallEvent> events = response.body();
                    if (events.isEmpty()) {
                        // 빈 상태 표시
                        emptyTextView.setVisibility(View.VISIBLE);
                        recyclerView.setVisibility(View.GONE);
                        lastEventId = -1;
                    } else {
                        // 데이터 표시
                        adapter.setFallEvents(events);
                        recyclerView.setVisibility(View.VISIBLE);
                        emptyTextView.setVisibility(View.GONE);
                        
                        // 가장 최신 이벤트 ID 저장
                        if (!events.isEmpty()) {
                            lastEventId = events.get(0).id;
                        }
                    }
                } else {
                    // 에러 처리
                    showError("서버 응답 오류: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<List<FallEvent>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                showError("네트워크 오류: " + t.getMessage());
                t.printStackTrace();
            }
        });
    }

    /**
     * 에러 메시지 표시
     */
    private void showError(String message) {
        errorTextView.setText(message);
        errorTextView.setVisibility(View.VISIBLE);
        recyclerView.setVisibility(View.GONE);
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_settings) {
            // 설정 화면으로 이동 (선택사항)
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
    
    /**
     * 주기적으로 새 이벤트 체크 시작
     */
    private void startCheckingNewEvents() {
        if (checkNewEventsRunnable == null) {
            checkNewEventsRunnable = new Runnable() {
                @Override
                public void run() {
                    checkForNewEvents();
                    // 다음 체크 예약
                    if (handler != null) {
                        handler.postDelayed(this, CHECK_INTERVAL);
                    }
                }
            };
        }
        handler.postDelayed(checkNewEventsRunnable, CHECK_INTERVAL);
    }
    
    /**
     * 새 이벤트 체크 중지
     */
    private void stopCheckingNewEvents() {
        if (handler != null && checkNewEventsRunnable != null) {
            handler.removeCallbacks(checkNewEventsRunnable);
        }
    }
    
    /**
     * 새로운 이벤트가 있는지 확인
     */
    private void checkForNewEvents() {
        ApiService apiService = RetrofitClient.getApiService();
        Call<List<FallEvent>> call = apiService.getFallEvents();

        call.enqueue(new Callback<List<FallEvent>>() {
            @Override
            public void onResponse(Call<List<FallEvent>> call, Response<List<FallEvent>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<FallEvent> events = response.body();
                    if (!events.isEmpty()) {
                        int latestId = events.get(0).id;
                        
                        // 새로운 이벤트가 있는지 확인
                        if (lastEventId != -1 && latestId > lastEventId) {
                            // 새 이벤트 발견
                            showNewEventWarning(events.get(0));
                            // 목록 새로고침
                            loadFallEvents();
                        } else if (lastEventId == -1 && !events.isEmpty()) {
                            // 첫 로드 시 마지막 ID 저장
                            lastEventId = latestId;
                        }
                    }
                }
            }

            @Override
            public void onFailure(Call<List<FallEvent>> call, Throwable t) {
                // 조용히 실패 (에러 표시 안 함, 정기 체크이므로)
            }
        });
    }
    
    /**
     * 새 이벤트 발견 시 Warning 알림 표시
     */
    private void showNewEventWarning(FallEvent newEvent) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("⚠️ 새로운 낙상 감지");
        builder.setMessage("새로운 낙상 이벤트가 감지되었습니다.\n\n" +
                "위치: " + (newEvent.location != null ? newEvent.location : "정보 없음") + "\n" +
                "발생 시간: " + formatDateTime(newEvent.occurred_at));
        builder.setIcon(android.R.drawable.ic_dialog_alert);
        builder.setPositiveButton("확인", (dialog, which) -> {
            dialog.dismiss();
            // 목록 맨 위로 스크롤
            if (recyclerView != null) {
                recyclerView.smoothScrollToPosition(0);
            }
        });
        builder.setCancelable(true);
        
        AlertDialog dialog = builder.create();
        dialog.show();
    }
    
    /**
     * 날짜 시간 포맷팅
     */
    private String formatDateTime(String isoDateTime) {
        if (isoDateTime == null || isoDateTime.isEmpty()) {
            return "정보 없음";
        }
        try {
            java.text.SimpleDateFormat inputFormat = new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", java.util.Locale.getDefault());
            java.text.SimpleDateFormat outputFormat = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.getDefault());
            java.util.Date date = inputFormat.parse(isoDateTime.substring(0, Math.min(19, isoDateTime.length())));
            return outputFormat.format(date);
        } catch (Exception e) {
            return isoDateTime;
        }
    }
}