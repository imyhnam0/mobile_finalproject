package com.example.mobile.ui;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.mobile.R;
import com.example.mobile.api.FallEvent;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * 낙상 이벤트 RecyclerView 어댑터
 */
public class FallEventAdapter extends RecyclerView.Adapter<FallEventAdapter.ViewHolder> {
    private List<FallEvent> fallEvents = new ArrayList<>();
    private OnItemClickListener listener;

    public interface OnItemClickListener {
        void onItemClick(FallEvent event);
        void onImageClick(FallEvent event, String imageUrl);
    }

    public void setOnItemClickListener(OnItemClickListener listener) {
        this.listener = listener;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_fall_event, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        FallEvent event = fallEvents.get(position);
        holder.bind(event);
    }

    @Override
    public int getItemCount() {
        return fallEvents.size();
    }

    public void setFallEvents(List<FallEvent> events) {
        this.fallEvents = events != null ? events : new ArrayList<>();
        notifyDataSetChanged();
    }

    public void addFallEvents(List<FallEvent> events) {
        if (events != null && !events.isEmpty()) {
            int startPosition = fallEvents.size();
            fallEvents.addAll(events);
            notifyItemRangeInserted(startPosition, events.size());
        }
    }

    class ViewHolder extends RecyclerView.ViewHolder {
        private ImageView imageView;
        private TextView locationTextView;
        private TextView descriptionTextView;
        private TextView occurredAtTextView;
        private TextView statusTextView;

        ViewHolder(View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.imageView);
            locationTextView = itemView.findViewById(R.id.locationTextView);
            descriptionTextView = itemView.findViewById(R.id.descriptionTextView);
            occurredAtTextView = itemView.findViewById(R.id.occurredAtTextView);
            statusTextView = itemView.findViewById(R.id.statusTextView);

            itemView.setOnClickListener(v -> {
                int position = getAdapterPosition();
                if (position != RecyclerView.NO_POSITION && listener != null) {
                    listener.onItemClick(fallEvents.get(position));
                }
            });
        }

        void bind(FallEvent event) {
            // 이미지 로드 (Glide 사용)
            if (event.image_url != null && !event.image_url.isEmpty()) {
                Glide.with(itemView.getContext())
                        .load(event.image_url)
                        .placeholder(android.R.drawable.ic_menu_gallery) // 로딩 중 이미지
                        .error(android.R.drawable.ic_dialog_alert) // 에러 시 이미지
                        .centerCrop()
                        .into(imageView);
                
                // 이미지 클릭 시 확대 보기
                imageView.setOnClickListener(v -> {
                    if (listener != null) {
                        listener.onImageClick(event, event.image_url);
                    }
                });
            } else {
                imageView.setImageResource(android.R.drawable.ic_menu_gallery);
                imageView.setOnClickListener(null);
            }

            // 위치 정보
            locationTextView.setText(event.location != null ? event.location : "위치 정보 없음");

            // 설명
            descriptionTextView.setText(event.description != null ? event.description : "");

            // 발생 일시
            if (event.occurred_at != null) {
                occurredAtTextView.setText(formatDateTime(event.occurred_at));
            } else {
                occurredAtTextView.setText("일시 정보 없음");
            }

            // 확인 상태
            if (event.is_checked) {
                statusTextView.setText("✓ 확인됨");
                statusTextView.setTextColor(itemView.getContext().getResources().getColor(android.R.color.holo_green_dark));
            } else {
                statusTextView.setText("미확인");
                statusTextView.setTextColor(itemView.getContext().getResources().getColor(android.R.color.holo_red_dark));
            }
        }

        private String formatDateTime(String isoDateTime) {
            try {
                SimpleDateFormat inputFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                SimpleDateFormat outputFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault());
                Date date = inputFormat.parse(isoDateTime.substring(0, 19)); // ISO 형식 파싱
                return outputFormat.format(date);
            } catch (ParseException e) {
                return isoDateTime; // 파싱 실패 시 원본 반환
            }
        }
    }
}
