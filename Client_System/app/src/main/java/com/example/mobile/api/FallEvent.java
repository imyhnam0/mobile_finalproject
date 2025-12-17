package com.example.mobile.api;

/**
 * 낙상 이벤트 모델 클래스
 */
public class FallEvent {
    public int id;
    public String image_url;
    public String location;
    public String description;
    public String occurred_at;
    public String created_at;
    public boolean is_checked;

    public FallEvent() {
    }

    public FallEvent(int id, String image_url, String location, String description, 
                     String occurred_at, String created_at, boolean is_checked) {
        this.id = id;
        this.image_url = image_url;
        this.location = location;
        this.description = description;
        this.occurred_at = occurred_at;
        this.created_at = created_at;
        this.is_checked = is_checked;
    }
}
