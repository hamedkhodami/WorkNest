from django.urls import path

from . import views

app_name = 'apps.account'
urlpatterns = [
    path('token/basic', views.LoginBasic.as_view(), name='token_obtain_pair_basic'),
    path('token/otp', views.LoginOTP.as_view(), name='token_obtain_pair_otp'),
    path('token/refresh/', views.TokenRefresh.as_view(), name='token_refresh'),

    path('logout', views.Logout.as_view(), name='logout'),
    path('register', views.Register.as_view(), name='register'),
    path('reset-password', views.ResetPassword.as_view(), name='reset_password__send_code'),
    path('reset-password/check-code-and-set', views.ResetPasswordCheckAndSet.as_view(),
         name='reset_password__check_code_and_set'),

    path('user/create', views.UserCreate.as_view(), name='user_create'),
    path('user/send-otp-code', views.UserSendOTP.as_view(), name='user_send_otp_code'),
    path('user/update', views.UserUpdate.as_view(), name='user_update'),
    path('user/list', views.UserList.as_view(), name='user_list'),
    path('user/<uuid:user_id>/delete', views.UserDelete.as_view(), name='user_delete'),
    path('user/detail', views.UserDetail.as_view(), name='user_detail'),
    path('user/detail/basic', views.UserDetailBasic.as_view(), name='user_detail_basic'),
    path('user/<int:national_id>/detail/basic', views.UserDetailBasicByOtherUser.as_view(),
         name='user_detail_basic_by_other'),
    path('user/<uuid:user_id>/block', views.UserBlock.as_view(), name='user_block'),
    path('user/<uuid:user_id>/unblock', views.UserUnBlock.as_view(), name='user_unblock'),
    path('user/<uuid:user_id>/block/detail', views.UserBlockDetail.as_view(), name='user_block_detail'),

    path('user/profile/confirm-phonenumber', views.ConfirmPhoneNumber.as_view(),
         name='user_profile_confirm_phonenumber'),

]