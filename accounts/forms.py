from django import forms
from captcha.fields import ReCaptchaField
from .models import EmailTemplates,User,UserEmail

class EmailTemplatesForm(forms.ModelForm):

    class Meta():
        model = EmailTemplates
        fields = ('subject','email',)


class UserForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('first_name','last_name','email')


class UserLoginForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('email','password',)

    captcha = ReCaptchaField()


class ReCaptchaForm(forms.Form):
    captcha = ReCaptchaField()

class UserEmailForm(forms.ModelForm):

    class Meta():
        model = UserEmail
        fields = ('title','email_body',)
