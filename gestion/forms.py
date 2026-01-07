from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('bibliotecario', 'Bibliotecario'),
            ('bodeguero', 'Bodeguero'), 
            ('admin', 'Admin'),
        ],
        label="Tipo de usuario"
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')
