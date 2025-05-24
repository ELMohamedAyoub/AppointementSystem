from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from medicalpro.accounts import views

urlpatterns = [
    # Authentication endpoints
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('email/verify/', views.EmailVerificationView.as_view(), name='email_verify'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UpdateUserProfileView.as_view(), name='update_profile'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/mark-read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    
    # Admin routes
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
] 