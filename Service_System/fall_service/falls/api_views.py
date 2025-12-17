from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from datetime import timedelta

from .models import Device, FallEvent
from .serializers import FallEventSerializer
from .utils import send_fcm_notification


class FallEventCreateView(generics.CreateAPIView):
    """
    Edge system uploads images + metadata.
    POST /api/fall-events/
    """

    queryset = FallEvent.objects.all()
    serializer_class = FallEventSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        """Add request to serializer context for image_url generation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """Override create to ensure proper context in response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        occurred_at_str = request.data.get("occurred_at")
        occurred_at = parse_datetime(occurred_at_str) if occurred_at_str else None
        event = serializer.save(occurred_at=occurred_at)

        # Notify all devices (simple version)
        for device in Device.objects.all():
            send_fcm_notification(
                device.token,
                "Fall detected",
                f"{event.location}에서 낙상이 감지되었습니다.",
            )
        
        # Create response with proper context
        response_serializer = FallEventSerializer(event, context={'request': request})
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FallEventListView(generics.ListAPIView):
    """
    Android fetches latest fall events.
    GET /api/fall-events/list/
    
    Query parameters:
    - start_date: ISO 8601 format (e.g., 2025-12-01T00:00:00Z) - 필터링 시작 날짜
    - end_date: ISO 8601 format (e.g., 2025-12-31T23:59:59Z) - 필터링 종료 날짜
    
    Examples:
    - GET /api/fall-events/list/ - 모든 이벤트 조회
    - GET /api/fall-events/list/?start_date=2025-12-01T00:00:00Z - 2025-12-01 이후 이벤트
    - GET /api/fall-events/list/?end_date=2025-12-31T23:59:59Z - 2025-12-31 이전 이벤트
    - GET /api/fall-events/list/?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z - 기간 지정
    """

    serializer_class = FallEventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """기간별 필터링이 적용된 queryset 반환"""
        queryset = FallEvent.objects.all()
        
        # start_date 파라미터로 필터링 (이 날짜 이후)
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            try:
                start_date_parsed = parse_datetime(start_date)
                if start_date_parsed:
                    queryset = queryset.filter(occurred_at__gte=start_date_parsed)
            except (ValueError, TypeError):
                pass  # 잘못된 형식은 무시
        
        # end_date 파라미터로 필터링 (이 날짜 이전)
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            try:
                end_date_parsed = parse_datetime(end_date)
                if end_date_parsed:
                    queryset = queryset.filter(occurred_at__lte=end_date_parsed)
            except (ValueError, TypeError):
                pass  # 잘못된 형식은 무시
        
        # 발생 시간 기준 내림차순 정렬 (최신순)
        return queryset.order_by("-occurred_at")

    def get_serializer_context(self):
        """Add request to serializer context for image_url generation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FallEventDetailView(generics.RetrieveAPIView):
    """
    Single event detail.
    GET /api/fall-events/<id>/
    """

    queryset = FallEvent.objects.all()
    serializer_class = FallEventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        """Add request to serializer context for image_url generation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
