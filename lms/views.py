from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CreateUserForm, StaffDetailsForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from .models import *
from django.utils import timezone
from django.db.models import Min
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
import io
from django.utils.timezone import make_naive
from django.utils.timezone import is_aware
import pandas as pd
from .forms import LeaveDownloadForm
import json
from django.db.models import Max
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from itertools import chain
from django.db.models import Q




class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


def notification_save(notification_username,notification_message):
    staff_notify = StaffDetails.objects.get(username_copy = notification_username)
    staff_notify.notification_message = notification_message
    staff_notify.notification_display = True
    staff_notify.save()



def send_email(subject, body, to_email):#This is email sending function
    # Create the MIME object
    message = MIMEMultipart()
    message['From'] ="freefireoff2020@gmail.com"
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    # Establish a connection to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        try:
            # Upgrade the connection to a secure TLS connection
            server.starttls()

            # Log in to the SMTP server
            server.login('freefireoff2020', 'ctps wjel lklv whfg')

            # Send the email
            server.sendmail('freefireoff2020', to_email, message.as_string())

            print("Email sent successfully. to ", to_email)
        except Exception as e:
            print(f"Error sending email: {e} to", to_email)
    


def get_user_common_context(request):
    staff_notification = StaffDetails.objects.get(username_copy = request.user.username)
    if staff_notification.notification_display:
        answer = True
        notification_message= staff_notification.notification_message
        staff_notification.notification_display = False
        staff_notification.save()
    else:
        answer = False
        notification_message = None
    
    user_common_context = {
        'notify':answer,
        'notification_message':notification_message,
        'bell_message' : StaffDetails.objects.get(username_copy = request.user.username).notification_message,
        'username': request.user.first_name,
        'email': request.user.email,
    }


    return user_common_context


@login_required
def home(request):
    username = request.user.username
    
    

    last_leave = {}

# Define a list of all leave model classes
    leave_models = [casual_leave, LOP_leave, earnLeave, vaccationLeave, onDuty, specialOnduty, medicalLeave, CH_leave]

    # Loop through each leave model class
    for leave_model in leave_models:
        try:
            # Get the latest leave record for the current model
            last_leave_instance = leave_model.objects.filter(username=username).latest('date_Applied')
            # Store the latest date applied in the dictionary with the leave type as the key
            last_leave[leave_model.__name__] = last_leave_instance.date_Applied.strftime("%d/%m/%y %I.%M %p")
        except leave_model.DoesNotExist:
           
        # If no record exists for the current model, set the value to "Not Applied Yet"
            last_leave[leave_model.__name__] = "Not Applied Yet" # No records found for this leave type


    
    

    specific_context = {
        'last_leave': last_leave,
        
    }
    user_common_context = get_user_common_context(request)
    context = merge_contexts(user_common_context,specific_context)
    return render(request, 'index.html', context)


@login_required
def profile(request):
       
    specific_context = {
         
         'firstname':request.user.first_name,
         'lastname':request.user.last_name,
         'Department':StaffDetails.objects.get(username_copy = request.user.username).department,
         'Doj':StaffDetails.objects.get(username_copy = request.user.username).doj,
    }
    user_common_context = get_user_common_context(request)
    context = merge_contexts(user_common_context,specific_context)
    return render(request, 'profile.html',context)


@login_required
def casual_leave_function(request):
    if request.method=='POST':
        username = request.user.username    
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        fromDate_month = fromDate.month
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        session = request.POST.get("session")
        print(session)
        if session == 'fullDay':
            tot_days = days_difference
        else:
            tot_days = float((days_difference)/2)
            print("TOTTTTT",tot_days)
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        # username = request.session.get('username')
        print("CS" , username)
        # result = casual_leave.objects.filter(username=username) 
        remaining = float(Leave_Availability.objects.get(username = username).casual_remaining)
        print(remaining)
        total_leave = tot_days


        # if len((result))>0:

        #     remaining = result.aggregate(Min('remaining'))['remaining__min']
        #     print("rem",remaining)
            # remaining1 = result.filter(username=username).order_by('remaining').first()
            # print('remmm',remaining1)
        # remaining += float(StaffDetails.objects.get(username_copy = request.user.username).casual_leave_avail)
        # print(remaining)
        # if remaining == 0:
        #      remaining  += float(StaffDetails.objects.get(username_copy = request.user.username).casual_leave_avail)


        print('user :' ,username)
        print(request.user)
        
        print(tot_days,'--=-')
        leave_count_result = casual_leave.objects.filter(username=username, status='Approved', from_Date__startswith=f'{fromDate.year}-{fromDate.month:02}')
        print(len(leave_count_result),'--')
        if (remaining)<=0 or remaining<tot_days or days_difference>1 or  days_difference <= 0 or len(leave_count_result)==1:
            specific_context = {
                "remaining" : remaining,
                "flag" : True,
                'user':username,
                "this_month" : len(leave_count_result)
                
            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            print("Exceed")
            return render(request , "casual_leave.html" , context=context)        
        print(remaining)
        

        # specific_context = {
        #     "days" : tot_days,
        #     "remaining" : remaining-total_leave,
        #     "flag" : False,
        #     "leave_type" : "Casual Leave",
        #     'user':username,
        #     "leave_count":len(leave_count_result)
        # }
        # user_common_context = get_user_common_context(request)
        # context = merge_contexts(user_common_context,specific_context)

        
        casual_leave_instance  = casual_leave(
        username = username,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        remaining = remaining,
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        casual_leave_instance.save()
        return redirect('Home')
    else:
        context = get_user_common_context(request)
        return render(request, 'casual_leave.html',context)


@login_required
def lop_leave_function(request):
    if request.method=='POST':
        username = request.user.username
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        session = request.POST.get("session")
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        if session == 'fullDay':
            tot_days = days_difference
        else:
            tot_days = (days_difference)/2
        date_difference_days = date_difference.days
        # username = request.session.get('username')
        if date_difference_days < 0:
            specific_context = {             
                "flag" : True,
                "message" : "Date Invalid"           
            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            return render(request, 'lop_leave.html',context=context)

        
        

    
        result = LOP_leave.objects.filter(username=username) 
        total_leave = tot_days
        if len((result))>0:
            total_leave = result[len(result)-1].total_leave
            total_leave+=float(tot_days)
            
    
        
        LOP_leave_instance  = LOP_leave(
        username = username,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        LOP_leave_instance.save()
            
            
        return redirect('Home')
    else:
        context = get_user_common_context(request)
        return render(request,'lop_leave.html',context)
    


def earn_leave_function(request):
    if request.method=='POST':
        username = request.user.username
        
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        fromDate_month = fromDate.month
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        selected_option = request.POST.get('option')
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        tot_days = days_difference
        # username = request.session.get('username')
        print("CS" , username)
        print("Name:",  )
        result = earnLeave.objects.filter(username=username)
        year_instance = StaffDetails.objects.filter(username_copy = request.user.username)
        print(result)
        
        applying_year = fromDate.year
        # Get the year of the applying date and the joined date
        joined_year = year_instance[0].doj.year

        # Calculate the year 3 years after the joined date
        eligible_year = joined_year + 3

        # print(applying_year)
        print(eligible_year)
        print(joined_year)
        # Check if the applying year is at least 3 years greater than the joined year
       

        remaining = float(Leave_Availability.objects.get(username = request.user.username).earn_leave_remaining)
        total_leave = tot_days
        

            
        print(tot_days,'--=-')
        
        leave_count_result = earnLeave.objects.filter(username=username, status='Approved', from_Date__startswith=f'{fromDate.year}-{fromDate.month:02}')
        print(len(leave_count_result),'--')


        if remaining<=0 or float(remaining)<float(tot_days) or applying_year < eligible_year or days_difference <= 0 or int(len(leave_count_result))==5:
            specific_context = {
                "remaining" : remaining,
                "flag" : True,
                'user':username,
                "this_month" : len(leave_count_result)
                
            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            print("Exceed")
            return render(request , "earn_leave.html" , context=context)        
        # print(remaining)


        
        earn_leave_instance  = earnLeave(
        leave_type = selected_option,
        username = username,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        remaining = remaining,
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        earn_leave_instance.save()
            
            
        return redirect('Home')
    else:
        context = get_user_common_context(request)
        return render(request, 'earn_leave.html',context)
    

def vaccation_leave_function(request):
    if request.method=='POST':
        
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        session = request.POST.get("session")
        selected_option = request.POST.get('option')
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        if session == 'fullDay':
            tot_days = days_difference
        else:
            tot_days = (days_difference)/2
        username = request.user.username
        staff_name = request.user.first_name
        remaining = Leave_Availability.objects.get(username = username).vaccation_remaining
        if remaining<=0 or float(remaining)<float(tot_days) or days_difference <= 0:
            specific_context = {
            "days" : tot_days,
            "flag" : False,
            "leave_type" : "Vaccation Leave",
            'user':username,

            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            return render(request, 'vaccation_leave.html',context = context)


        total_leave = tot_days
        # if len((result))>0:
        #     total_leave = result[len(result)-1].total_leave
        #     total_leave+=float(tot_days)
        
            
    
        
        vaccation_leave_instance  = vaccationLeave(
        username = username,
        leave_type = selected_option,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        vaccation_leave_instance.save()
            
            
        return redirect("Home")
    else:
        context = get_user_common_context(request)
        return render(request,'vaccation_leave.html',context)

def onduty_function(request):
    if request.method=='POST':
        username = request.user.username
        
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        fromDate_month = fromDate.month
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        tot_days = days_difference
        # username = request.session.get('username')
        print("CS" , username)
        result = onDuty.objects.filter(username=username) 
        remaining = Leave_Availability.objects.get(username = username).onduty_remaining
        total_leave = tot_days
        # if len((result))>0:

        #      remaining = result.aggregate(Min('remaining'))['remaining__min']
        #      print("rem",remaining)

            
        print(tot_days,'--=-')
        print(username)

        
        # leave_count_result = onDuty.objects.filter(username=username, status='Approved', from_Date__startswith=f'{fromDate.year}-{fromDate.month:02}')
        # print(len(leave_count_result),'--')
        if float(remaining)<=0 or float(remaining)<tot_days or days_difference>float(remaining) or  days_difference <= 0:
            specific_context = {
                "remaining" : remaining,
                "flag" : True,
                "user":username
                # "this_month" : len(leave_count_result)
                
            }
            print("Exceed")
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            return render(request , "onduty.html" , context=context)        

        
        onduty_instance  = onDuty(
        username = username,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        remaining = remaining,
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        onduty_instance.save()
            
            
        return redirect("Home")
    else:
        context = get_user_common_context(request)
        return render(request,'onduty.html',context)
    
def special_onduty_function(request):
    if request.method=='POST':
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        session = request.POST.get("session")
        selected_option = request.POST.get('option')
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        if session == 'fullDay':
            tot_days = days_difference
        else:
            tot_days = (days_difference)/2
        username = request.user.username
        
        specific_context = {
            "days" : tot_days,
            "flag" : False,
            "leave_type" : "LOP Leave",
            'user':username,
        }
        result = specialOnduty.objects.filter(username=username) 
        total_leave = tot_days
        if len((result))>0:
            total_leave = result[len(result)-1].total_leave
            total_leave+=float(tot_days)
            
    
        
        speical_onduty_instance  = specialOnduty(
        username = username,
        leave_type = selected_option,
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        speical_onduty_instance.save()
            
            
        return redirect("Home")
    else:
        context = get_user_common_context(request)
        return render(request, 'special_onduty.html',context)
  
def CH_leave_function(request):
    if request.method=='POST':
        username = request.user.username
        
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        fromDate_month = fromDate.month
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        session = request.POST.get("session")
        if session == 'fullDay':
            tot_days = days_difference
        else:
            tot_days = float((days_difference)/2)
            print("TOTTTTT",tot_days)
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        # username = request.session.get('username')
        print("CS" , username)
        result = CH_leave.objects.filter(username=username) 
        print(result)
        # remaining_q = login_details.objects.get(username=username)
        remaining = Leave_Availability.objects.get(username = username)


        total_leave = tot_days

       


            
        print(tot_days,'--=-')
        
        if remaining<=0 or remaining<tot_days  or  days_difference <= 0 :
            specific_context = {
                "remaining" : remaining,
                "flag" : True,
                'user':request.user.username
                
            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            print("Exceed")

            return render(request , "ch_leave.html" , context=context)        
        # print(remaining)


        
        CH_leave_instance  = CH_leave(
        username = username.upper(),
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        total_leave = total_leave,
        remaining = remaining,
        reason = request.POST.get("reason"),
        document = document
        )
        CH_leave_instance.save()
            
            
        return redirect("Home")
    else:
        context = get_user_common_context(request)
        return render(request,'ch_leave.html',context)
  

def medical_leave_function(request):
    if request.method=='POST':
        username = request.user.username
        
        fromDate_str = request.POST.get("fromDate")
        toDate_str = request.POST.get("toDate")
        fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
        fromDate_month = fromDate.month
        toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        date_difference = toDate - fromDate
        days_difference = (date_difference.days)+1
        if 'file' in request.FILES:
            document = request.FILES['file'] 
            print(document)
        else:
            document = None
            print(document)
        tot_days = days_difference
        # username = request.session.get('username')
        print("CS" , username)
        result = medicalLeave.objects.filter(username=username.upper()) 
        user_login_details = StaffDetails.objects.get(first_name=request.user.first_name)

    # Get the year of the applying date and the joined date
        applying_year = fromDate.year
        joined_year = user_login_details.doj.year

        # Calculate the year 3 years after the joined date
        eligible_year = joined_year + 3

        print(applying_year)
        print(eligible_year)
        # Check if the applying year is at least 3 years greater than the joined year
       

        remaining = Leave_Availability.objects.get(username =username)

        total_leave = tot_days
        # if len((result))>0:

        #      remaining = int(result.aggregate(Min('remaining'))['remaining__min'])
        #      print("rem",remaining)

            
        print(tot_days,'--=-')
        
        
        leave_count_result = medicalLeave.objects.filter(username=username, status='Approved', from_Date__startswith=f'{fromDate.year}-{fromDate.month:02}')
        print(len(leave_count_result),'--')

        if remaining<0 or int(remaining)<int(tot_days) or applying_year < eligible_year or days_difference <= 0:
            specific_context = {
                "remaining" : remaining,
                "flag" : True,
                'user':username.upper(),
                "this_month" : len(leave_count_result)
                
            }
            user_common_context = get_user_common_context(request)
            context = merge_contexts(user_common_context,specific_context)
            print("Exceed")
            return render(request , "medical_leave.html" , context=context)        
        # print(remaining)


        
        medical_leave_instance  = medicalLeave(
        username = username.upper(),
        date_Applied = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_Date = fromDate_str,
        to_Date = toDate_str,
        session = request.POST.get("session"),
        remaining = remaining,
        total_leave = total_leave,
        reason = request.POST.get("reason"),
        document = document
        )
        medical_leave_instance.save()
            
            
        return redirect("Home")
    else:
        context = get_user_common_context(request)
        return render(request,'medical_leave.html',context)
  


def hr_view_function(request):

    return render(request,'custom_admin/index.html')


def admin_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser and user.is_staff and user.is_active:
            login(request, user)
            return redirect('AdminPage')
        elif user is not None and user.is_active and user.is_staff and not user.is_superuser:
            login(request,user)
            return redirect("HODPage")
             
        else:
            context={
                'error_message':"Wrong Username or Password"
            }
            return render(request,'admin-login.html',context)
        
    else:
        return render(request,'admin-login.html')

def get_common_context(request):
    user_details = StaffDetails.objects.get(username_copy=request.user.username)
    leave_types = [
            casual_leave, LOP_leave, CH_leave, medicalLeave,
            earnLeave, vaccationLeave, specialOnduty, onDuty
        ]

    all_records = []

    for leave_type in leave_types:
        records = leave_type.objects.filter(status='Approved(1)').order_by('-date_Applied')
        all_records = list(chain(all_records, records))

    all_records_sorted = sorted(all_records, key=lambda x: x.date_Applied, reverse=True)

    recent_records = all_records_sorted[:5]

    recent_data = [{'username': record.username, 'leave_type': record.leave_type} for record in recent_records]

    casual_leave_count = casual_leave.objects.filter(status='Approved(1)').count()
    LOP_leave_count = LOP_leave.objects.filter(status='Approved(1)').count()
    CH_leave_count = CH_leave.objects.filter(status='Approved(1)').count()
    medicalLeave_count = medicalLeave.objects.filter(status='Approved(1)').count()
    earnLeave_count = earnLeave.objects.filter(status='Approved(1)').count()
    vaccationLeave_count = vaccationLeave.objects.filter(status='Approved(1)').count()
    specialOnduty_count = specialOnduty.objects.filter(status='Approved(1)').count()
    onDuty_count = onDuty.objects.filter(status='Approved(1)').count()

    # Sum of all counts
    total_approved_count = (
        casual_leave_count + LOP_leave_count + CH_leave_count + medicalLeave_count +
        earnLeave_count + vaccationLeave_count + specialOnduty_count + onDuty_count
    )

    common_context = {
        'notification_message': user_details.notification_message,
        'recent_data': recent_data, 
        'pending':int(total_approved_count),
        'admin': 'HR'
    }
    return common_context

def merge_contexts(common_context, specific_context):
    context = common_context.copy()
    context.update(specific_context)
    return context


@login_required    
def admin_page(request , username=None):
    user = request.user
    is_superuser = user.is_superuser
    is_staff = user.is_staff

    if request.user.is_superuser:
        print("User is a superuser")
        common_context = get_common_context(request)
        if request.resolver_match.url_name == "NewRequests":
            print("New Request")

            result = casual_leave.objects.all()

            data_list_of_dicts = []
            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                print(settings.MEDIA_URL + str(item.document) )
                data_list_of_dicts.append(data_dict)

            result = LOP_leave.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                    
                }
                print(settings.MEDIA_URL + str(item.document) )
                data_list_of_dicts.append(data_dict)
                # print(data_list_of_dicts)

            result = CH_leave.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                    
                }
                data_list_of_dicts.append(data_dict)

            result = medicalLeave.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = earnLeave.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = vaccationLeave.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = specialOnduty.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = onDuty.objects.all()

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)
            # print(data_list_of_dicts)

            specific_context = {
                'admin_list' : data_list_of_dicts
            }
            context = merge_contexts(common_context,specific_context)

            return render(request, 'custom_admin/new_requests.html', context=context)
        
        
        elif request.resolver_match.url_name == "AddStaff":
            if request.method == 'POST':
                print(request.POST)
                user_form = CreateUserForm(request.POST)
                staff_form = StaffDetailsForm(request.POST)

                if user_form.is_valid() and staff_form.is_valid():
                    is_staff = request.POST.get('is_staff')
                    is_superuser = request.POST.get('is_superuser')  
                       

                    user = user_form.save(commit=False)
                    if is_staff:
                        user.is_staff = True
                    if is_superuser:
                        user.is_superuser = True

                    user.save()
                    staff_details = staff_form.save(commit=False)
                    staff_details.user = user
                    staff_details.first_name = user.first_name
                    staff_details.last_name = user.last_name
                    print(user.username)
                    casual = request.POST.get("casual")
                    vaccation = request.POST.get("vaccation")
                    onduty = request.POST.get("onduty")
                    medical = request.POST.get("medical")
                    earn = request.POST.get("earn")
                    leave_availability_instance = Leave_Availability(
                        username = user.username,
                        casual_remaining = int(casual),
                        vaccation_remaining = int(vaccation),
                        onduty_remaining = int(onduty),
                        medical_leave_remaining = int(medical),
                        earn_leave_remaining = int(earn),
                        ch_leave_remaining = 0
                    )
                    leave_availability_instance.save()
                    
                    staff_details.save()

                    notification_save(request.user.username,f"New Staff {user.username} was added Successfully")
                    
                    messages.info(request, "Staff was added Successfully")
                    return redirect('AddStaff')
            else:
                user_form = CreateUserForm()
                staff_form = StaffDetailsForm()

            specific_context = {
                'user_form': user_form,
                'staff_form': staff_form,
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/addstaff.html', context=context)
        
        
        elif request.resolver_match.url_name == 'DeleteStaff':
            if request.method == 'POST':
                staff = User.objects.get(username = username)
                leave_availabilities = Leave_Availability.objects.get(username = username)
                leave_availabilities.delete()
                # check = StaffDetails.objects.get(username_copy = username).department
                # print("HII",check)
                print(staff)
                staff.delete()
                notification_save(request.user.username,f"{username} was deleted Successfully")
                messages.success(request, f'{username} details deleted successfully.')
                return redirect('DeleteStaffView')
            
            # print(User.objects.all())
            specific_context={
                'staff_members':User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False)
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/deletestaff.html' ,context=context)
        
        
        elif request.resolver_match.url_name == 'DeleteStaffView':
            search_id = request.GET.get('search_id')
            print(search_id)

            if search_id:
                staff_members = User.objects.filter(username=search_id).filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)

            else:
                staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False)

            specific_context = {
                'staff_members': staff_members
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/deletestaff.html' ,context=context)
        
        
        elif request.resolver_match.url_name == 'EditStaffView':
            search_id = request.GET.get('search_id')
            print(search_id)

            if search_id:
                staff_details = User.objects.filter(username=search_id)
                print(staff_details)

            else:
                staff_details = User.objects.all()
            
            # staff_details = User.objects.all()
            specific_context = {
                'staff_details':staff_details
            }
            context = merge_contexts(common_context,specific_context)
            return render(request, "custom_admin/editstaff.html",context=context)
        
       
        elif request.resolver_match.url_name == 'EditStaff':
            if request.method == "POST":
                username_from_function = username
                staff_instance = User.objects.get(username=username_from_function)
                username = request.POST.get("username")
                first_name = request.POST.get("first_name")
                last_name = request.POST.get("last_name")
                email = request.POST.get("email")
                is_active = request.POST.get('is_active') == 'on'  # Convert 'on' to boolean
                is_staff = request.POST.get('is_staff') == 'on'
                is_superuser = request.POST.get('is_superuser') == 'on'
                
                # Assuming you already have the user instance
                
                
                
                # Update user attributes
                staff_instance.username = username
                staff_instance.first_name = first_name
                staff_instance.last_name = last_name
                staff_instance.email = email
                staff_instance.is_active = is_active
                staff_instance.is_staff = is_staff
                staff_instance.is_superuser = is_superuser

                staff_instance.save()
                notification_save(request.user.username,f"{username_from_function} user was edited Successfully")
                messages.info(request, f"{username_from_function} user was edited Successfully!")

                return redirect('EditStaffView')
                

        elif request.resolver_match.url_name == "AvailLeaveView":
            search_id = request.GET.get('search_id')
            if search_id:
                staff_members = User.objects.filter(username=search_id).filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)

            else:
                staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False)
            specific_context = {
                'staff_members':staff_members
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/availleave.html' , context = context)
            

        elif request.resolver_match.url_name == "AvailLeave":
            if request.method == "POST":
                
                LEAVE_TYPE_MODEL_MAP = {
                'Casual Leave': 'casual_leave_avail',
                'LOP Leave': 'LOP_leave_avail',
                'Compensated Holiday': 'CH_leave_avail',
                'Medical Leave': 'medicalLeave_avail',
                'Earn Leave': 'earnLeave_avail',
                'Vacation Leave': 'vaccationLeave_avail',
                'Special Onduty': 'specialOnduty_avail',
                'Onduty': 'onDutye_avail',
            }
                username_from_function = username
                print(username_from_function)
                leave_type = request.POST.get("leave_type")
                field_name = LEAVE_TYPE_MODEL_MAP[leave_type]
                value = request.POST.get("value")
                
                print(leave_type)
                leave_instance = StaffDetails.objects.get(username_copy=username_from_function)
                
                leave_avail = float(getattr(leave_instance, field_name))
                action = request.POST.get('action')  # Get the selected action

                leave_availibility_remaining = Leave_Availability.objects.get(username = username_from_function)

                REMAINING_TYPE_MODEL_MAP = {
                'Casual Leave': 'casual_remaining',
                # 'LOP Leave': LOP_leave,
                'Compensated Holiday': 'ch_leave_remaining',
                'Medical Leave': 'medical_leave_remaining',
                'Earn Leave': 'earn_leave_remaining',
                'Vacation Leave': 'vaccation_remaining',
                # 'Special Onduty': specialOnduty,
                'Onduty': 'onduty_remaining',
            }
                field_name1 = REMAINING_TYPE_MODEL_MAP[leave_type]
                existing_remaining = float(getattr(leave_availibility_remaining, field_name1))
                
                
                if action == 'increment':
                    leave_avail += float(value)
                    new_value = float(existing_remaining) + float(value)
                    action_text = "incremented"
                elif action == 'decrement':
                    leave_avail -= float(value)
                    new_value = float(existing_remaining) - float(value)
                    action_text = "decremented"
                # REMAINING_TYPE_MODEL_MAP[leave_type] = new_value
                
                print(REMAINING_TYPE_MODEL_MAP[leave_type])
                leave_availibility_remaining.save()
                print(Leave_Availability.objects.get(username = username_from_function).casual_remaining)

                setattr(leave_instance, field_name, leave_avail)
                setattr(leave_availibility_remaining, field_name1, new_value)
                leave_instance.save()
                leave_availibility_remaining.save()
                
                # leave_availibility_remaining.save()
                notification_save(request.user.username,f"{value} day(s) of {leave_type} was successfully {action_text} for the user {username_from_function}")
                messages.info(request,f"{value} day(s) of {leave_type} was successfully {action_text} for the user {username_from_function}")
                
                return redirect('AvailLeaveView')


        elif request.resolver_match.url_name == "DownloadView":
            search_id = request.GET.get('search_id')
            if search_id:
                staff_members = User.objects.filter(username=search_id).filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)

            else:
                staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False)
            specific_context = {
                'staff_members':staff_members
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/download.html' , context = context)


        elif request.resolver_match.url_name == "Download":
            if request.method == 'POST':
                form = LeaveDownloadForm(request.POST)
                if form.is_valid():
                    leave_type = form.cleaned_data['leave_type']

                    # Query data based on leave type
                    if leave_type == 'All':
                        leaves = []
                        for model in [casual_leave, LOP_leave, CH_leave, medicalLeave, earnLeave, vaccationLeave, specialOnduty, onDuty]:
                            leaves.extend(model.objects.filter(username=username))
                    else:
                        model_dict = {
                            'Casual Leave': casual_leave,
                            'LOP Leave': LOP_leave,
                            'CH Leave': CH_leave,
                            'Medical Leave': medicalLeave,
                            'Earn Leave': earnLeave,
                            'Vacation Leave': vaccationLeave,
                            'Onduty': onDuty,
                            'Special Onduty': specialOnduty,
                        }
                        leaves = model_dict[leave_type].objects.filter(username=username)

                    # Create a DataFrame from the queryset
                    data = []
                    for leave in leaves:
                        data.append([
                            leave.username, leave.leave_type, make_naive(leave.date_Applied), leave.from_Date,
                            leave.to_Date, leave.session, leave.remaining, leave.total_leave,
                            leave.status, leave.reason
                        ])
                    df = pd.DataFrame(data, columns=['Username', 'Leave Type', 'Date Applied', 'From Date', 'To Date', 'Session', 'Remaining', 'Total Leave', 'Status', 'Reason'])

                    # Create an in-memory Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)

                    # Send the response with the Excel file
                    output.seek(0)
                    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={username}_leaves.xlsx'
                    return response
            else:
                form = LeaveDownloadForm()
            return render(request, 'custom_admin/download.html', {'form': form})


        elif request.resolver_match.url_name == "DownloadAll":
            if request.method == 'POST':
                form = LeaveDownloadForm(request.POST)
                if form.is_valid():
                    leave_type = form.cleaned_data['leave_type']

                    # Query data based on leave type
                    if leave_type == 'All':
                        leaves = []
                        for model in [casual_leave, LOP_leave, CH_leave, medicalLeave, earnLeave, vaccationLeave, specialOnduty, onDuty]:
                            leaves.extend(model.objects.all())
                    else:
                        model_dict = {
                            'Casual Leave': casual_leave,
                            'LOP Leave': LOP_leave,
                            'CH Leave': CH_leave,
                            'Medical Leave': medicalLeave,
                            'Earn Leave': earnLeave,
                            'Vacation Leave': vaccationLeave,
                            'Onduty': onDuty,
                            'Special Onduty': specialOnduty,
                        }
                        leaves = model_dict[leave_type].objects.all()

                    # Create a DataFrame from the queryset
                    data = []
                    for leave in leaves:
                        data.append([
                            leave.username, leave.leave_type, make_naive(leave.date_Applied), leave.from_Date,
                            leave.to_Date, leave.session, leave.remaining, leave.total_leave,
                            leave.status, leave.reason
                        ])
                    df = pd.DataFrame(data, columns=['Username', 'Leave Type', 'Date Applied', 'From Date', 'To Date', 'Session', 'Remaining', 'Total Leave', 'Status', 'Reason'])

                    # Create an in-memory Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)

                    # Send the response with the Excel file
                    output.seek(0)
                    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={leave_type}_leaves.xlsx'
                    return response
            else:
                form = LeaveDownloadForm()
            return render(request, 'custom_admin/download.html', {'form': form})
            

        elif request.resolver_match.url_name == "LeaveAvailability":

            staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)

            # Get the usernames of the filtered users
            staff_usernames = staff_members.values_list('username', flat=True)

            # Filter Leave_Availability based on these usernames
            leave_data = Leave_Availability.objects.filter(username__in=staff_usernames)

            data_dics = [
            {
            'username': leave.username,
            'casual_remaining': leave.casual_remaining,
            'vaccation_remaining': leave.vaccation_remaining,
            'onduty_remaining': leave.onduty_remaining,
            'medical_leave_remaining': leave.medical_leave_remaining,
            'earn_leave_remaining': leave.earn_leave_remaining,
            'ch_leave_remaining': leave.ch_leave_remaining,
            } for leave in leave_data
            ]
            specific_context = {
                'data_dics':data_dics
            }
            context = merge_contexts(common_context,specific_context)
            print(staff_usernames)
            return render(request,'custom_admin/leave_availability.html', context)



        elif request.resolver_match.url_name == "AdminAccount":
            specific_context = {
                'email':request.user.email
            }
            context = merge_contexts(common_context,specific_context)
            return render(request,'custom_admin/account_settings.html',context)
        


        today = date.today()
        print(today)


        # Query each model and count the instances where date_Applied matches today's date
        casual_leave_count = casual_leave.objects.filter(date_Applied__date=today).count()
        LOP_leave_count = LOP_leave.objects.filter(date_Applied__date=today).count()
        CH_leave_count = CH_leave.objects.filter(date_Applied__date=today).count()
        medicalLeave_count = medicalLeave.objects.filter(date_Applied__date=today).count()
        earnLeave_count = earnLeave.objects.filter(date_Applied__date=today).count()
        vaccationLeave_count = vaccationLeave.objects.filter(date_Applied__date=today).count()
        specialOnduty_count = specialOnduty.objects.filter(date_Applied__date=today).count()
        onDuty_count = onDuty.objects.filter(date_Applied__date=today).count()

        # Sum up the counts from all models
        total_count = (
            casual_leave_count + LOP_leave_count + CH_leave_count +
            medicalLeave_count + earnLeave_count + vaccationLeave_count +
            specialOnduty_count + onDuty_count
        )



        specific_context = {
            'total_user': User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False).count(),
            'total_hod' : User.objects.filter(is_active=True,is_staff=True, is_superuser=False).count(),
            'today_applied' : total_count,
            
            'announcement_list':Announcement.objects.all().order_by('-timestamp'),
        }

        context = merge_contexts(common_context,specific_context)
        return render(request,'custom_admin/index.html', context=context)
    

def get_hod_common_context(request):
    hod_department = StaffDetails.objects.get(username_copy = request.user.username).department
    HOD_Department = hod_department.strip().replace(" ", "").upper()
    dept_users = StaffDetails.objects.filter(department=HOD_Department).values_list('user__username', flat=True)
    casual_leave_count = casual_leave.objects.filter(status='Reviewing', username__in=dept_users).count()
    LOP_leave_count = LOP_leave.objects.filter(status='Reviewing', username__in=dept_users).count()
    CH_leave_count = CH_leave.objects.filter(status='Reviewing', username__in=dept_users).count()
    medicalLeave_count = medicalLeave.objects.filter(status='Reviewing', username__in=dept_users).count()
    earnLeave_count = earnLeave.objects.filter(status='Reviewing', username__in=dept_users).count()
    vaccationLeave_count = vaccationLeave.objects.filter(status='Reviewing', username__in=dept_users).count()
    specialOnduty_count = specialOnduty.objects.filter(status='Reviewing', username__in=dept_users).count()
    onDuty_count = onDuty.objects.filter(status='Reviewing', username__in=dept_users).count()

    total_approved_count = (
        casual_leave_count + LOP_leave_count + CH_leave_count + medicalLeave_count +
        earnLeave_count + vaccationLeave_count + specialOnduty_count + onDuty_count
    )


    leave_types = [
        casual_leave, LOP_leave, CH_leave, medicalLeave,
        earnLeave, vaccationLeave, specialOnduty, onDuty
    ]

    # Initialize list to store all records
    all_records = []

    # Query and concatenate records for each leave type
    for leave_type in leave_types:
        records = leave_type.objects.filter(status='Reviewing').order_by('-date_Applied')
        all_records.extend(records)

    # Sort all records by date applied in descending order
    all_records_sorted = sorted(all_records, key=lambda x: x.date_Applied, reverse=True)

    # Get recent 5 records
    recent_records = all_records_sorted[:5]

    # Filter recent data for ECE department
    recent_data = []
    ece_staff_usernames = StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True)
    
    for record in recent_records:
        if record.username in ece_staff_usernames:
            recent_data.append({'username': record.username, 'leave_type': record.leave_type})


    hod_common_context = {
        'is_hod':True,
        'pending':int(total_approved_count),
        'recent_data': recent_data,
        'admin':HOD_Department
    }

    return hod_common_context



@login_required
def hod_page(request,username=None):
    if request.user.is_staff and request.user.is_active:
        hod_department = StaffDetails.objects.get(username_copy = request.user.username).department
        print(hod_department)
        HOD_Department = hod_department.strip().replace(" ", "").upper()
        print(HOD_Department)
        hod_common_context = get_hod_common_context(request)
        if request.resolver_match.url_name == 'HODNewRequests':
            print("New Request")

            result = casual_leave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            data_list_of_dicts = []
            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)
                print(data_list_of_dicts)

            result = LOP_leave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                print(settings.MEDIA_URL + str(item.document) )
                data_list_of_dicts.append(data_dict)
                # print(data_list_of_dicts)

            result = CH_leave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                    
                }
                data_list_of_dicts.append(data_dict)

            result = medicalLeave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = earnLeave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = vaccationLeave.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = specialOnduty.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)

            result = onDuty.objects.filter(username__in=StaffDetails.objects.filter(department=HOD_Department).values_list('username_copy', flat=True))

            for item in result:
                user_name = User.objects.get(username=item.username)
                data_dict = {
                    "reason" : item.reason,
                    "unique_id": item.unique_id,
                    "staff_name": user_name.first_name + ' ' + user_name.last_name,
                    "username": item.username,
                    "department" : StaffDetails.objects.get(username_copy = item.username).department,
                    "leave_type": item.leave_type,
                    "date_Applied": str(item.date_Applied),
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status,
                    "document_url": settings.MEDIA_URL + str(item.document) 
                }
                data_list_of_dicts.append(data_dict)
            print(data_list_of_dicts)

            specific_context = {
                'admin_list' : data_list_of_dicts,
                
            }
            context = merge_contexts(hod_common_context,specific_context)

            return render(request, 'custom_admin/hod_new_requests.html', context=context)
            


        elif request.resolver_match.url_name == 'HODLeaveAvailability':
            print("HI")

            staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)
            staff_usernames = staff_members.values_list('username', flat=True)

            # Step 2: Filter Leave_Availability based on these usernames
            leave_data = Leave_Availability.objects.filter(username__in=staff_usernames)

            # Step 3: Join with Staff_Details and filter for department 'ECE'
            ece_staff = StaffDetails.objects.filter(department=HOD_Department, username_copy__in=leave_data.values_list('username', flat=True))
            ece_usernames = ece_staff.values_list('username_copy', flat=True)

            # Step 4: Filter Leave_Availability for ECE staff and create data_dics
            ece_leave_data = leave_data.filter(username__in=ece_usernames)
            data_dics = [
                {
                    'username': leave.username,
                    'casual_remaining': leave.casual_remaining,
                    'vaccation_remaining': leave.vaccation_remaining,
                    'onduty_remaining': leave.onduty_remaining,
                    'medical_leave_remaining': leave.medical_leave_remaining,
                    'earn_leave_remaining': leave.earn_leave_remaining,
                    'ch_leave_remaining': leave.ch_leave_remaining,
                } for leave in ece_leave_data
            ]

            # Step 5: Pass context to template
            specific_context = {
                'data_dics': data_dics
            }
            context = merge_contexts(hod_common_context,specific_context)

            return render(request, 'custom_admin/leave_availability.html' ,context)


        elif request.resolver_match.url_name == "HODDownloadView":
            search_id = request.GET.get('search_id')

            if search_id:
                staff_members = User.objects.filter(username=search_id).filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)
            else:
                staff_members = User.objects.filter(Q(is_active=True) | Q(is_staff=True), is_superuser=False)

            # Join with Staff_Details to filter for department 'ECE'
            ece_staff = StaffDetails.objects.filter(department=HOD_Department, username_copy__in=staff_members.values_list('username', flat=True))
            ece_usernames = ece_staff.values_list('username_copy', flat=True)

            # Filter User for ECE staff
            ece_staff_members = staff_members.filter(username__in=ece_usernames)

            specific_context = {
                'staff_members': ece_staff_members
            }
            context = merge_contexts(hod_common_context, specific_context)
            return render(request, 'custom_admin/download.html', context=context)
        

        elif request.resolver_match.url_name == "HODDownload":
            if request.method == 'POST':
                form = LeaveDownloadForm(request.POST)
                if form.is_valid():
                    leave_type = form.cleaned_data['leave_type']

                    # Query data based on leave type
                    if leave_type == 'All':
                        leaves = []
                        for model in [casual_leave, LOP_leave, CH_leave, medicalLeave, earnLeave, vaccationLeave, specialOnduty, onDuty]:
                            leaves.extend(model.objects.filter(username=username))
                    else:
                        model_dict = {
                            'Casual Leave': casual_leave,
                            'LOP Leave': LOP_leave,
                            'CH Leave': CH_leave,
                            'Medical Leave': medicalLeave,
                            'Earn Leave': earnLeave,
                            'Vacation Leave': vaccationLeave,
                            'Onduty': onDuty,
                            'Special Onduty': specialOnduty,
                        }
                        leaves = model_dict[leave_type].objects.filter(username=username)

                    # Create a DataFrame from the queryset
                    data = []
                    for leave in leaves:
                        data.append([
                            leave.username, leave.leave_type, make_naive(leave.date_Applied), leave.from_Date,
                            leave.to_Date, leave.session, leave.remaining, leave.total_leave,
                            leave.status, leave.reason
                        ])
                    df = pd.DataFrame(data, columns=['Username', 'Leave Type', 'Date Applied', 'From Date', 'To Date', 'Session', 'Remaining', 'Total Leave', 'Status', 'Reason'])

                    # Create an in-memory Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)

                    # Send the response with the Excel file
                    output.seek(0)
                    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={username}_leaves.xlsx'
                    return response
            else:
                form = LeaveDownloadForm()
            return render(request, 'custom_admin/download.html', {'form': form})


        elif request.resolver_match.url_name == "HODDownloadAll":
            if request.method == 'POST':
                form = LeaveDownloadForm(request.POST)
                if form.is_valid():
                    leave_type = form.cleaned_data['leave_type']

                    # Query ECE department staff members
                    ece_staff = StaffDetails.objects.filter(department=HOD_Department)
                    ece_usernames = ece_staff.values_list('username_copy', flat=True)

                    # Query data based on leave type
                    if leave_type == 'All':
                        leaves = []
                        for model in [casual_leave, LOP_leave, CH_leave, medicalLeave, earnLeave, vaccationLeave, specialOnduty, onDuty]:
                            leaves.extend(model.objects.filter(username__in=ece_usernames))
                    else:
                        model_dict = {
                            'Casual Leave': casual_leave,
                            'LOP Leave': LOP_leave,
                            'CH Leave': CH_leave,
                            'Medical Leave': medicalLeave,
                            'Earn Leave': earnLeave,
                            'Vacation Leave': vaccationLeave,
                            'Onduty': onDuty,
                            'Special Onduty': specialOnduty,
                        }
                        leaves = model_dict[leave_type].objects.filter(username__in=ece_usernames)

                    # Create a DataFrame from the queryset
                    data = []
                    for leave in leaves:
                        data.append([
                            leave.username, leave.leave_type, make_naive(leave.date_Applied), leave.from_Date,
                            leave.to_Date, leave.session, leave.remaining, leave.total_leave,
                            leave.status, leave.reason
                        ])
                    df = pd.DataFrame(data, columns=['Username', 'Leave Type', 'Date Applied', 'From Date', 'To Date', 'Session', 'Remaining', 'Total Leave', 'Status', 'Reason'])

                    # Create an in-memory Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)

                    # Send the response with the Excel file
                    output.seek(0)
                    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = f'attachment; filename={leave_type}_leaves.xlsx'
                    return response
            else:
                form = LeaveDownloadForm()
            return render(request, 'custom_admin/download.html', {'form': form})


        elif request.resolver_match.url_name == "HODAdminAccount":
            specific_context = {
                'email':request.user.email
            }
            context = merge_contexts(hod_common_context,specific_context)
            return render(request,'custom_admin/account_settings.html',context)


        today = timezone.now().date()
        dept_users = StaffDetails.objects.filter(department=hod_department).values_list('user__username', flat=True)
        casual_leave_count = casual_leave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        LOP_leave_count = LOP_leave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        CH_leave_count = CH_leave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        medicalLeave_count = medicalLeave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        earnLeave_count = earnLeave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        vaccationLeave_count = vaccationLeave.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        specialOnduty_count = specialOnduty.objects.filter(date_Applied__date=today, username__in=dept_users).count()
        onDuty_count = onDuty.objects.filter(date_Applied__date=today, username__in=dept_users).count()


        total_count = (
            casual_leave_count + LOP_leave_count + CH_leave_count +
            medicalLeave_count + earnLeave_count + vaccationLeave_count +
            specialOnduty_count + onDuty_count
        )

        

        
        
        specific_context={
            'total_user': User.objects.filter(Q(is_active=True) | Q(is_staff=True) , is_superuser=False).count(),
            'total_hod' : StaffDetails.objects.filter(department = hod_department).count(),
            'today_applied' : total_count,
            'announcement_list':Announcement.objects.all().order_by('-timestamp')
        }
        context = merge_contexts(hod_common_context,specific_context)
        return render(request,'custom_admin/index.html',context)
        


     


def requests_handling(request):
    if request.method == "POST":
        data = request.POST
        print(data)


        if data.get('partial')  == 'yes': 
            subject = "Leave Update"
            body = f"""
            Hello {data.get('rowData[username]')},
                Your {data.get('rowData[leave_type]')} request applied on {data.get('rowData[date_Applied]')} was {data.get('action')} by HOD.
    """
            

                
            username = data.get('rowData[username]')
            to_email = User.objects.get(username = username).email
            print(to_email)



            leave_type = data.get('rowData[leave_type]')
            unique_id = int(data.get('rowData[unique_id]'))
            print(leave_type)


            if leave_type == 'LOP Leave':
                result = LOP_leave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                    
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)

            elif leave_type == "CH Leave":
                result = CH_leave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Casual Leave":
                result = casual_leave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Medical Leave":
                result = medicalLeave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Accumulation":
                result = earnLeave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Encashment":
                result = earnLeave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Vaccation Leave":
                result = vaccationLeave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Vaccation Earn Leave":
                result = vaccationLeave.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Special Onduty":
                result = specialOnduty.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Sevatical Special Onduty":
                result = specialOnduty.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            elif leave_type == "Onduty":
                result = onDuty.objects.filter(unique_id = unique_id)
                action = str(data.get('action'))
                if str(action) == 'Declined':
                    action = 'Declined(1)'
                elif str(action) == 'Approved':
                        action = 'Approved(1)'
                result.update(status=action)
            if action =='Declined(1)':
                print("JJJJJJJJJJJ")
                send_email(subject, body, to_email)
                staff_notify = StaffDetails.objects.get(username_copy = data.get('rowData[username]'))
                notification_message = f"Your {data.get('rowData[leave_type]')} request was Declined by HOD"
                staff_notify.notification_message = notification_message
                staff_notify.notification_display = True

                staff_notify.save()
            elif action == 'Approved(1)':
                staff_notify = StaffDetails.objects.get(username_copy = data.get('rowData[username]'))
                notification_message = f"Your {data.get('rowData[leave_type]')} request was Approved by HOD"
                staff_notify.notification_message = notification_message
                staff_notify.notification_display = True
                staff_notify.save()
            



        elif data.get('partial')  == 'no':   
            leave_type = data.get('rowData[leave_type]')
            unique_id = int(data.get('rowData[unique_id]'))
            username = data.get('rowData[username]')
            print(username)
            to_email = User.objects.get(username=username).email
            print(to_email)
            if leave_type == 'LOP Leave':
                result = LOP_leave.objects.filter(unique_id = unique_id)
                result.update(status=data.get('action'))

                username = data.get('rowData[username]')
                
                subject = "Leave Update"
                body = f"""

                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,
                    Vattamalaipalayam,
                    Coimbatore - 641022.
                """
                

                send_email(subject, body, to_email)



            elif leave_type == 'Special Onduty':
                result = specialOnduty.objects.filter(unique_id = unique_id)
                result.update(status=data.get('action'))

                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,  
                    Vattamalaipalayam,
                    Coimbatore - 641022.  
                """
                

                send_email(subject, body, to_email)

                print("Approved")

            elif leave_type == 'Sevatical Special Onduty':
                result = specialOnduty.objects.filter(unique_id = unique_id)
                result.update(status=data.get('action'))
                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,  
                    Vattamalaipalayam,
                    Coimbatore - 641022.  
                """
                

                send_email(subject, body, to_email)

                print("Approved")


            elif leave_type == 'Vaccation Leave':
                result = vaccationLeave.objects.filter(unique_id = unique_id)
                result.update(status=data.get('action'))
                reducing_remaining = Leave_Availability.objects.get(username = data.get('rowData[username]'))
                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    remaining = float(reducing_remaining.vaccation_remaining) - float(total_leave)
                    reducing_remaining.vaccation_remaining = remaining
                    reducing_remaining.save()



                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,  
                    Vattamalaipalayam,
                    Coimbatore - 641022.  
                """
                
                send_email(subject, body, to_email)

                print("Approved")

            elif leave_type == 'Vaccation Earn Leave':
                result = vaccationLeave.objects.filter(unique_id = unique_id)
                result.update(status=data.get('action'))

                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,  
                    Vattamalaipalayam,
                    Coimbatore - 641022.  
                """
                
                send_email(subject, body, to_email)

                print("Approved")
                
            elif leave_type == "CH Leave":
                result = CH_leave.objects.filter(unique_id = unique_id)

                result.update(status=data.get('action'))

                requesting_remaining = Leave_Availability.objects.get(username = data.get('rowData[username]'))

                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    remaining = float(requesting_remaining.ch_leave_remaining) - float(total_leave)
                    requesting_remaining.ch_leave_remaining = remaining
                    requesting_remaining.save()
                #     remaining = result1.ch_avail
                    # result1_queryset = result1.filter(username=username).order_by('ch_avail')
                    # least_remaining_result = result1_queryset.first()
                    # least_remaining_value = least_remaining_result.remaining
                    # result.update(remaining = float(remaining) - float(total_leave))
                    # filterered = login_details.objects.filter(username=username)
                    # filterered.update(ch_avail =( float(remaining) - float(total_leave)))

                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,
                    Sri Ramakrishna Engineering College,  
                    Vattamalaipalayam,
                    Coimbatore - 641022.  
                """
                

                send_email(subject, body, to_email)

            elif leave_type == "Casual Leave":

                result = casual_leave.objects.filter(unique_id = unique_id)
                username = data.get('rowData[username]')
                print('user',username)
                # result1 = casual_leave.objects.filter(username = username)
                reducing_remaining = Leave_Availability.objects.get(username = username)


                result.update(status=data.get('action'))

                # result1_queryset = result1.filter(username=username).order_by('remaining')
                # least_remaining_result = result1_queryset.first()
                # least_remaining_value = least_remaining_result.remaining
                # if least_remaining_value == 0:
                #     staff_detail = StaffDetails.objects.get(username_copy = username)
                #     least_remaining_value += float(staff_detail.casual_leave_avail)
                    
                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    remaining = float(reducing_remaining.casual_remaining) - float(total_leave)
                    reducing_remaining.casual_remaining = remaining
                    reducing_remaining.save()

                    # print('leasst',least_remaining_value )

                # remaining = least_remaining_value

                    subject = "Leave Update"
                    body = f"""

    Hello {data.get('rowData[username]')},

    We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

    Request Details:
    - Leave Type: {data.get('rowData[leave_type]')}
    - Applied Date: {data.get('rowData[date_Applied]')}
    - From Date: {data.get('rowData[from_Date]')}
    - To Date: {data.get('rowData[to_Date]')}
    - Reason: {data.get('rowData[reason]')}
    - Session: {data.get('rowData[session]')}
    - Remaining Leave: {remaining}
    - Total Leave: {data.get('rowData[total_leave]')}

    Status: {data.get('action')}

    If you have any questions or concerns, please feel free to contact us.

    Best regards,
        Administrative Office,  
        Sri Ramakrishna Engineering College,    
        Vattamalaipalayam,  
        Coimbatore - 641022.    
    """
                

                    send_email(subject, body, to_email)

            elif leave_type == "Onduty":

                result = onDuty.objects.filter(unique_id = unique_id)
                username = data.get('rowData[username]')
                print('user',username)
                result1 = onDuty.objects.filter(username = username)


                result.update(status=data.get('action'))

                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    result1_queryset = result1.filter(username=username).order_by('remaining')
                    least_remaining_result = result1_queryset.first()
                    least_remaining_value = least_remaining_result.remaining
                    result.update(remaining = float(least_remaining_value) - float(total_leave))

                    print('leasst',least_remaining_value )


                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {float(least_remaining_value) - float(total_leave)}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}    

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,  
                    Sri Ramakrishna Engineering College,    
                    Vattamalaipalayam,  
                    Coimbatore - 641022.    
                """
                


                send_email(subject, body, to_email)


            elif leave_type == "Medical Leave":

                result = medicalLeave.objects.filter(unique_id = unique_id)
                username = data.get('rowData[username]')
                print('user',username)
                result1 = medicalLeave.objects.filter(username = username)
                result.update(status=data.get('action'))
                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    result1_queryset = result1.filter(username=username).order_by('remaining')
                    least_remaining_result = result1_queryset.first()
                    least_remaining_value = least_remaining_result.remaining
                    result.update(remaining = float(least_remaining_value) - float(total_leave))

                    print('leasst',least_remaining_value )

                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {float(least_remaining_value) - float(total_leave)}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}    

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,  
                    Sri Ramakrishna Engineering College,    
                    Vattamalaipalayam,  
                    Coimbatore - 641022.    
                """
                



                send_email(subject, body, to_email)
            elif leave_type == "Accumulation":

                result = earnLeave.objects.filter(unique_id = unique_id)
                username = data.get('rowData[username]')
                print('user',username)
                result1 = Leave_Availability.objects.get(username = username)
                result.update(status=data.get('action'))
                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    remaining = float(result1.casual_remaining) - float(total_leave)
                    result1.casual_remaining = remaining
                    result1.save()

                    # print('leasst',least_remaining_value )

                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {float(least_remaining_value) - float(total_leave)}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}    

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,  
                    Sri Ramakrishna Engineering College,    
                    Vattamalaipalayam,  
                    Coimbatore - 641022.    
                """
                


                send_email(subject, body, to_email)

                    # data_list_of_dicts =[]
        
            elif leave_type == "Encashment":

                result = earnLeave.objects.filter(unique_id = unique_id)
                username = data.get('rowData[username]')
                print('user',username)
                result1 = Leave_Availability.objects.get(username = username)
                result.update(status=data.get('action'))
                if data.get('action') == "Approved":
                    total_leave = data.get('rowData[total_leave]')
                    # result1.earn_leave_remaining = float()
                    remaining = float(result1.casual_remaining) - float(total_leave)
                    result1.casual_remaining = remaining
                    result1.save()
                    
                    
                    # result.update(remaining = float(least_remaining_value) - float(total_leave))

                    # print('leasst',least_remaining_value )


                subject = "Leave Update"
                body = f"""
                Hello {data.get('rowData[username]')},

                We would like to inform you that your {data.get('rowData[leave_type]')} request, applied on {data.get('rowData[date_Applied]')}, has been {data.get('action')}.

                Request Details:
                - Leave Type: {data.get('rowData[leave_type]')}
                - Applied Date: {data.get('rowData[date_Applied]')}
                - From Date: {data.get('rowData[from_Date]')}
                - To Date: {data.get('rowData[to_Date]')}
                - Reason: {data.get('rowData[reason]')}
                - Session: {data.get('rowData[session]')}
                - Remaining Leave: {data.get('rowData[remaining]')}
                - Total Leave: {data.get('rowData[total_leave]')}

                Status: {data.get('action')}    

                If you have any questions or concerns, please feel free to contact us.

                Best regards,
                    Administrative Office,  
                    Sri Ramakrishna Engineering College,    
                    Vattamalaipalayam,  
                    Coimbatore - 641022.    
                """
                


                send_email(subject, body, to_email)

                    # data_list_of_dicts =[]
                

            staff_notify = StaffDetails.objects.get(username_copy = data.get('rowData[username]'))
            notification_message = f"Your {data.get('rowData[leave_type]')} request was {data.get('action')} by HR"
            staff_notify.notification_message = notification_message
            staff_notify.notification_display = True
            staff_notify.save()
        return HttpResponse("Success")

@login_required
def add_announcement(request, username, timestamp):
    if request.user.is_superuser:
        if request.method == "POST":
            announcement = request.POST.get("announcement")
            username = request.user.first_name
            timestamp = datetime.now()
            
            announcement_instance = Announcement(
                username = username,
                announcement = announcement,
                timestamp = timestamp
            )
            announcement_instance.save()
            return redirect('AdminPage')
        elif request.resolver_match.url_name == 'DeleteAnnouncement':
            announcement = get_object_or_404(Announcement, username=username, timestamp=timestamp)
            print(announcement)
            announcement.delete()
            print("deleted")
            return redirect('AdminPage')
        
@login_required
def dashboard(request):

    data_list_of_dicts = []
    print(request.user.username)
    result = casual_leave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if isinstance(item.date_Applied, (date, datetime)) else item.date_Applied,
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
        # print(data_list)
    result = LOP_leave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
        # print(data_list)
    result = CH_leave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date.isoformat(),
                    "to_Date": item.to_Date.isoformat() ,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
    result = medicalLeave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date.isoformat(),
                    "to_Date": item.to_Date.isoformat(),
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
    result = earnLeave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date,
                    "to_Date": item.to_Date,
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
    result = vaccationLeave.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date.isoformat(),
                    "to_Date": item.to_Date.isoformat(),
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
    result = specialOnduty.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date.isoformat(),
                    "to_Date": item.to_Date.isoformat(),
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
    result = onDuty.objects.filter(username=request.user.username)
    for item in result:
                data_dict = {
                    "unique_id": item.unique_id,
                    "username": item.username,
                    "leave_type": item.leave_type,
                    "date_Applied": item.date_Applied.isoformat() if item.date_Applied else None,
                    "from_Date": item.from_Date.isoformat(),
                    "to_Date": item.to_Date.isoformat(),
                    "session": item.session.upper(),
                    "remaining": item.remaining,
                    "total_leave": item.total_leave,
                    "status" : item.status
                }
                data_list_of_dicts.append(data_dict)
   
   
    staff_notification = StaffDetails.objects.get(username_copy = request.user.username)
    if staff_notification.notification_display:
        answer = True
        notification_message= staff_notification.notification_message
        staff_notification.notification_display = False
        staff_notification.save()
    else:
        answer = False
        notification_message = None
    

    context = {
        'username': request.user.first_name,
        'email': request.user.email,
        'notify':answer,
        'notification_message':notification_message,
        'data_dics':json.dumps(data_list_of_dicts),
        'bell_message' : StaffDetails.objects.get(username_copy = request.user.username).notification_message
    }
    
    

    print(data_list_of_dicts)
    return render(request,'datatables.html',context=context)


def card_dashboard(request):

    total_list=[]
    remaining_list=[]
    percentage_taken = []
    total_days = []
     
    #0.casual leave

    result = casual_leave.objects.filter(username = request.user.username)
    remaining = casual_total = float(Leave_Availability.objects.get(username = request.user.username).casual_remaining)
    if len((result))>0:
        casual_total = result.aggregate(Max('remaining'))['remaining__max']
    total_taken = casual_total-remaining
    taken = (total_taken /casual_total)*100
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(casual_total)

    
    #1. Vaccation leave

    result = vaccationLeave.objects.filter(username = request.user.username)
    remaining = vaccation_total = float(Leave_Availability.objects.get(username = request.user.username).vaccation_remaining)
    if len((result))>0:
        vaccation_total = result.aggregate(Max('remaining'))['remaining__max']
    # print(remaining)
    
    total_taken = vaccation_total-remaining
    taken = (total_taken/vaccation_total)* 100
    print(taken)
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(vaccation_total)

    #2. On duty

    result = onDuty.objects.filter(username = request.user.username)
    remaining = onduty_total = float(Leave_Availability.objects.get(username = request.user.username).onduty_remaining)
    if len((result))>0:
        onduty_total = result.aggregate(Max('remaining'))['remaining__max']
    # print(remaining)
    total_taken = onduty_total-remaining
    taken = (total_taken/onduty_total)* 100
    print(taken)
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(onduty_total)


    #3. Medical Leave

    result = medicalLeave.objects.filter(username = request.user.username)
    remaining = medical_total = float(Leave_Availability.objects.get(username = request.user.username).medical_leave_remaining)
    if len((result))>0:
        remaining = result.aggregate(Max('remaining'))['remaining__max']
    # print(remaining)
    total_taken = medical_total-remaining
    taken = (total_taken/medical_total)* 100
    print(taken)
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(medical_total)

    #4 ch avail

    result = CH_leave.objects.filter(username = request.user.username)
    remaining = ch_total = float(Leave_Availability.objects.get(username = request.user.username).ch_leave_remaining)
    if len((result))>0:
        remaining = result.aggregate(Max('remaining'))['remaining__max']
    # print(remaining)
    total_taken = ch_total-remaining
    if ch_total != 0:
        taken = (total_taken / ch_total) * 100
    else:
        taken = 0 
   
    print(taken)
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(ch_total)
    
    #5 earn leave
    
    result = earnLeave.objects.filter(username = request.user.username)
    remaining = earn_total = float(Leave_Availability.objects.get(username = request.user.username).earn_leave_remaining)
    if len((result))>0:
        remaining = result.aggregate(Max('remaining'))['remaining__max']
    # print(remaining)
    total_taken = float(earn_total)-float(remaining)
    taken = (total_taken/earn_total)* 100
    print(taken)
    percentage_taken.append(taken)
    total_list.append(total_taken)
    remaining_list.append(remaining)
    total_days.append(earn_total)

    staff_notification = StaffDetails.objects.get(username_copy = request.user.username)
    if staff_notification.notification_display:
        answer = True
        notification_message= staff_notification.notification_message
        staff_notification.notification_display = False
        staff_notification.save()
    else:
        answer = False
        notification_message = None
    

    context = {
        'username': request.user.first_name,
        'email': request.user.email,
        'notify':answer,
        'notification_message':notification_message,
        'bell_message' : StaffDetails.objects.get(username_copy = request.user.username).notification_message,
        'total':total_list,
        'remaining':remaining_list,
        'percentage':percentage_taken,
        'total_days' :total_days,
    }



    
    return render(request,'card_dashboard.html',context=context)


@login_required
def announcement_view(request):
    new_announcement = Announcement.objects.all().order_by('-timestamp')
    staff_notification = StaffDetails.objects.get(username_copy = request.user.username)
    if staff_notification.notification_display:
        answer = True
        notification_message= staff_notification.notification_message
        staff_notification.notification_display = False
        staff_notification.save()
    else:
        answer = False
        notification_message = None
    

    context = {
        'username': request.user.first_name,
        'email': request.user.email,
        'notify':answer,
        'notification_message':notification_message,
        'bell_message' : StaffDetails.objects.get(username_copy = request.user.username).notification_message,
        'announcements':new_announcement,
    }
    return render(request,'announcement.html',context)


@login_required
def download_individual(request, leave_type):
    if leave_type == 'All':
        leaves = []
        for model in [casual_leave, LOP_leave, CH_leave, medicalLeave, earnLeave, vaccationLeave, specialOnduty, onDuty]:
            leaves.extend(model.objects.filter(username=request.user.username))
    else:
        model_dict = {
            'Casual Leave': casual_leave,
            'LOP Leave': LOP_leave,
            'CH Leave': CH_leave,
            'Medical Leave': medicalLeave,
            'Earn Leave': earnLeave,
            'Vacation Leave': vaccationLeave,
            'Onduty': onDuty,
            'Special Onduty': specialOnduty,
        }
        leaves = model_dict[leave_type].objects.filter(username=request.user.username)

    # Create a DataFrame from the queryset
    data = []
    for leave in leaves:
        data.append([
            leave.username, leave.leave_type, make_naive(leave.date_Applied), leave.from_Date,
            leave.to_Date, leave.session, leave.remaining, leave.total_leave,
            leave.status, leave.reason
        ])
    df = pd.DataFrame(data, columns=['Username', 'Leave Type', 'Date Applied', 'From Date', 'To Date', 'Session', 'Remaining', 'Total Leave', 'Status', 'Reason'])

    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    # Send the response with the Excel file
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={request.user.username}_leaves.xlsx'
    return response


def account_settings(request):
    staff_notification = StaffDetails.objects.get(username_copy = request.user.username)
    if staff_notification.notification_display:
        answer = True
        notification_message= staff_notification.notification_message
        staff_notification.notification_display = False
        staff_notification.save()
    else:
        answer = False
        notification_message = None
    

    context = {
        'username': request.user.first_name,
        'email': request.user.email,
        'notify':answer,
        'notification_message':notification_message,
        'bell_message' : StaffDetails.objects.get(username_copy = request.user.username).notification_message,
    }
    return render(request,'account_settings.html',context)


@csrf_exempt
# @login_required
def get_otp(request):
    if request.method == "POST":
        print("POST request received")
        print("Request body:", request.POST)
        email = request.POST.get("email")
        print(f"Email: {email}")

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
            print("User found")
        except User.DoesNotExist:
            messages.error(request, 'User does not exist. Please log in or sign up.')
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        
        user_name = user.username

        otp = random.randint(100000, 999999)
        subject = "OTP"
        body = f"Your otp to update password is {otp}"
        send_email(subject, body, email)
        otp_save = StaffDetails.objects.get(username_copy=user_name)
        otp_save.otp = otp
        otp_save.save()

        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        email = request.POST.get("email")
        print(request)
        print(email)
        user = User.objects.get(email=email)
        user_name = user.username
        user_details = StaffDetails.objects.get(username_copy=user_name)
        
        if str(user_details.otp) == otp_input:
            return JsonResponse({'status': 'success', 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt

def update_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")
        user = User.objects.get(email=email)  # Retrieve the User object

        if new_password == confirm_password:
            # Set the new password for the current user
            user.set_password(new_password)
            user.save()
            logout(request)
            
            return JsonResponse({'status': 'success', 'message': 'Password updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def update_email(request):
    if request.method == "POST":
        new_email = request.POST.get("email")
        user = request.user
        user.email = new_email
        user.save()
        messages.info(request,"Email updated successfully")
       
        if (user is not None) and ((user.is_active and user.is_staff and not user.is_superuser) or (user.is_superuser and user.is_staff and user.is_active)):

            return redirect("AdminAccount")
        else:
            return redirect("AccountSettings")
             




