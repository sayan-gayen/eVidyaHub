from django.contrib import admin
from .models import UserProfile, Exam, Question, ExamAttempt, Answer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'duration', 'total_marks', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'teacher']
    search_fields = ['title', 'description', 'teacher__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['get_question_preview', 'exam', 'question_type', 'marks', 'correct_answer']
    list_filter = ['question_type', 'marks', 'exam']
    search_fields = ['question_text', 'exam__title']
    
    def get_question_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    get_question_preview.short_description = 'Question'


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'score', 'get_percentage', 'is_graded', 'started_at', 'completed_at']
    list_filter = ['is_graded', 'started_at', 'exam']
    search_fields = ['student__username', 'exam__title']
    date_hierarchy = 'started_at'
    readonly_fields = ['started_at', 'completed_at']
    
    def get_percentage(self, obj):
        return f"{obj.get_percentage()}%"
    get_percentage.short_description = 'Percentage'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_answer', 'is_correct']
    list_filter = ['is_correct', 'selected_answer']
    search_fields = ['attempt__student__username', 'question__question_text']
