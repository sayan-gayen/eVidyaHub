from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for students and teachers"""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Exam(models.Model):
    """Exam model created by teachers"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    total_marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Exam"
        verbose_name_plural = "Exams"


class Question(models.Model):
    """Questions for each exam"""
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='mcq')
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200, blank=True)
    option_d = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(max_length=1, help_text="Enter A, B, C, or D")
    marks = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.exam.title} - Question {self.id}"
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class ExamAttempt(models.Model):
    """Student exam attempts"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"
    
    def get_percentage(self):
        if self.score is not None and self.exam.total_marks > 0:
            return round((self.score / self.exam.total_marks) * 100, 2)
        return 0
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['student', 'exam']
        verbose_name = "Exam Attempt"
        verbose_name_plural = "Exam Attempts"


class Answer(models.Model):
    """Student answers for each question"""
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.attempt.student.username} - Question {self.question.id}"
    
    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
