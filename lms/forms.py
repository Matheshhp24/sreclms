from django import forms
from django.contrib.auth.models import User
<<<<<<< HEAD
from .models import StaffDetails,StaffDepartment
=======
from .models import StaffDetails
>>>>>>> ffb26b97a2715c20203b6f4c56265c2c23fe644c
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Your Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Your Password'


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password('srec@123')  # Default password
        if commit:
            user.save()
        return user

class StaffDetailsForm(forms.ModelForm):
<<<<<<< HEAD
    department = forms.ChoiceField(choices=[])

=======
>>>>>>> ffb26b97a2715c20203b6f4c56265c2c23fe644c
    class Meta:
        model = StaffDetails
        fields = ['department', 'doj']
        widgets = {
            'doj': forms.SelectDateWidget(years=range(1980, 2030))
        }

<<<<<<< HEAD
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch departments from StaffDepartment instance
        try:
            staff_department_instance = StaffDepartment.objects.first()
            departments = staff_department_instance.departments if staff_department_instance else []
            self.fields['department'].choices = [(dept, dept) for dept in departments]
        except StaffDepartment.DoesNotExist:
            self.fields['department'].choices = []

=======
>>>>>>> ffb26b97a2715c20203b6f4c56265c2c23fe644c
class LeaveDownloadForm(forms.Form):
    leave_type = forms.ChoiceField(choices=[
        ('All', 'All'),
        ('Casual Leave', 'Casual Leave'),
        ('LOP Leave', 'LOP Leave'),
        ('CH Leave', 'Compensated Holiday'),
        ('Earn Leave', 'Earn Leave'),
        ('Medical Leave', 'Medical Leave'),
        ('Onduty', 'Onduty'),
        ('Special Onduty', 'Special Onduty'),
        ('Vacation Leave', 'Vacation Leave'),
    ])

