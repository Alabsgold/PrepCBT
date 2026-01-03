from rest_framework import viewsets, permissions
from .models import User, Subject, Quiz, Question, Result
from .serializers import (
    UserSerializer, SubjectSerializer, QuizSerializer,
    QuestionSerializer, ResultSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see themselves unless they are admin (optional logic)
        return User.objects.filter(id=self.request.user.id)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['subject', 'creator']

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['quiz', 'difficulty']

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Students see their own results, Teachers see results for their quizzes?
        # For now, let's restrict to own results + teacher access
        user = self.request.user
        if user.is_teacher:
            # Teachers might want to see all results or just their quizzes
            return Result.objects.all() 
        return Result.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
