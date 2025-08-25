from django.urls import path
from . import views

urlpatterns = [
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    path('teacher/quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('teacher/question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('student/quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('student/quiz/<int:quiz_id>/review/', views.review_quiz, name='review_quiz'),
]