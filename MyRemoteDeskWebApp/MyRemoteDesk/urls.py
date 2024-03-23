"""MyRemoteDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
import app.views as av
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

urlpatterns = [
    path('',av.index),
    path('LoginOrg', av.org_login),
    path('SignUpOrg',av.org_register),
    path('LoginUser', av.user_login),
    path('VerifyEmail',av.verifyEmail),
    path('logout',av.logout),
    path('contact',av.contact),
    path('faq', av.faq),
    path('org_index', av.org_index),
    path('org_change_password',av.org_change_password),
    path('org_report_problems',av.report_org),
    path('create-emp',av.add_emp),
    path('read-emp',av.read_emp),
    path('create-wp', av.create_wp),
    path('update-emp/<int:eid>', av.update_emp),
    path('del-emp/<int:eid>', av.del_emp),
    path('view-app-web', av.view_app_web),
    path('ss-monitoring', av.ss_monitoring),
    path('logout',av.logout),
    path('edit-wp', av.read_edit_wp),
    path('del-wp/<int:wid>', av.del_wp),
    path('org-forgot-password',av.org_forgot_password),
    path('org-forgot-password-otp-verify', av.org_forgot_password_otp_verify),
    path('org-forgot-password-change-pass', av.org_forgot_password_change_password),
    path('user-ss-monitoring', av.user_ss_monitoring),
    path('user-power-monitoring', av.user_power_monitoring),
    path('power-monitoring', av.power_monitoring),
    path('work-productivity-check', av.work_productivity_check),
    path('user-work-productivity-check', av.user_work_productivity_check),
    path('view-emp/<int:eid>', av.view_emp),
    path('logDashboard', av.logDashboard),
    path('get_prod_details/<str:eidanddate>', av.get_prod_details),
    path('org-view-attendance', av.org_view_attendance),
    path('get_emp_logged_in_count_today', av.get_emp_logged_in_count_today),
    path('admin/', admin.site.urls),
    path('get_select_result/', av.get_select_result),
    path('get_ip_data/', av.get_ip_data, name='get_ip_data'),
    path('push_start_attendance_logs_to_db/', av.push_start_attendance_logs_to_db, name='push_start_attendance_logs_to_db'),
    path('push_power_logs_to_db/', av.push_power_logs_to_db, name='push_power_logs_to_db'),
    path('push_start_attendance_logs_to_db/', av.push_start_attendance_logs_to_db, name='push_start_attendance_logs_to_db'),
    path('get_monitoring_app/', av.get_monitoring_app, name='get_monitoring_app'),
    path('push_screenshot_logs_to_db/', av.push_screenshot_logs_to_db, name='push_screenshot_logs_to_db'),
]

handler404 = "app.views.error_404_view"
