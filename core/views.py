from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .decorators import student_required, teacher_required
from .models import Quiz, Question, Result, User
from .forms import StudentRegistrationForm, TeacherRegistrationForm, QuizForm, QuestionForm
import json

def home(request):
    return render(request, 'core/home.html')

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created successfully! You can now login.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/registration/student_register.html', {'form': form})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher account created successfully! You can now login.')
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'core/registration/teacher_register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_student:
        return redirect('student_dashboard')
    elif request.user.is_teacher:
        return redirect('teacher_dashboard')
    return redirect('home')

@login_required
@student_required
def student_dashboard(request):
    quizzes = Quiz.objects.all()
    results = Result.objects.filter(student=request.user)
    return render(request, 'core/student/dashboard.html', {
        'quizzes': quizzes,
        'results': results
    })

@login_required
@teacher_required
def teacher_dashboard(request):
    quizzes = Quiz.objects.filter(creator=request.user)
    return render(request, 'core/teacher/dashboard.html', {'quizzes': quizzes})

@login_required
@teacher_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'core/teacher/quiz_form.html', {'form': form})

@login_required
@teacher_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    return render(request, 'core/teacher/quiz_detail.html', {
        'quiz': quiz,
        'form': form
    })

@login_required
@teacher_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__creator=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('quiz_detail', quiz_id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'core/teacher/question_form.html', {'form': form, 'question': question})

@login_required
@student_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    # Check if student already took this quiz
    if Result.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, 'You have already taken this quiz.')
        return redirect('quiz_result', quiz_id=quiz.id)
    
    if request.method == 'POST':
        # Calculate score
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option == question.correct_answer:
                score += 1
        
        percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
        
        # Save result
        Result.objects.create(
            student=request.user,
            quiz=quiz,
            score=percentage_score
        )
        
        return redirect('quiz_result', quiz_id=quiz.id)
    
    return render(request, 'core/student/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
@student_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    result = get_object_or_404(Result, student=request.user, quiz=quiz)
    return render(request, 'core/student/quiz_result.html', {
        'quiz': quiz,
        'result': result
    })

@login_required
@student_required
def review_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    result = get_object_or_404(Result, student=request.user, quiz=quiz)
    
    # Get student's answers from the session or database
    # For simplicity, we'll just show all questions with correct answers
    questions = quiz.questions.all()
    
    return render(request, 'core/student/review_quiz.html', {
        'quiz': quiz,
        'result': result,
        'questions': questions
    })