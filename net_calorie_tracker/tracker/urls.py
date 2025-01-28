from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.home, name='home'),
    # user dashboard  views logic path
    path('users_dashboard/', views.user_dashboard, name='users_dashboard'),
    path('user_daily_logs_dashboard/', views.user_daily_logs_dashboard, name='user_daily_logs_dashboard'),
    path('user_daily_summery/',views.get_daily_summaries,name='user_daily_summery'),
    path('search_food/', views.search_food, name='search_food'),
    path('save_food_log/', views.save_food_log, name='save_food_log'),
    path('search_activity/', views.search_activity, name='search_activity'),
    path('save_activity_log/', views.save_activity_log, name='save_activity_log'),
    path('get-logs/', views.get_logs, name='get_logs'),
    path('api/delete_food_log/<int:log_id>/', views.delete_food_log, name='delete_food_log'),  # DELETE request
    path('api/delete_activity_log/<int:log_id>/', views.delete_activity_log, name='delete_activity_log'),
    
    # admin dashboard view logic path
    path('admin_panel_dashboard/', views.admin_dashboard, name='admin_panel_dashboard'),
    path('daily_summary/<int:user_id>/', views.daily_summery_for_admin, name='daily_summery_for_admin'),
    path('user/<int:user_id>/daily-logs/<str:selected_date>/', views.daily_logs, name='daily_logs')

    
]
