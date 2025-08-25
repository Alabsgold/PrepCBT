from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/student/', core_views.student_register, name='student_register'),
    path('register/teacher/', core_views.teacher_register, name='teacher_register'),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('', include('core.urls')),
]