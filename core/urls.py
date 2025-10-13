# in core/urls.py

from django.urls import path
from . import views

# Alabi's Note: I've added comments to keep the sections organized.
urlpatterns = [
    
    # --- Teacher URLs ---
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    
    # ALABI'S NOTE: Added the new URL for our formset page.
    path('teacher/quiz/<int:quiz_id>/add-question/', views.add_question_to_quiz, name='add_question'),
    path('teacher/search-quizzes/', views.search_quizzes, name='search_quizzes'),
    
    # These teacher URLs below might need to be updated or removed now that we have the formset.
    # We can review them later.
    path('teacher/quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('teacher/question/<int:question_id>/edit/', views.edit_question, name='edit_question'),


    # --- Student URLs ---
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    
    # ALABI'S NOTE: Corrected this URL to pass the result_id, which the view now requires.
    path('student/result/<int:result_id>/', views.quiz_result, name='quiz_result'),

    path('student/quiz/<int:quiz_id>/review/', views.review_quiz, name='review_quiz'),
]