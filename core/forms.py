from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Quiz, Question

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        return user

class TeacherRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'time_limit_minutes']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        # These are the ONLY fields that actually exist on the Question model now.
        fields = ['text', 'rationale']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'rationale': forms.Textarea(attrs={'rows': 2}),
        }