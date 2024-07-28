from django.db import models
from django.contrib.auth.models import User

class StaffDepartment(models.Model):
    departments = models.JSONField(default=list)

    def add_department(self, department_name):
        # Avoid adding duplicates
        if department_name not in self.departments:
            self.departments.append(department_name)
            self.save()

    def __str__(self):
        return ", ".join(self.departments)
    
    
class StaffDetails(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username_copy = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    doj = models.DateField()  # Date of joining
    otp = models.IntegerField(default=0)
    casual_leave_avail = models.IntegerField(default=0)
    LOP_leave_avail = models.IntegerField(default=0)
    CH_leave_avail = models.IntegerField(default=0)
    medicalLeave_avail = models.IntegerField(default=0)
    earnLeave_avail = models.IntegerField(default=0)
    vaccationLeave_avail = models.IntegerField(default=0)
    specialOnduty_avail = models.IntegerField(default=0)
    onDutye_avail = models.IntegerField(default=0)
    notification_display  = models.BooleanField(default=False)
    notification_message = models.CharField(max_length=100,default='')
    is_principal = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.user} ----- {self.first_name} {self.last_name}"
    def save(self, *args, **kwargs):
        self.username_copy = self.user.username
        if self.department:
            self.department = self.department.upper()
        super().save(*args, **kwargs)

class default_table (models.Model):
    casual_leave_default = models.IntegerField(default=12)
    LOP_leave_default = models.IntegerField(default=0)
    CH_leave_default = models.IntegerField(default=0)
    medicalLeave_default = models.IntegerField(default=5)
    earnLeave_default = models.IntegerField(default=5)
    vaccationLeave_default = models.IntegerField(default=15)
    specialOnduty_default = models.IntegerField(default=0)
    onDuty_default = models.IntegerField(default=14)

class casual_leave(models.Model):
    username = models.CharField( max_length=50)
    
    leave_type = models.CharField(max_length = 50, default = "Casual Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.FloatField( max_length=50, default = 12.0)
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False )
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/')

    def __str__(self):
        return f"{self.username}"


class LOP_leave(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "LOP Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='documents/') 


class CH_leave(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "CH Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/')

class medicalLeave(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "Medical Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/') 


class earnLeave(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "Earn Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/') 

class vaccationLeave(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "Vaccation Leave")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/') 

class specialOnduty(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "Special Onduty")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/') 

class onDuty(models.Model):
    username = models.CharField( max_length=50)
    leave_type = models.CharField(max_length = 50, default = "Onduty")
    date_Applied = models.DateTimeField( max_length=50)
    from_Date = models.CharField( max_length=50)
    to_Date = models.CharField( max_length=50)
    session = models.CharField( max_length=50)
    remaining = models.CharField( max_length=50, default = "-")
    total_leave = models.FloatField(default = 0)
    status = models.CharField(max_length=50 ,default = 'Reviewing')
    unique_id = models.AutoField(primary_key=True, editable=False)
    reason = models.CharField(max_length = 200 , default = "-")
    document = models.FileField(upload_to='leave_documents/') 



class Leave_Availability(models.Model):
    username = models.CharField( max_length=50)
    casual_remaining = models.CharField(max_length = 50 , default = 0)
    initial_casual_remaining = models.CharField(max_length = 50 , default = 0)
    vaccation_remaining= models.CharField(max_length=50, default=0)
    initial_vaccation_remaining= models.CharField(max_length=50, default=0)
    onduty_remaining= models.CharField(max_length=50, default=0)
    initial_onduty_remaining= models.CharField(max_length=50, default=0)
    medical_leave_remaining= models.CharField(max_length=50, default=0)
    initial_medical_leave_remaining= models.CharField(max_length=50, default=0)
    earn_leave_remaining = models.CharField(max_length=50,default=0)
    initial_earn_leave_remaining = models.CharField(max_length=50,default=0)
    ch_leave_remaining = models.CharField(max_length=50,default=0)
    initial_ch_leave_remaining = models.CharField(max_length=50,default=0)
    def __str__(self):
        return f"{self.username}"



class Announcement(models.Model):
    username = models.CharField( max_length=50 )
    announcement = models.CharField(max_length=500)
    timestamp = models.DateTimeField( max_length=50)