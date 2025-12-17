package com.example.mobile.ui;

import android.content.Context;
import android.graphics.Matrix;
import android.graphics.RectF;
import android.graphics.drawable.Drawable;
import android.util.AttributeSet;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.ViewParent;

import androidx.annotation.Nullable;
import androidx.appcompat.widget.AppCompatImageView;

/**
 * 핀치 줌/드래그/더블탭 줌을 지원하는 ImageView.
 * - 기본 상태: fitCenter(=화면에 맞춰 중앙 정렬)
 * - 핀치: 확대/축소 (최소 1x ~ 최대 MAX_SCALE)
 * - 드래그: 확대 상태에서만 이동
 * - 더블탭: 1x <-> DOUBLE_TAP_SCALE 토글
 */
public class ZoomableImageView extends AppCompatImageView {
    private static final float MAX_SCALE = 5.0f;
    private static final float DOUBLE_TAP_SCALE = 2.5f;

    private final Matrix baseMatrix = new Matrix();
    private final Matrix drawMatrix = new Matrix();
    private final RectF drawableRect = new RectF();
    private final RectF viewRect = new RectF();

    private float currentScale = 1.0f; // baseMatrix 대비 추가 스케일
    private float lastX;
    private float lastY;
    private boolean isDragging = false;

    private ScaleGestureDetector scaleDetector;
    private GestureDetector gestureDetector;

    public ZoomableImageView(Context context) {
        super(context);
        init(context);
    }

    public ZoomableImageView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public ZoomableImageView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    private void init(Context context) {
        setScaleType(ScaleType.MATRIX);

        scaleDetector = new ScaleGestureDetector(context, new ScaleGestureDetector.SimpleOnScaleGestureListener() {
            @Override
            public boolean onScale(ScaleGestureDetector detector) {
                float scaleFactor = detector.getScaleFactor();
                float targetScale = clamp(currentScale * scaleFactor, 1.0f, MAX_SCALE);
                float factor = targetScale / currentScale;

                if (factor != 1.0f) {
                    drawMatrix.postScale(factor, factor, detector.getFocusX(), detector.getFocusY());
                    currentScale = targetScale;
                    fixTranslation();
                    setImageMatrix(drawMatrix);
                    disallowParentIntercept(true);
                }
                return true;
            }
        });

        gestureDetector = new GestureDetector(context, new GestureDetector.SimpleOnGestureListener() {
            @Override
            public boolean onDoubleTap(MotionEvent e) {
                if (currentScale > 1.0f) {
                    resetZoom();
                } else {
                    zoomTo(DOUBLE_TAP_SCALE, e.getX(), e.getY());
                }
                return true;
            }

            @Override
            public boolean onSingleTapConfirmed(MotionEvent e) {
                // 다이얼로그 등에서 클릭 이벤트를 쓰는 경우를 위해 performClick 전달
                return performClick();
            }
        });

        setOnTouchListener((v, event) -> {
            if (getDrawable() == null) return false;

            gestureDetector.onTouchEvent(event);
            scaleDetector.onTouchEvent(event);

            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    lastX = event.getX();
                    lastY = event.getY();
                    isDragging = false;
                    break;
                case MotionEvent.ACTION_MOVE:
                    if (currentScale > 1.0f && !scaleDetector.isInProgress()) {
                        float dx = event.getX() - lastX;
                        float dy = event.getY() - lastY;

                        // 미세 이동은 무시 (클릭 오인 방지)
                        if (!isDragging && (Math.abs(dx) > 2f || Math.abs(dy) > 2f)) {
                            isDragging = true;
                        }

                        if (isDragging) {
                            drawMatrix.postTranslate(dx, dy);
                            fixTranslation();
                            setImageMatrix(drawMatrix);
                            disallowParentIntercept(true);
                        }

                        lastX = event.getX();
                        lastY = event.getY();
                    }
                    break;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    disallowParentIntercept(false);
                    break;
            }

            // 확대/드래그/핀치 상황에서는 이벤트를 소비해서 스크롤(RecyclerView 등)로 전달되지 않게 함
            return currentScale > 1.0f || scaleDetector.isInProgress() || isDragging;
        });
    }

    @Override
    public boolean performClick() {
        return super.performClick();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        fitImageToView();
    }

    @Override
    public void setImageDrawable(@Nullable Drawable drawable) {
        super.setImageDrawable(drawable);
        // Glide 로딩 완료 시점 등에서 다시 맞춤
        post(this::fitImageToView);
    }

    private void fitImageToView() {
        Drawable d = getDrawable();
        if (d == null) return;
        int vw = getWidth();
        int vh = getHeight();
        if (vw <= 0 || vh <= 0) return;

        float dw = d.getIntrinsicWidth();
        float dh = d.getIntrinsicHeight();
        if (dw <= 0 || dh <= 0) return;

        float scale = Math.min((float) vw / dw, (float) vh / dh);
        float dx = (vw - dw * scale) / 2f;
        float dy = (vh - dh * scale) / 2f;

        baseMatrix.reset();
        baseMatrix.postScale(scale, scale);
        baseMatrix.postTranslate(dx, dy);

        drawMatrix.set(baseMatrix);
        currentScale = 1.0f;
        setImageMatrix(drawMatrix);
    }

    private void resetZoom() {
        drawMatrix.set(baseMatrix);
        currentScale = 1.0f;
        setImageMatrix(drawMatrix);
        disallowParentIntercept(false);
    }

    private void zoomTo(float targetScale, float focusX, float focusY) {
        targetScale = clamp(targetScale, 1.0f, MAX_SCALE);
        float factor = targetScale / currentScale;
        drawMatrix.postScale(factor, factor, focusX, focusY);
        currentScale = targetScale;
        fixTranslation();
        setImageMatrix(drawMatrix);
        disallowParentIntercept(true);
    }

    private void fixTranslation() {
        Drawable d = getDrawable();
        if (d == null) return;

        int vw = getWidth();
        int vh = getHeight();
        if (vw <= 0 || vh <= 0) return;

        viewRect.set(0, 0, vw, vh);
        drawableRect.set(0, 0, d.getIntrinsicWidth(), d.getIntrinsicHeight());
        drawMatrix.mapRect(drawableRect);

        float deltaX = 0f;
        float deltaY = 0f;

        if (drawableRect.width() <= viewRect.width()) {
            deltaX = (viewRect.width() - drawableRect.width()) / 2f - drawableRect.left;
        } else {
            if (drawableRect.left > 0) deltaX = -drawableRect.left;
            else if (drawableRect.right < viewRect.width()) deltaX = viewRect.width() - drawableRect.right;
        }

        if (drawableRect.height() <= viewRect.height()) {
            deltaY = (viewRect.height() - drawableRect.height()) / 2f - drawableRect.top;
        } else {
            if (drawableRect.top > 0) deltaY = -drawableRect.top;
            else if (drawableRect.bottom < viewRect.height()) deltaY = viewRect.height() - drawableRect.bottom;
        }

        if (deltaX != 0f || deltaY != 0f) {
            drawMatrix.postTranslate(deltaX, deltaY);
        }
    }

    private static float clamp(float v, float min, float max) {
        return Math.max(min, Math.min(max, v));
    }

    private void disallowParentIntercept(boolean disallow) {
        ViewParent p = getParent();
        if (p != null) {
            p.requestDisallowInterceptTouchEvent(disallow);
        }
    }
}


