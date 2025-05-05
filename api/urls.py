from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, LoginView, LogoutView, ContractUploadView, ContractListView, ContractDetailView
from .template_views import register, user_login, user_logout, contract_list, contract_upload, contract_detail, contract_edit, contract_delete, contract_download

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    
    # Password reset views
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    path('contracts/', contract_list, name='contracts'),
    path('contracts/upload/', contract_upload, name='contract-upload'),
    path('contracts/<int:pk>/', contract_detail, name='contract-detail'),
    path('contracts/<int:pk>/edit/', contract_edit, name='contract-edit'),
    path('contracts/<int:pk>/delete/', contract_delete, name='contract-delete'),
    path('contracts/<int:pk>/download/', contract_download, name='contract-download'),
]
