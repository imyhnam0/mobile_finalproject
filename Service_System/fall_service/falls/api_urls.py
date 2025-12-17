from django.urls import path

from .api_views import FallEventCreateView, FallEventDetailView, FallEventListView

urlpatterns = [
    path("fall-events/", FallEventCreateView.as_view(), name="fall-event-create"),
    path("fall-events/list/", FallEventListView.as_view(), name="fall-event-list"),
    path("fall-events/<int:pk>/", FallEventDetailView.as_view(), name="fall-event-detail"),
]
