from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_teacher': True})
    time_limit_minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    # Remove option_a, option_b, etc. from here
    rationale = models.TextField(blank=True, null=True) 
    
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text[:50]  # Return first 50 characters of question

class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}%"