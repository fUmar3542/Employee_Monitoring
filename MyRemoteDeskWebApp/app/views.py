from django.shortcuts import render
from matplotlib.style import use

from .models import AttendanceLogs, Board, Employee, Meeting, Monitoring, MonitoringDetails, Organization, OrganizationNews, PowerMonitoring, Project, Project_Employee_Linker, ScreenShotsMonitoring, Task, WorkProductivityDataset, Leaves
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
# from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

import math
import random
from password_generator import PasswordGenerator
import uuid
import datetime
import json
import time
import base64
import os
import requests


from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd

pwo = PasswordGenerator()
# Create your views here.

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(5):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def error_404_view(request, exception):
    return render(request,'404.html')


def error_500_view(request, exception):
    return render(request,'500.html')


def org_login_required(function):
    def wrapper(request, *args, **kw):
        if 'logged_in' in request.session:
            if request.session['u_type'] == 'org':
                return function(request, *args, **kw)
            else:
                messages.error(request, "You don't have privilege to access this page!")
                return HttpResponseRedirect('/')
        else:
            messages.error(request, "Logout Request/ Unauthorized Request, Please login!")
            return HttpResponseRedirect('/LoginOrg')
    return wrapper

def user_login_required(function):
    def wrapper(request, *args, **kw):
        if 'logged_in' in request.session:
            if request.session['u_type'] == 'emp':
                return function(request, *args, **kw)
            else:
                messages.error(request, "You don't have privilege to access this page!")
                return HttpResponseRedirect('/')
        else:
            messages.error(request, "Logout Request / Unauthorized Request, Please login!")
            return HttpResponseRedirect('/LoginUser')
    return wrapper

def index(request):
    return render(request, 'index.html')

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    if request.method == 'POST':
        cname = request.POST['cname']
        cemail = request.POST['cemail']
        cquery = request.POST['cquery']
        subject = 'MyRemoteDesk - New Enquiry'
        message = f'Name : {cname}, Email : {cemail}, Query : {cquery}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["narender.rk10@gmail.com",
                          "2021.narender.keswani@ves.ac.in",
                          "2021.prathamesh.bhosale@ves.ac.in",
                          "2021.chinmay.vyapari@ves.ac.in"]
        # send_mail(subject, message, email_from, recipient_list)
        # send_mail(subject, "YOUR QUERY WILL BE PROCESSED! WITHIN 24 HOURS", email_from, [cemail])
        messages.success(request, "Your Query has been recorded.")
        msg = "Your Query has been recorded."
        return render(request, 'contact.html', {"msg" : msg})
    return render(request, 'contact.html')

def org_login(request):
    if request.method == "POST":
        o_email = request.POST['o_email']
        o_pass = request.POST['o_pass']
        org_details = Organization.objects.filter(o_email=o_email, o_password=o_pass).values()
        if org_details:
            request.session['logged_in'] = True
            request.session['o_email'] = org_details[0]["o_email"]
            request.session['o_id'] = org_details[0]["id"]
            request.session['o_name'] = org_details[0]["o_name"]
            request.session['u_type'] = "org"
            return HttpResponseRedirect('/org_index')
        else:
            return render(request, 'OrgLogin.html', {'details': "0"})
    else:
        return render(request, 'OrgLogin.html')

def user_login(request):
    if request.method == "POST":
        e_email = request.POST['e_email']
        e_pass = request.POST['e_pass']
        user_details = Employee.objects.filter(e_email=e_email, e_password=e_pass).values()
        if user_details:
            request.session['logged_in'] = True
            request.session['u_email'] = user_details[0]["e_email"]
            request.session['u_id'] = user_details[0]["id"]
            request.session['u_name'] = user_details[0]["e_name"]
            request.session['u_oid'] = user_details[0]["o_id_id"]
            request.session['u_type'] = "emp"
            return HttpResponseRedirect('/user_index')
        else:
            return render(request, 'EmpLogin.html', {'msg': "0"})
    else:
        return render(request, 'EmpLogin.html')

def org_register(request):
    try:
        if request.method == "POST":
            o_name = request.POST['org_name']
            o_email = request.POST['o_email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            contact_no = request.POST['contact_no']
            website = request.POST['website']
            o_address = request.POST['o_address']
            if password1 == password2:
                otp = generateOTP()
                request.session['tempOTP'] = otp
                subject = 'MyRemoteDesk - OTP Verification'
                message = f'Hi {o_name}, thank you for registering in MyRemoteDesk . Your One Time Password (OTP) for verfication is {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [o_email, ]
                # send_mail(subject, message, email_from, recipient_list)
                request.session['tempOrg_name'] = o_name
                request.session['tempOrg_email'] = o_email
                request.session['tempPassword'] = password2
                request.session['tempContact_no'] = contact_no
                request.session['tempWebsite'] = website
                request.session['tempO_address'] = o_address
                return HttpResponseRedirect('/VerifyEmail')
            else:
                messages.error("Password not matched!")
        else:
            return render(request, 'OrgRegister.html')
    except Exception as ex:
        print(ex)

def verifyEmail(request):
    if request.method == 'POST':
        # theOTP = request.POST['eotp']
        # mOTP = request.session['tempOTP']
        theOTP = mOTP = 1
        if theOTP == mOTP:
            myDB_o_name = request.session['tempOrg_name']
            myDB_o_email = request.session['tempOrg_email'] 
            myDB_password = request.session['tempPassword']
            myDB_contact_no = request.session['tempContact_no']
            myDB_website = request.session['tempWebsite']
            myDB_o_address = request.session['tempO_address']
            try:
                obj = Organization.objects.create(o_name=myDB_o_name, o_email=myDB_o_email, o_password=myDB_password, o_contact=myDB_contact_no, o_website=myDB_website, o_address=myDB_o_address)
                obj.save()
                for key in list(request.session.keys()):
                    del request.session[key]
                messages.success(request,"You are successfully registered")
                return HttpResponseRedirect('/LoginOrg')
            except:
                for key in list(request.session.keys()):
                    del request.session[key]
                messages.error(request,"Error was occurred!")
                return render(request, 'OrgLogin.html', {'details': "Error Occurred"})
        else:
            messages.error(request, 'OTP is not matched!')
    else:
        return render(request,'verifyOTP.html')

@org_login_required
def org_index(request):
    return render(request,'OrgIndex.html')


@org_login_required
def org_change_password(request):
    if request.method == 'POST':
        oldPwd = request.POST['oldPwd']
        newPwd = request.POST['newPwd']
        o_id = request.session['o_id']
        o_email = request.session['o_email']
        org_details = Organization.objects.filter(o_email=o_email, o_password=oldPwd, pk=o_id).update(o_password=newPwd)
        if org_details:
            subject = 'MyRemoteDesk - Password Changed'
            message = f'Hi, your password was changed successfully! From MyRemoteDesk'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [o_email, ]
            # send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Password Change Successfully")
            return HttpResponseRedirect('/org_change_password')
        else:
            subject = 'MyRemoteDesk - Notifications'
            message = f'Hi, there was attempt to change your password! From MyRemoteDesk'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [o_email, ]
            # send_mail(subject, message, email_from, recipient_list)
            messages.error(request, "Old Password was not matched!")
            return HttpResponseRedirect('/org_change_password')
    else:
        return render(request, 'OrgChangePass.html')


def org_forgot_password(request):
    if request.method == 'POST':
        o_email = request.POST['o_email']
        request.session['tempfpOrgEmail'] = o_email
        org_details = Organization.objects.filter(o_email=o_email).values()
        if org_details:
            otp = generateOTP()
            request.session['tempfpOrgOTP'] = otp
            subject = 'MyRemoteDesk - OTP Verification for Forgot Password'
            message = f'Hi {o_email}, Your One Time Password (OTP) for forgot password is is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [o_email, ]
            # send_mail(subject, message, email_from, recipient_list)
            return HttpResponseRedirect('/org-forgot-password-otp-verify')
        else:
            return render(request, 'Org_fp.html', {'msg': "0"})
    else:
        return render(request, 'Org_fp.html')

def org_forgot_password_otp_verify(request):
    if request.method == 'POST':
        fp_org_otp = request.POST['fp_org_otp']
        tempOrgFpOTP = request.session['tempfpOrgOTP']
        if(fp_org_otp == tempOrgFpOTP):
            return HttpResponseRedirect('/org-forgot-password-change-pass')
        else:
            return render(request, 'OrgFpVerifyOTP.html', {'msg': "0"})
    else:
        return render(request, 'OrgFpVerifyOTP.html')

def org_forgot_password_change_password(request):
    if request.method == 'POST':
        tempOrgFpEmail = request.session['tempfpOrgEmail']
        pwd1 = request.POST['pwd1']
        pwd2 = request.POST['pwd2']
        if(pwd1 == pwd2):
            org_details = Organization.objects.filter(o_email=tempOrgFpEmail).update(o_password=pwd1)
            if org_details:
                subject = 'MyRemoteDesk - Password was Changed'
                message = f'Hi, Your Password was changed!'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [tempOrgFpEmail]
                # send_mail(subject, message, email_from, recipient_list)
                return render(request, 'OrgFpChangePass.html', {'msg': '10'})
            else:
                return render(request, 'OrgFpChangePass.html', {'msg': '11'})
        else:
            return render(request, 'OrgFpChangePass.html', {'msg': "2"})
    else:
        return render(request, 'OrgFpChangePass.html')


@org_login_required
def report_org(request):
    if request.method == 'POST':
        cname = request.session['o_name']
        cemail = request.session['o_email']
        ptype = request.POST['prob_type']
        cquery = request.POST['rquery']
        subject = 'MyRemoteDesk - New Enquiry'
        message = f'Name : {cname}, Email : {cemail}, Problem : {ptype}, Query : {cquery}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["narender.rk10@gmail.com",
                          "2021.narender.keswani@ves.ac.in",
                          "2021.prathamesh.bhosale@ves.ac.in",
                          "2021.chinmay.vyapari@ves.ac.in"]
        # send_mail(subject, message, email_from, recipient_list)
        # send_mail(subject, "Your Problem has been recorded. From: MyRemoteDesk", email_from, [cemail])
        msg = "Your Problem has been recorded."
        messages.success(request, "Your Problem has been recorded.")
        return HttpResponseRedirect('/org_report_problems')    
    return render(request, 'OrgReportProblems.html')

@user_login_required
def report_emp(request):
    if request.method == 'POST':
        cname = request.session['o_name']
        cemail = request.session['o_email']
        ptype = request.POST['prob_type']
        cquery = request.POST['rquery']
        subject = 'MyRemoteDesk - New Enquiry'
        message = f'Name : {cname}, Email : {cemail}, Problem : {ptype}, Query : {cquery}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["narender.rk10@gmail.com",
                          "2021.narender.keswani@ves.ac.in",
                          "2021.prathamesh.bhosale@ves.ac.in",
                          "2021.chinmay.vyapari@ves.ac.in"]
        # send_mail(subject, message, email_from, recipient_list)
        # send_mail(subject, "Your Problem has been recorded. From: MyRemoteDesk", email_from, [cemail])
        msg = "Your Problem has been recorded."
        return render(request, 'EmpReportProblems.html', {"msg": msg})
    return render(request, 'EmpReportProblems.html')

@org_login_required
def add_emp(request):
    if request.method == 'POST':
        o_id = request.session['o_id']
        e_name = request.POST['e_name']
        e_email = request.POST['e_email']
        e_password = pwo.generate()
        e_gender = request.POST['e_gender']
        e_contact = request.POST['e_contact']
        e_address = request.POST['e_address']
        empObj = Employee.objects.create(e_name=e_name, e_email=e_email, e_password=e_password,e_contact=e_contact, e_gender=e_gender, e_address=e_address, o_id_id=o_id)
        if empObj:
            subject = 'MyRemoteDesk - Login Info'
            org_name = request.session['o_name']
            message = f'Name : {e_name}, \n Email : {e_email}, \n Password : {e_password} \n Organization : {org_name}, \n FROM - MyRemoteDesk \n Developed by Narender Keswani, Prathamesh Bhosale, Chinmay Vpapari'
            email_from = settings.EMAIL_HOST_USER
            # send_mail(subject, message, email_from, [e_email])
            messages.success(request, "Employee was added successfully!")
            return HttpResponseRedirect('/create-emp')
        else:
            messages.error(request, "Some error was occurred!")
            return HttpResponseRedirect('/create-emp')
    return render(request, 'AddEmp.html')


@org_login_required
def view_emp(request,eid):
    if request.method == 'GET':
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id, id=eid).first()
        count_no_of_total_tasks = Task.objects.filter(o_id_id=o_id, e_id_id=eid).count()
        count_no_of_completed_tasks = Task.objects.filter(o_id_id=o_id, e_id_id=eid, t_status="completed").count()
        count_no_of_pending_tasks = count_no_of_total_tasks - count_no_of_completed_tasks
        pel_details = Project_Employee_Linker.objects.filter(o_id_id=o_id, e_id_id=eid).values_list('p_id_id', flat=True)
        project_details = Project.objects.filter(id__in=pel_details).values()
        return render(request, 'EmpDetails.html', {"msg": emp_details, "msg1": count_no_of_total_tasks, "msg2": count_no_of_completed_tasks, "msg3": count_no_of_pending_tasks, "msg4": project_details})

@org_login_required
def update_emp(request, eid):
    try:
        emp_detail = Employee.objects.filter(id=eid,o_id_id=request.session['o_id'])
        if request.method == "POST":
            e_name = request.POST['e_name']
            e_email = request.POST['e_email']
            e_gender = request.POST['e_gender']
            e_contact = request.POST['e_contact']
            e_address = request.POST['e_address']
            emp_detail = Employee.objects.get(id=eid)
            emp_detail.e_name = e_name
            emp_detail.e_email = e_email
            emp_detail.e_gender = e_gender
            emp_detail.e_contact = e_contact
            emp_detail.e_address = e_address
            emp_detail.save()
            if emp_detail:
                messages.success(request, "Employee Data was updated successfully!")
                return HttpResponseRedirect('/read-emp')
            else:
                messages.error(request, "Some Error was occurred!")
                return HttpResponseRedirect('/read-emp')
        return render(request, 'UpdateEmp.html', {'emp_detail':emp_detail[0]})
    except:
        messages.error(request, "Some Error was occurred!")
        return HttpResponseRedirect('/read-emp')

@org_login_required
def del_emp(request, eid):
    try:
        emp_detail = Employee.objects.filter(id=eid,o_id_id=request.session['o_id']).delete()
        if emp_detail:
            messages.success(request, "Employee was deleted successfully!")
            return HttpResponseRedirect('/read-emp')
        else:
            messages.error(request, "Some Error was occurred!")
            return HttpResponseRedirect('/read-emp')
    except:
        messages.error(request, "Some Error was occurred!")
        return HttpResponseRedirect('/read-emp')

@org_login_required
def view_app_web(request):
    if request.method == 'POST':
        o_id = request.session['o_id']
        e_id = request.POST['e_id']
        m_date = request.POST['date_log']
        m_date_f1 = datetime.datetime.strptime(m_date, '%Y-%m-%d')
        m_date_f2 = datetime.datetime.strftime(m_date_f1, '%Y-%m-%d')
        moni_details = Monitoring.objects.filter(o_id_id=o_id, e_id_id=e_id, m_log_ts__startswith=m_date_f2).exclude(m_title="").values()
        return render(request, 'ViewMoniLogs.html', {"msg": moni_details})
    else:
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        return render(request, 'SelectMoniEmp.html', {"msg": emp_details})



@org_login_required
def ss_monitoring(request):
    if request.method == 'POST':
        o_id = request.session['o_id']
        e_id = request.POST['e_id']
        ss_date = request.POST['date_log']
        ss_date_f1 = datetime.datetime.strptime(ss_date, '%Y-%m-%d')
        ss_date_f2 = datetime.datetime.strftime(ss_date_f1, '%Y-%m-%d')
        ss_moni_details = ScreenShotsMonitoring.objects.filter(o_id_id=o_id, e_id_id=e_id, ssm_log_ts__startswith=ss_date_f2).values()
        return render(request, 'ViewSSMoniLogs.html', {"msg": ss_moni_details})
    else:
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        return render(request, 'SelectSSMoniEmp.html', {"msg": emp_details})

@user_login_required
def user_ss_monitoring(request):
    if request.method == 'POST':
        o_id = request.session['u_oid']
        e_id = request.session['u_id']
        ss_date = request.POST['date_log']
        ss_date_f1 = datetime.datetime.strptime(ss_date, '%Y-%m-%d')
        ss_date_f2 = datetime.datetime.strftime(ss_date_f1, '%Y-%#m-%#d')
        ss_moni_details = ScreenShotsMonitoring.objects.filter(o_id_id=o_id, e_id_id=e_id, ssm_log_ts__startswith=ss_date_f2).values()
        return render(request, 'EmpViewSSMoniLogs.html', {"msg": ss_moni_details})
    else:
        return render(request, 'EmpSelectSSMoniEmp.html')

@org_login_required
def power_monitoring(request):
    if request.method == 'POST':
        o_id = request.session['o_id']
        e_id = request.POST['e_id']
        pm_date = request.POST['date_log']
        pm_date_f1 = datetime.datetime.strptime(pm_date, '%Y-%m-%d')
        pm_date_f2 = datetime.datetime.strftime(pm_date_f1, '%Y-%#m-%#d')
        ss_power_details = PowerMonitoring.objects.filter(o_id_id=o_id, e_id_id=e_id, pm_log_ts__startswith=pm_date_f2).values()
        return render(request, 'ViewPowerMoniLogs.html', {"msg": ss_power_details})
    else:
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        return render(request, 'SelectPowerMoniEmp.html', {"msg": emp_details})


@org_login_required
def read_emp(request):
    if request.method == 'GET':
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        return render(request, 'ViewEmp.html', {"msg": emp_details})


@user_login_required
def user_power_monitoring(request):
    if request.method == 'POST':
        o_id = request.session['u_oid']
        e_id = request.session['u_id']
        pm_date = request.POST['date_log']
        pm_date_f1 = datetime.datetime.strptime(pm_date, '%Y-%m-%d')
        pm_date_f2 = datetime.datetime.strftime(pm_date_f1, '%Y-%#m-%#d')
        ss_power_details = PowerMonitoring.objects.filter(o_id_id=o_id, e_id_id=e_id, pm_log_ts__startswith=pm_date_f2).values()
        return render(request, 'EmpViewPowerMoniLogs.html', {"msg": ss_power_details})
    else:
        return render(request, 'EmpSelectPowerMoniEmp.html')

@org_login_required
def create_wp(request):
    o_id = request.session['o_id']
    if request.method == 'POST':
        wp_ds = request.POST['wp_ds']
        wp_type = request.POST['wp_type']
        wpObj = WorkProductivityDataset.objects.create(w_pds=wp_ds, w_type=wp_type, o_id_id=o_id)
        if wpObj:
            messages.success(request, "Work Productivity Dataset Entry was added successfully!")
            return HttpResponseRedirect('/create-wp')
        else:
            messages.error(request, "Some error was occurred!")
            return HttpResponseRedirect('/create-wp')
    return render(request, 'AddWorkProductivity.html')

@org_login_required
def read_edit_wp(request):
    o_id = request.session['o_id']
    wpds_details = WorkProductivityDataset.objects.filter(o_id_id=o_id).values()
    return render(request, 'EditWorkProductivity.html', {"msg": wpds_details})


@org_login_required
def del_wp(request, wid):
    try:
        wpds_details = WorkProductivityDataset.objects.filter(id=wid,o_id_id=request.session['o_id']).delete()
        if wpds_details:
            messages.success(request, "Work Productivity Dataset Entry was deleted successfully!")
            return HttpResponseRedirect('/edit-wp')
        else:
            messages.error(request, "Some error was occurred!")
            return HttpResponseRedirect('/edit-wp')
    except:
        messages.error(request, "Some Error was occurred!")
        return HttpResponseRedirect('/edit-wp')


@org_login_required
def work_productivity_check(request):
    if request.method == 'POST':
        o_id = request.session['o_id']
        e_id = request.POST['e_id']
        m_date = request.POST['date_log']
        sum_of_emp_prod = get_work_productivity_details(o_id, e_id, m_date)
        prd_total = 0 
        unprd_total = 0
        undef_total = 0   
        for i in sum_of_emp_prod:
            if i[1]==1:
                prd_total = prd_total+int(i[2])
            if i[1]==2:
                unprd_total = unprd_total+int(i[2])
            if i[1]==3:
                undef_total = undef_total+int(i[2])
        total_time_spent = prd_total + unprd_total +undef_total
        return render(request, 'ViewWorkProductivity.html', {"msg": sum_of_emp_prod, "msg1": prd_total, "msg2": e_id, "msg3": m_date, "msg4": unprd_total, "msg5": undef_total, "msg6": total_time_spent})
    else:
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        return render(request, 'SelectWpEmp.html', {"msg": emp_details})

@user_login_required
def user_work_productivity_check(request):
    if request.method == 'POST':
        o_id = request.session['u_oid']
        e_id = request.session['u_id']
        m_date = request.POST['date_log']
        sum_of_emp_prod = get_work_productivity_details(o_id, e_id, m_date)
        prd_total = 0 
        unprd_total = 0
        undef_total = 0   
        for i in sum_of_emp_prod:
            if i[1]==1:
                prd_total = prd_total+int(i[2])
            if i[1]==2:
                unprd_total = unprd_total+int(i[2])
            if i[1]==3:
                undef_total = undef_total+int(i[2])
        total_time_spent = prd_total + unprd_total +undef_total
        return render(request, 'EmpViewWorkProductivity.html', {"msg": sum_of_emp_prod, "msg1": prd_total, "msg2": e_id, "msg3": m_date, "msg4": unprd_total, "msg5": undef_total, "msg6": total_time_spent})
    else:
        return render(request, 'EmpSelectWp.html')

@org_login_required
def logDashboard(request):
    o_id = request.session['o_id']
    employees = Employee.objects.filter(o_id_id=o_id).values()
    depth_moni_details = MonitoringDetails.objects.filter(o_id_id=o_id).values_list()
    app_names =  json.dumps([i[1] for i in depth_moni_details])
    app_usage_time =  json.dumps([i[2] for i in depth_moni_details])
    eids = json.dumps([i[4] for i in depth_moni_details])
    dates = json.dumps([i[3] for i in depth_moni_details])
    context = {'employees':employees,'app_usage_time':app_usage_time, 'app_names':app_names,'eids':eids, 'dates':dates}
    return render(request, 'logsDashboard.html', context)    


def org_view_attendance(request):
    try:
        o_id = request.session['o_id']
        emp_details = Employee.objects.filter(o_id_id=o_id).values()
        if request.method=='POST':
            e_id = request.POST['e_id']
            m_date = request.POST['date_log']
            m_date = datetime.datetime.strptime(m_date, '%Y-%m-%d')
            m_date = datetime.datetime.strftime(m_date, '%Y-%#m-%#d')
            attendance_logs = list(AttendanceLogs.objects.filter(o_id_id=o_id, e_id_id=e_id,a_date=m_date).values_list('a_date','a_ip_address','a_time_zone','a_lat','a_long'))[0]
            logged_in_time = list(AttendanceLogs.objects.filter(o_id_id=o_id, e_id_id=e_id,a_date=m_date, a_status=1).values_list('a_time'))[0][0]
            logged_out_time = list(AttendanceLogs.objects.filter(o_id_id=o_id, e_id_id=e_id,a_date=m_date, a_status=0).values_list('a_time'))[0][0]
            logged_in_time = datetime.datetime.fromtimestamp(int(logged_in_time)).strftime('%H:%M:%S')
            logged_out_time = datetime.datetime.fromtimestamp(int(logged_out_time)).strftime('%H:%M:%S')
            total_time_logged = datetime.datetime.strptime(logged_out_time,"%H:%M:%S") - datetime.datetime.strptime(logged_in_time,"%H:%M:%S")
            context = {
                "msg": emp_details, 'attendance_logs':list(attendance_logs), 'logged_in_time':logged_in_time, 'logged_out_time':logged_out_time, 'total_time_logged':total_time_logged
            }
            return render(request, 'Attendance.html', context)
        else:
            return render(request, 'Attendance.html', {"msg": emp_details})
    except:
        messages.error(request,"Data not found or some error was occurred!")
        return HttpResponseRedirect('/org-view-attendance')


def get_exact_time(date_str, timestamp):

    # Convert the timestamp to a datetime object
    timestamp_dt = str(datetime.datetime.fromtimestamp(int(timestamp)))

    return timestamp_dt[-8:]


def get_work_productivity_details(o_id, e_id, m_date):
        md_date_f1 = datetime.datetime.strptime(m_date, '%Y-%m-%d')
        md_date_f2 = datetime.datetime.strftime(md_date_f1, '%Y-%#m-%#d')
        sum_of_emp_prod = []

        wp_ds_pr_details_unclean = list(WorkProductivityDataset.objects.filter(
            o_id_id=o_id, w_type='1').values_list('w_pds'))
        wp_ds_un_pr_details_unclean = list(WorkProductivityDataset.objects.filter(
            o_id_id=o_id, w_type='0').values_list('w_pds'))
        emp_work_data_details_unclean = list(MonitoringDetails.objects.filter(
            o_id_id=o_id, e_id_id=e_id, md_date=md_date_f2).values_list('md_title', 'md_total_time_seconds').distinct())

        wp_ds_pr_details = [
            item for x in wp_ds_pr_details_unclean for item in x]
        wp_ds_un_pr_details = [
            item for x in wp_ds_un_pr_details_unclean for item in x]
        emp_work_data_details = [
            item for x in emp_work_data_details_unclean for item in x]


        combined_wp_ds_pr_un_pr = wp_ds_pr_details + wp_ds_un_pr_details

        for emp, ti in emp_work_data_details_unclean:
            for pr in wp_ds_pr_details:
                ratio = fuzz.partial_ratio(emp, pr)
                if ratio >= 60:
                    sum_of_emp_prod.append(tuple((emp, 1, ti)))

        for emp, ti in emp_work_data_details_unclean:
            for un_pr in wp_ds_un_pr_details:
                ratio = fuzz.partial_ratio(emp, un_pr)
                if ratio >= 60:
                    sum_of_emp_prod.append(tuple((emp, 2, ti)))

        for emp, ti in emp_work_data_details_unclean:
            for combined_pr_un_pr in combined_wp_ds_pr_un_pr:
                ratio = fuzz.partial_ratio(emp, combined_pr_un_pr)
                if ratio >= 5:
                    sum_of_emp_prod.append(tuple((emp, 3, ti)))
        return sum_of_emp_prod

def get_prod_details(request, eidanddate):
    e_id = eidanddate.split('and')[0]
    m_date = eidanddate.split('and')[1]
    o_id = eidanddate.split('and')[2]
    sum_of_emp_prod = get_work_productivity_details(o_id, e_id, m_date)
    prd_total = 0 
    unprd_total = 0
    undef_total = 0   
    for i in sum_of_emp_prod:
        if i[1]==1:
            prd_total = prd_total+int(i[2])
        if i[1]==2:
            unprd_total = unprd_total+int(i[2])
        if i[1]==3:
            undef_total = undef_total+int(i[2])
    titles = ['prd_total', 'unprd_total', 'undef_total']
    values = [prd_total, unprd_total, undef_total]
    total_dict = dict(zip(titles, values))
    return JsonResponse(total_dict)

@org_login_required
def view_project_wise_employees(request):
    pids = list(Project.objects.filter(o_id_id=request.session['o_id']).values_list('id', flat=True))
    projEmps = {}
    eids = []
    eid_enames = dict(Employee.objects.filter(o_id_id=request.session['o_id']).values_list('id','e_name'))
    pnames = list(Project.objects.filter(o_id_id=2).values_list('p_name', flat=True))
    enames = []
    for pid in pids:
        e = list(Project_Employee_Linker.objects.filter(o_id_id=request.session['o_id'],p_id=pid).values_list('e_id', flat=True))
        eids.append(e)
        enames.append([eid_enames[i] for i in e])
    projEmps = dict(zip(pnames, enames))
    print(dict(zip(pnames, enames)))
    return render(request, 'ViewProjEmps.html', {'projEmps':projEmps})


def get_overall_work_productivity_details(o_id, e_id):
        sum_of_emp_prod = []

        wp_ds_pr_details_unclean = list(WorkProductivityDataset.objects.filter(
            o_id_id=o_id, w_type='1').values_list('w_pds'))
        wp_ds_un_pr_details_unclean = list(WorkProductivityDataset.objects.filter(
            o_id_id=o_id, w_type='0').values_list('w_pds'))
        emp_work_data_details_unclean = list(MonitoringDetails.objects.filter(
            o_id_id=o_id, e_id_id=e_id).values_list('md_title', 'md_total_time_seconds'))

        wp_ds_pr_details = [
            item for x in wp_ds_pr_details_unclean for item in x]
        wp_ds_un_pr_details = [
            item for x in wp_ds_un_pr_details_unclean for item in x]
        emp_work_data_details = [
            item for x in emp_work_data_details_unclean for item in x]

        combined_wp_ds_pr_un_pr = wp_ds_pr_details + wp_ds_un_pr_details

        for emp, ti in emp_work_data_details_unclean:
            for pr in wp_ds_pr_details:
                ratio = fuzz.partial_ratio(emp, pr)
                if ratio >= 70:
                    sum_of_emp_prod.append(tuple((emp, 1, ti)))

        for emp, ti in emp_work_data_details_unclean:
            for un_pr in wp_ds_un_pr_details:
                ratio = fuzz.partial_ratio(emp, un_pr)
                if ratio >= 70:
                    sum_of_emp_prod.append(tuple((emp, 2, ti)))

        for emp, ti in emp_work_data_details_unclean:
            for combined_pr_un_pr in combined_wp_ds_pr_un_pr:
                ratio = fuzz.partial_ratio(emp, combined_pr_un_pr)
                if ratio >= 5:
                    sum_of_emp_prod.append(tuple((emp, 3, ti)))
        return sum_of_emp_prod


def get_only_prod_details(oid, eid):
    o_id = oid
    e_id = eid
    sum_of_emp_prod = get_overall_work_productivity_details(o_id, e_id)
    prd_total = 0 
    unprd_total = 0
    undef_total = 0   
    for i in sum_of_emp_prod:
        if i[1]==1:
            prd_total = prd_total+int(i[2])
        if i[1]==2:
            unprd_total = unprd_total+int(i[2])
        if i[1]==3:
            undef_total = undef_total+int(i[2])
    titles = ['prd_total', 'unprd_total', 'undef_total']
    values = [prd_total, unprd_total, undef_total]
    total_dict = dict(zip(titles, values))
    return prd_total


@org_login_required
def get_emp_logged_in_count_today(request):
    o_id = request.session['o_id']
    total_emps = Employee.objects.filter(o_id_id=o_id).count()
    logged_in_count = AttendanceLogs.objects.filter(o_id=o_id, a_date=datetime.datetime.today().strftime('%Y-%#m-%#d'), a_status=1).count()
    return JsonResponse({'total_emps':total_emps, 'logged_in_count':logged_in_count})


@csrf_exempt
def logout(request):
    if request.method == 'POST':
        try:
            for key in list(request.session.keys()):
                del request.session[key]
            messages.success(request, "You are logout successfully!")
            return HttpResponseRedirect('/')
        except:
            messages.error(request, "Some error was occurred in logout!")
            return HttpResponseRedirect('/')


# ----------------------------------------------------------------------------------------
@csrf_exempt
def get_select_result(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Query the database for the provided email and password
        try:
            employee = Employee.objects.get(e_email=email, e_password=password)
        except Employee.DoesNotExist:
            # If no matching record is found, return authentication failure
            return JsonResponse({'success': False})

        # If authentication succeeds, return the employee details
        result = {
            'success': True,
            'result': {
                'e_name': employee.e_name,
                'id': employee.id,
                'o_id_id': employee.o_id_id
            }
        }
        return JsonResponse(result)

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def push_power_logs_to_db(request):
    if request.method == 'POST':
        # Extract data from the request
        pm_status = request.POST.get('pm_status')
        pm_log_ts = request.POST.get('pm_log_ts')
        e_id_id = request.POST.get('e_id_id')
        o_id_id = request.POST.get('o_id_id')

        # Perform your logic to save power logs to the database
        # Example:
        power_log = PowerMonitoring.objects.create(
            pm_status=pm_status,
            pm_log_ts=pm_log_ts,
            e_id_id=e_id_id,
            o_id_id=o_id_id
        )
        power_log.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_monitoring_app(request):
    if request.method == 'POST':
        # Extract data from the request
        e_id = request.POST.get('e_id')
        o_id = request.POST.get('o_id')
        flag = request.POST.get('flag')

        # Perform your logic for monitoring app based on the flag
        # Example:
        if flag == "1":
            # Start monitoring
            # Implement your monitoring logic here
            pass
        elif flag == "0":
            # Stop monitoring
            # Implement your logic to stop monitoring here
            pass
        else:
            return JsonResponse({'error': 'Invalid flag value'})

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def save_screenshot(file, folder_path):
    try:
        # Generate a unique file name for the image
        image_name = 'image_' + str(uuid.uuid4()) + '.jpeg'  # You can use any format you prefer

        # Construct the full file path
        file_path = os.path.join(folder_path, image_name)

        # Write the file to the specified folder
        with open(file_path, 'wb') as f:
            f.write(file.read())

        file_path = "/static/Uploads/" + image_name
        return file_path
    except Exception as e:
        return None

@csrf_exempt
def push_screenshot_logs_to_db(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body

        # Extract data from the parsed JSON
        screenshot_data = request.FILES.get('ssm_img')
        e_id = request.POST.get('e_id_id')
        o_id = request.POST.get('o_id_id')
        tm = request.POST.get('ssm_log_ts')

        # Process the screenshot data and save it to the database
        if screenshot_data and e_id and o_id:
            try:
                # Assuming e_id is the ID of the Employee object
                employee_id = int(e_id)
                try:
                    employee = Employee.objects.get(pk=employee_id)
                except Employee.DoesNotExist:
                    # Handle the case where the Employee does not exist
                    employee = None
                # Assuming o_id is the ID of the Organization object
                org_id = int(o_id)
                try:
                    org = Organization.objects.get(pk=org_id)
                except Employee.DoesNotExist:
                    # Handle the case where the Employee does not exist
                    org = None

                folder_path = 'D:\\Pycharm Projects\\Outwork\\Monitoring\\MyRemoteDeskWebApp\\static\\Uploads'
                file_path = save_screenshot(screenshot_data, folder_path)

                if file_path:
                    # Create the ScreenShotsMonitoring object
                    screenshot_log = ScreenShotsMonitoring.objects.create(
                        ssm_img=file_path,
                        e_id=employee,  # Assign the Employee instance
                        o_id=org,
                        ssm_log_ts=datetime.datetime.now()
                    )
                    screenshot_log.save()

                    return JsonResponse({'success': True, 'message': 'Screenshot data saved successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to save image file'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Incomplete data provided'})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def push_start_attendance_logs_to_db(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Extract data from the parsed JSON
            a_date = data.get('a_date')
            a_time = data.get('a_time')
            a_status = data.get('a_status')
            a_ip_address = data.get('a_ip_address')
            a_time_zone = data.get('a_time_zone')
            a_lat = data.get('a_lat')
            a_long = data.get('a_long')
            e_id_id = data.get('e_id_id')
            o_id_id = data.get('o_id_id')

            # Create the AttendanceLogs object
            attendance_log = AttendanceLogs.objects.create(
                a_date=a_date,
                a_time=a_time,
                a_status=a_status,
                a_ip_address=a_ip_address,
                a_time_zone=a_time_zone,
                a_lat=a_lat,
                a_long=a_long,
                e_id_id=e_id_id,
                o_id_id=o_id_id,
            )
            attendance_log.save()

            return JsonResponse({'success': True, 'message': 'Attendance log saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_ip_data(request):
    try:
        response = requests.get('https://ipinfo.io/json')
        ip_data = response.json()

        # Extract the required data from the API response
        query = ip_data.get('ip', '')
        timezone = ip_data.get('timezone', '')
        lat_long = ip_data.get('loc', '').split(',')
        lat = lat_long[0]
        lon = lat_long[1]

        # Prepare the data to be sent back as JSON response
        data = {
            'query': query,
            'timezone': timezone,
            'lat': lat,
            'lon': lon
        }

        return JsonResponse(data)

    except Exception as e:
        # Handle any errors that occur during the process
        return JsonResponse({'error': str(e)}, status=500)
