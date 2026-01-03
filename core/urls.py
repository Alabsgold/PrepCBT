# in core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    UserViewSet, SubjectViewSet, QuizViewSet,
    QuestionViewSet, ResultViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'results', ResultViewSet)

# Alabi's Note: I've added comments to keep the sections organized.
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # --- Teacher URLs ---
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    path('teacher/quiz/generate-ai/', views.generate_quiz_ai, name='generate_quiz_ai'),
    
    # ALABI'S NOTE: Added the new URL for our formset page.
    path('teacher/quiz/<int:quiz_id>/add-question/', views.add_question_to_quiz, name='add_question'),
    path('teacher/search-quizzes/', views.search_quizzes, name='search_quizzes'),
    
    # ALABI'S NOTE: Corrected this URL to pass the result_id, which the view now requires.
    path('student/result/<int:result_id>/', views.quiz_result, name='quiz_result'),
    path('student/api/explain-ai/', views.get_explanation_ai, name='get_explanation_ai'),
]