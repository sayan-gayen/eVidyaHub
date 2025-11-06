from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from .models import UserProfile, Exam, Question, ExamAttempt, Answer


def home(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.user_type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('teacher_dashboard')
        except UserProfile.DoesNotExist:
            logout(request)
            messages.error(request, 'Profile not found! Please login again.')
            return redirect('login')
    return redirect('login')


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                profile = UserProfile.objects.get(user=user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                if profile.user_type == 'student':
                    return redirect('student_dashboard')
                else:
                    return redirect('teacher_dashboard')
            except UserProfile.DoesNotExist:
                logout(request)
                messages.error(request, 'Profile not found! Please contact admin.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'login.html')


def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        phone = request.POST.get('phone', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('signup')
        
        if not user_type or user_type not in ['student', 'teacher']:
            messages.error(request, 'Please select a valid user type!')
            return redirect('signup')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone=phone
            )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')
    
    return render(request, 'signup.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')


@login_required
def student_dashboard(request):
    """Student dashboard with available exams"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'student':
        return redirect('teacher_dashboard')
    
    # Get all active exams
    exams = Exam.objects.filter(is_active=True).prefetch_related('questions')
    
    # Get exams already attempted by student
    attempted_exams = ExamAttempt.objects.filter(student=request.user)
    attempted_exam_ids = attempted_exams.values_list('exam_id', flat=True)
    
    context = {
        'exams': exams,
        'attempted_exam_ids': list(attempted_exam_ids),
        'profile': profile
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def student_profile(request):
    """Student profile with growth tracking"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'student':
        return redirect('home')
    
    # Get all graded attempts
    attempts = ExamAttempt.objects.filter(
        student=request.user, 
        is_graded=True
    ).select_related('exam').order_by('-completed_at')
    
    # Calculate statistics
    total_exams = attempts.count()
    total_score = sum([attempt.score for attempt in attempts if attempt.score is not None])
    total_possible = sum([attempt.exam.total_marks for attempt in attempts])
    
    average_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
    
    context = {
        'profile': profile,
        'attempts': attempts,
        'total_exams': total_exams,
        'total_score': total_score,
        'total_possible': total_possible,
        'average_percentage': round(average_percentage, 2)
    }
    return render(request, 'student_profile.html', context)


@login_required
def take_exam(request, exam_id):
    """Take exam view"""
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'student':
        messages.error(request, 'Only students can take exams!')
        return redirect('home')
    
    # Check if already attempted
    if ExamAttempt.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, 'You have already attempted this exam!')
        return redirect('student_dashboard')
    
    # Check if exam has questions
    if not exam.questions.exists():
        messages.error(request, 'This exam has no questions yet!')
        return redirect('student_dashboard')
    
    # Create new attempt
    attempt = ExamAttempt.objects.create(
        student=request.user,
        exam=exam
    )
    
    questions = exam.questions.all()
    
    context = {
        'exam': exam,
        'questions': questions,
        'attempt': attempt
    }
    return render(request, 'take_exam.html', context)


@login_required
def submit_exam(request, attempt_id):
    """Submit exam and calculate score"""
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    
    if request.method == 'POST':
        questions = attempt.exam.questions.all()
        score = 0
        
        for question in questions:
            answer_key = f'question_{question.id}'
            selected_answer = request.POST.get(answer_key)
            
            if selected_answer:
                is_correct = (selected_answer.upper() == question.correct_answer.upper())
                
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer.upper(),
                    is_correct=is_correct
                )
                
                if is_correct:
                    score += question.marks
        
        # Update attempt with score
        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.is_graded = True
        attempt.save()
        
        messages.success(request, f'Exam submitted successfully! Your score: {score}/{attempt.exam.total_marks}')
        return redirect('student_results')
    
    return redirect('student_dashboard')


@login_required
def student_results(request):
    """View all student results"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'student':
        return redirect('home')
    
    attempts = ExamAttempt.objects.filter(
        student=request.user, 
        is_graded=True
    ).select_related('exam').order_by('-completed_at')
    
    context = {
        'attempts': attempts,
        'profile': profile
    }
    return render(request, 'student_results.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        return redirect('student_dashboard')
    
    # Get teacher's exams
    exams = Exam.objects.filter(teacher=request.user).prefetch_related('questions', 'attempts')
    
    # Calculate statistics
    total_students = ExamAttempt.objects.filter(exam__teacher=request.user).values('student').distinct().count()
    total_attempts = ExamAttempt.objects.filter(exam__teacher=request.user).count()
    
    context = {
        'exams': exams,
        'total_students': total_students,
        'total_attempts': total_attempts,
        'profile': profile
    }
    return render(request, 'teacher_dashboard.html', context)


@login_required
def create_exam(request):
    """Create new exam"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        messages.error(request, 'Only teachers can create exams!')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        total_marks = request.POST.get('total_marks')
        
        # Validation
        if not all([title, description, duration, total_marks]):
            messages.error(request, 'All fields are required!')
            return redirect('create_exam')
        
        try:
            exam = Exam.objects.create(
                teacher=request.user,
                title=title,
                description=description,
                duration=int(duration),
                total_marks=int(total_marks)
            )
            
            messages.success(request, 'Exam created successfully! Now add questions.')
            return redirect('add_question', exam_id=exam.id)
        except Exception as e:
            messages.error(request, f'Error creating exam: {str(e)}')
            return redirect('create_exam')
    
    return render(request, 'create_exam.html')


@login_required
def add_question(request, exam_id):
    """Add questions to exam"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c', '')
        option_d = request.POST.get('option_d', '')
        correct_answer = request.POST.get('correct_answer')
        marks = request.POST.get('marks')
        
        # Validation
        if not all([question_text, option_a, option_b, correct_answer, marks]):
            messages.error(request, 'Please fill all required fields!')
            return redirect('add_question', exam_id=exam.id)
        
        try:
            Question.objects.create(
                exam=exam,
                question_text=question_text,
                question_type=question_type,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer.upper(),
                marks=int(marks)
            )
            
            messages.success(request, 'Question added successfully!')
            
            if 'add_another' in request.POST:
                return redirect('add_question', exam_id=exam.id)
            else:
                return redirect('view_exam', exam_id=exam.id)
        except Exception as e:
            messages.error(request, f'Error adding question: {str(e)}')
            return redirect('add_question', exam_id=exam.id)
    
    questions = exam.questions.all()
    context = {
        'exam': exam,
        'questions': questions
    }
    return render(request, 'add_question.html', context)


@login_required
def view_exam(request, exam_id):
    """View exam details"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    questions = exam.questions.all()
    attempts = ExamAttempt.objects.filter(exam=exam).select_related('student').order_by('-started_at')
    
    context = {
        'exam': exam,
        'questions': questions,
        'attempts': attempts
    }
    return render(request, 'view_exam.html', context)


@login_required
def delete_exam(request, exam_id):
    """Delete exam"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    exam_title = exam.title
    exam.delete()
    messages.success(request, f'Exam "{exam_title}" deleted successfully!')
    return redirect('teacher_dashboard')


@login_required
def delete_question(request, question_id):
    """Delete question"""
    question = get_object_or_404(Question, id=question_id, exam__teacher=request.user)
    exam_id = question.exam.id
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('add_question', exam_id=exam_id)


@login_required
def view_attempts(request):
    """View all exam attempts"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        return redirect('home')
    
    attempts = ExamAttempt.objects.filter(
        exam__teacher=request.user
    ).select_related('student', 'exam').order_by('-started_at')
    
    context = {
        'attempts': attempts,
        'profile': profile
    }
    return render(request, 'view_attempts.html', context)


@login_required
def grade_attempt(request, attempt_id):
    """View student's attempt details"""
    attempt = get_object_or_404(
        ExamAttempt, 
        id=attempt_id, 
        exam__teacher=request.user
    )
    answers = Answer.objects.filter(attempt=attempt).select_related('question')
    
    context = {
        'attempt': attempt,
        'answers': answers
    }
    return render(request, 'grade_attempt.html', context)
