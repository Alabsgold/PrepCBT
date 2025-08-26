from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import Quiz, Question, Option, User

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
        fields = ['text', 'rationale']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'rationale': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }

# This is the magic!
# It creates a factory that can generate a set of Option forms
# for a given Question.
OptionFormSet = inlineformset_factory(
    Question,              # The parent model
    Option,                # The child model
    form=OptionForm,       # The form to use for each child
    extra=4,               # Always show 4 option forms
    max_num=4,             # Do not allow more than 4 options
    can_delete=False       # We don't need to delete options from this page
)