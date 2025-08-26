# Alabi's Note: I have cleaned up and organized all your imports here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from .decorators import student_required, teacher_required
from .models import Quiz, Question, Result, Option, User
from .forms import (
    StudentRegistrationForm, 
    TeacherRegistrationForm, 
    QuizForm, 
    QuestionForm, 
    OptionFormSet
)


# --- General and Registration Views ---

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


# --- Teacher-Specific Views ---

@login_required
@teacher_required
def teacher_dashboard(request):
    quizzes_list = Quiz.objects.filter(teacher=request.user)
    quizzes_with_counts = quizzes_list.annotate(question_count=Count('questions'))

    stats = quizzes_with_counts.aggregate(
        total_quizzes=Count('id'),
        total_questions=Sum('question_count'),
        total_results=Count('results') 
    )

    paginator = Paginator(quizzes_with_counts, 10)
    page_number = request.GET.get('page')
    quizzes_page = paginator.get_page(page_number)

    context = {
        'quizzes': quizzes_page,
        'total_quizzes': stats.get('total_quizzes', 0),
        'total_questions': stats.get('total_questions', 0),
        'total_results': stats.get('total_results', 0),
    }
    return render(request, 'core/teacher/dashboard.html', context)


@login_required
@teacher_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user # Changed from creator to teacher for consistency
            quiz.save()
            messages.success(request, 'Quiz created successfully! Now add some questions.')
            # Redirect to the new "add question" page for the first question
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'core/teacher/create_quiz.html', {'form': form})


# Alabi's Note: Here is the NEW view, placed logically with other quiz management views.
@login_required
@teacher_required
def add_question_to_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, teacher=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = OptionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            formset.instance = question
            formset.save()

            messages.success(request, f'Successfully added question to "{quiz.title}"!')
            # For now, let's redirect back to the teacher's main dashboard.
            return redirect('teacher_dashboard') 
    else:
        form = QuestionForm()
        formset = OptionFormSet()

    context = {
        'form': form,
        'formset': formset,
        'quiz': quiz
    }
    return render(request, 'core/add_question.html', context)


# --- Student-Specific Views ---

@login_required
@student_required
def student_dashboard(request):
    quizzes = Quiz.objects.all() # Consider filtering for only 'active' quizzes
    # Get results for quizzes the student has already taken
    taken_quiz_ids = Result.objects.filter(student=request.user).values_list('quiz_id', flat=True)
    return render(request, 'core/student/dashboard.html', {
        'quizzes': quizzes,
        'taken_quiz_ids': taken_quiz_ids
    })

@login_required
@student_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('options') # More efficient
    
    if Result.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, 'You have already completed this quiz.')
        # Assuming you have a result detail page
        result = Result.objects.get(student=request.user, quiz=quiz)
        return redirect('quiz_result', result_id=result.id)
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                try:
                    # Alabi's Note: CRITICAL FIX HERE!
                    # We now check the selected option's 'is_correct' field.
                    selected_option = Option.objects.get(id=selected_option_id)
                    if selected_option.is_correct:
                        score += 1
                except Option.DoesNotExist:
                    # Handle case where a user submits an invalid option ID
                    pass
        
        percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
        
        result = Result.objects.create(
            student=request.user,
            quiz=quiz,
            score=percentage_score
        )
        
        return redirect('quiz_result', result_id=result.id)
    
    return render(request, 'core/student/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
@student_required
def quiz_result(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    quiz = result.quiz
    score = result.score
    
    if score >= 70:
        performance = {"status": "success", "message": "Excellent Performance!", "color_hex": "#4CAF50"}
    elif score >= 50:
        performance = {"status": "warning", "message": "Good Attempt!", "color_hex": "#FFC107"}
    else:
        performance = {"status": "danger", "message": "Needs Improvement", "color_hex": "#F44336"}

    context = {
        'quiz': quiz,
        'result': result,
        'performance': performance
    }
    # Alabi's Note: Corrected the template path
    return render(request, 'core/student/quiz_result.html', context)