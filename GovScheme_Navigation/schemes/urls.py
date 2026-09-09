from django.urls import path
from schemes import views

app_name = 'schemes'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('results/', views.results_view, name='results'),
    path('scheme/<str:scheme_code>/', views.scheme_detail_view, name='scheme_detail'),
    path('track/', views.track_status_view, name='track_status'),
    path('blueprint/', views.blueprint_view, name='blueprint'),

    # REST / AJAX API Endpoints
    path('api/track/', views.api_track_status, name='api_track_status'),
    path('api/simulate-transition/', views.api_simulate_transition, name='api_simulate_transition'),
    path('api/quick-apply/', views.api_quick_apply, name='api_quick_apply'),
    path('api/notifications/', views.api_get_notifications, name='api_notifications'),
    path('api/notifications/<uuid:notif_id>/read/', views.api_mark_notification_read, name='api_mark_read'),
]
