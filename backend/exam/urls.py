from django.urls import path
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:attempt_id>/submit/', views.submit_exam, name='submit_exam'),
    path('student/results/', views.student_results, name='student_results'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create-exam/', views.create_exam, name='create_exam'),
    path('teacher/exam/<int:exam_id>/add-question/', views.add_question, name='add_question'),
    path('teacher/exam/<int:exam_id>/view/', views.view_exam, name='view_exam'),
    path('teacher/exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('teacher/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('teacher/attempts/', views.view_attempts, name='view_attempts'),
    path('teacher/attempt/<int:attempt_id>/grade/', views.grade_attempt, name='grade_attempt'),
]
