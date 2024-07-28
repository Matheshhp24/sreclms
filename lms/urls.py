from django.urls import path
from .views import *
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import views as auth_views
from django.contrib import admin
urlpatterns = [
    # path('admin/', admin.site.urls),

    path('add-staff/', admin_page, name='AddStaff'),
    path('delete-staff-view/', admin_page, name='DeleteStaffView'),
    path('delete-staff/<str:username>/', admin_page, name='DeleteStaff'),
    path('edit-staff-view/', admin_page, name='EditStaffView'),
    path('edit-staff/<str:username>/', admin_page, name='EditStaff'),
    path('avail-leave-view/', admin_page, name='AvailLeaveView'),
    path('avail-leave/<str:username>/', admin_page, name='AvailLeave'),
    path('download-view/', admin_page, name='DownloadView'),
    path('hod-download-view/', hod_page, name='HODDownloadView'),
    path('download/<str:username>/', admin_page, name='Download'),
    path('hod-download/<str:username>/', hod_page, name='HODDownload'),
    path('download-all', admin_page, name='DownloadAll'),
    path('hod-download-all', hod_page, name='HODDownloadAll'),
    path('download_leavedata', admin_page, name='DownloadLeaveAvailability'),
    path('hod-download_leavedata', hod_page, name='HODDownloadLeaveAvailability'),
    path('delete-and-reset', admin_page, name='DeleteAndReset'),
    path('', CustomLoginView.as_view(), name='Login'),
    path("logout/", auth_views.LogoutView.as_view(template_name='logout.html'), name='Logout'),
    # path("login/",auth_views.LoginView.as_view(template_name = 'login.html'),name='Login'),

    path('home/',home,name='Home'),
    path('history/',dashboard,name='Dashboard'),
    path('dashboard/',card_dashboard,name='CardDashboard'),
    path('profile/',profile,name='Profile'),
    path('casual-leave/',casual_leave_function,name='CasualLeave'),
    path('lop-leave/',lop_leave_function,name='LopLeave'),
    path('earn-leave/',earn_leave_function,name='EarnLeave'),
    path('vaccation-leave/',vaccation_leave_function,name='VaccationLeave'),
    path('on-duty/',onduty_function,name='OnDuty'),
    path('special-on-duty/',special_onduty_function,name='SpecialOnDuty'),
    path('compensation-holiday/',CH_leave_function,name='CHLeave'),
    path('medical-leave/',medical_leave_function,name='MedicalLeave'),
    path('hr-view/',hr_view_function,name='HRView'),
    path('admin-login/',admin_login,name='AdminLogin'),
    path('admin-page/',admin_page,name='AdminPage'),
    path('Hod-page/',hod_page,name='HODPage'),
    path('new-requests/',admin_page,name='NewRequests'),
    path('hod-new-requests/',hod_page,name='HODNewRequests'),
    path('requests-handling/', requests_handling, name='RequestsHandling'),
    path('announcement/<str:username>/<str:timestamp>/', add_announcement, name='AddAnnouncement'),
    path('delete/<str:username>/<str:timestamp>/', add_announcement, name='DeleteAnnouncement'),
    path('new_announcement/', announcement_view, name='Announcement'),
    path('download-individual/<str:leave_type>/', download_individual, name='DownloadIndividual'),
    path('account-settings/', account_settings, name='AccountSettings'),
    path('admin-account-hod/', hod_page, name='HODAdminAccount'),
    path('admin-account/', admin_page, name='AdminAccount'),
    path('get_otp/', get_otp, name='get_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('update_password/',update_password , name='UpdatePassword'),
    path('update_email/',update_email , name='UpdateEmail'),
    path('leave_availability/',admin_page , name='LeaveAvailability'),
    path('leave_availability_hod/',hod_page , name='HODLeaveAvailability'),
    path('adding_department/',add_department , name='AddDepartment'),
    path('leave_documents/<path>/', serve, {'document_root': settings.MEDIA_ROOT}),


    # Add other URL patterns as needed
]