from django import forms
from .models import User

# creating a form for user registration by extending ModelForm
# we can create fields at form level also instead of model
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
    
    # when form is triggered , this clean is called which cleans the inputs and returns dictionary of cleaned data
    def clean(self):
        cleaned_data = super(UserForm, self).clean()   # to override clean method
        password= cleaned_data.get('password')
        confirm_password= cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password does not match")
