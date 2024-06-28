from django import forms
from django.contrib.auth.models import User
from .models import StaffDetails
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
    class Meta:
        model = StaffDetails
        fields = ['department', 'doj']
        widgets = {
            'doj': forms.SelectDateWidget(years=range(1980, 2030))
        }

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

