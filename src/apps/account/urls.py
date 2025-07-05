from django.urls import path

from . import views

app_name = 'apps.account'


urlpatterns = [
    path('token/refresh/', views.TokenRefresh.as_view(), name='token_refresh'),
    path('token/basic', views.LoginBasic.as_view(), name='token_obtain_pair_basic'),
    path('token/otp', views.LoginOTP.as_view(), name='token_obtain_pair_otp'),

    path('logout', views.Logout.as_view(), name='logout'),

    path('register', views.Register.as_view(), name='register'),
    path('reset-password', views.ResetPassword.as_view(), name='reset_password__send_code'),
    path('reset-password/check-code-and-set', views.ResetPasswordCheckAndSet.as_view(),
         name='reset_password__check_code_and_set'),

    path('user/create', views.UserCreate.as_view(), name='user_create'),
    path('user/send-otp-code', views.UserSendOTP.as_view(), name='user_send_otp_code'),
    path('user/<uuid:user_id>/delete', views.UserDelete.as_view(), name='user_delete'),
    path('user/<uuid:user_id>/block', views.UserBlock.as_view(), name='user_block'),
    path('user/<uuid:user_id>/unblock', views.UserUnBlock.as_view(), name='user_unblock'),
    path('user/<uuid:user_id>/block/detail', views.UserBlockDetail.as_view(), name='user_block_detail'),

    path('user/profile/confirm-phone_number', views.ConfirmPhoneNumber.as_view(),
         name='user_profile_confirm_phone_number'),

    path('list/', views.ProfileListView.as_view(), name='profile-list'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile-update'),

]