from rest_framework import serializers

from .models import FallEvent


class FallEventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # image 필드를 명시적으로 추가해야 업로드된 파일이 저장됩니다
    image = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = FallEvent
        fields = [
            "id",
            "image",  # 쓰기 전용 (write_only=True)
            "image_url",  # 읽기 전용 (SerializerMethodField)
            "location",
            "description",
            "occurred_at",
            "created_at",
            "is_checked",
        ]
        read_only_fields = ["id", "created_at", "is_checked"]

    def get_image_url(self, obj):
        """읽기 전용: 이미지 URL 반환"""
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback: return relative URL if no request context
                return obj.image.url
        return None
