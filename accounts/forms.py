from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    """Form for user registration."""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat Password'
    })) 

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
    
    #Placeholders are set for all the other fields ecxept password fields.
    #Loop through all fields in the form and assign the widget attribute class to all fields in register template.
    def __init__(self, *args, **kwargs):
        """Initialize the registration form."""
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        """Clean and validate form data."""
        #With 'super' we call the parent class's clean method.
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords didn't match"
            )
        

class UserForm(forms.ModelForm):
    """Form for user profile information."""
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    #Loop through all UserForm fields in the form and assign the widget attribute class to all fields in register template.
    def __init__(self, *args, **kwargs):
        """Initialize the user form."""
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    """Form for user profile details."""
    #Below variable is for not to show the path for the avatar image in the form in browser.
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid': ("Image files only")}, widget=forms.FileInput)
    
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    #Loop through all UserForm fields in the form and assign the widget attribute class to all fields in register template.
    def __init__(self, *args, **kwargs):
        """Initialize the user profile form."""
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'




