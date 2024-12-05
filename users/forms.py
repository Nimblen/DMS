from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import RoleRequest, User

class CustomUserCreationForm(UserCreationForm):


    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')




class RoleRequestForm(forms.ModelForm):
    class Meta:
        model = RoleRequest
        fields = ['requested_role']
        labels = {
            'requested_role': 'Запрашиваемая роль',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(RoleRequestForm, self).__init__(*args, **kwargs)
        ROLE_CHOICES = [choice for choice in User.ROLE_CHOICES if choice[0] != self.user.role]
        self.fields['requested_role'].choices = ROLE_CHOICES