from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
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
def teacher_dashboard(request):
    # First, get the quizzes for ONLY the logged-in teacher.
    # This prevents data leaks.
    quizzes_list = Quiz.objects.filter(teacher=request.user)

    # --- This is where the magic happens ---
    # We use annotations to solve the N+1 query problem.
    # This single, efficient query gets each quiz AND its question count.
    quizzes_with_counts = quizzes_list.annotate(question_count=Count('questions'))

    # Now, we do all calculations on the server in one go.
    # We use the already-fetched queryset to avoid more DB hits.
    stats = quizzes_with_counts.aggregate(
        total_quizzes=Count('id'),
        total_questions=Sum('question_count'),
        # Assuming you have a Result model linked to Quiz
        total_results=Count('results') 
    )

    # --- Add Pagination ---
    paginator = Paginator(quizzes_with_counts, 10) # Show 10 quizzes per page
    page_number = request.GET.get('page')
    quizzes_page = paginator.get_page(page_number)

    context = {
        'quizzes': quizzes_page,  # Pass the paginated page object
        'total_quizzes': stats.get('total_quizzes', 0),
        'total_questions': stats.get('total_questions', 0),
        'total_results': stats.get('total_results', 0),
    }
    
    return render(request, 'teacher/dashboard.html', context)
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
# Assuming you have a view that renders this template
def quiz_result(request, quiz_id, result_id):
    # ... (your existing code to get quiz and result objects) ...
    result = Result.objects.get(id=result_id)
    quiz = Quiz.objects.get(id=quiz_id)

    score = result.score
    
    # --- The new logic belongs here, in the view ---
    if score >= 70:
        performance = {
            "status": "success",
            "message": "Excellent Performance!",
            "color_hex": "#4CAF50"
        }
    elif score >= 50:
        performance = {
            "status": "warning",
            "message": "Good Attempt!",
            "color_hex": "#FFC107"
        }
    else:
        performance = {
            "status": "danger",
            "message": "Needs Improvement",
            "color_hex": "#F44336"
        }

    context = {
        'quiz': quiz,
        'result': result,
        'performance': performance # Pass the whole dictionary to the template
    }
    
    return render(request, 'templates/core/student/quiz_result.html', context)

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