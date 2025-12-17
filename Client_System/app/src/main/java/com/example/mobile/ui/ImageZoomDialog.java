package com.example.mobile.ui;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Bundle;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.ImageButton;

import androidx.annotation.NonNull;

import com.bumptech.glide.Glide;
import com.example.mobile.R;

/**
 * 이미지 확대 보기 다이얼로그
 */
public class ImageZoomDialog extends Dialog {
    private String imageUrl;
    private ZoomableImageView zoomImageView;
    private ImageButton closeButton;

    public ImageZoomDialog(@NonNull Context context, String imageUrl) {
        super(context);
        this.imageUrl = imageUrl;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.dialog_image_zoom);

        zoomImageView = findViewById(R.id.zoomImageView);
        closeButton = findViewById(R.id.closeButton);

        // 전체 화면처럼 보이도록 처리
        if (getWindow() != null) {
            getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
            getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        }

        // 이미지 로드
        if (imageUrl != null && !imageUrl.isEmpty()) {
            Glide.with(getContext())
                    .load(imageUrl)
                    .into(zoomImageView);
        }

        // 닫기 버튼
        closeButton.setOnClickListener(v -> dismiss());

        // 배경 클릭 닫기는 제스처(핀치/드래그)와 충돌할 수 있어 제외 (닫기 버튼/뒤로가기 사용)
    }
}
