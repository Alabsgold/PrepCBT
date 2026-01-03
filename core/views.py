# Alabi's Note: I have cleaned up and organized all your imports here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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
    QuizForm, 
    QuestionForm, 
    OptionFormSet
)
from .ai_utils import generate_quiz_content, get_ai_explanation
from .models import Subject


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
    quizzes_list = Quiz.objects.filter(creator=request.user)
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
def generate_quiz_ai(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        subject_name = request.POST.get('subject') # Text input or select
        difficulty = request.POST.get('difficulty', 'medium')
        num_questions = int(request.POST.get('num_questions', 5))
        
        # Ensure subject exists or create it
        subject, created = Subject.objects.get_or_create(name=subject_name)
        
        # Call AI
        ai_data = generate_quiz_content(subject.name, topic, num_questions, difficulty)
        
        if ai_data:
            # Create Quiz
            quiz = Quiz.objects.create(
                title=f"AI Quiz: {topic} ({difficulty})",
                subject=subject,
                subject_text=subject.name,
                creator=request.user,
                time_limit_minutes=num_questions * 2 # 2 mins per question default
            )
            
            # Create Questions and Options
            for q_data in ai_data:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['text'],
                    difficulty=difficulty,
                    topic=topic,
                    rationale=q_data.get('rationale', '')
                )
                
                options = q_data['options'] # List of 4 strings
                correct_idx = q_data['correct_index']
                
                for i, opt_text in enumerate(options):
                    Option.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=(i == correct_idx)
                    )
            
            messages.success(request, f'Successfully generated quiz "{quiz.title}" with {len(ai_data)} questions!')
            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Failed to generate quiz. Please check your API key or try again.')
    
    return render(request, 'core/teacher/generate_quiz_ai.html')

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


@login_required
@teacher_required
def search_quizzes(request):
    search_text = request.GET.get('q', '').strip()

    quizzes_list = Quiz.objects.filter(
        creator=request.user,
        title__icontains=search_text
    ).annotate(question_count=Count('questions'))

    # We don't need the full stats here, just the quizzes
    context = {
        'quizzes': quizzes_list,
    }
    return render(request, 'core/teacher/partials/quiz_list_partial.html', context)


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
        'performance': performance,
        'questions': quiz.questions.prefetch_related('options') # Add questions to context
    }
    # Alabi's Note: Corrected the template path
    return render(request, 'core/student/quiz_result.html', context)

@login_required
def get_explanation_ai(request):
    if request.method == 'GET':
        question_id = request.GET.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        
        # Find correct option
        correct_option = question.options.filter(is_correct=True).first()
        correct_text = correct_option.text if correct_option else "Unknown"
        
        # Check if we already have a rationale (human wrote it or AI generated it previously)
        if question.rationale and len(question.rationale) > 10:
            return JsonResponse({'explanation': question.rationale, 'source': 'database'})
            
        # Call AI
        explanation = get_ai_explanation(question.text, correct_text)
        
        # Optionally save it to DB so we don't pay for it again!
        if explanation and "Could not" not in explanation:
            question.rationale = explanation
            question.save()
            
        return JsonResponse({'explanation': explanation, 'source': 'ai'})
    return JsonResponse({'error': 'Invalid request'}, status=400)