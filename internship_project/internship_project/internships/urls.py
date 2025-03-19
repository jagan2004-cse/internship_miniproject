from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'internships'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search_internships/', views.search_internships, name='search_internships'),
    path('apply/<int:internship_id>/', views.apply_internship, name='apply_internship'),
    path('track/', views.track_applications, name='track_applications'),
    path('notifications/', views.notifications, name='notifications'),
    path('review/<int:internship_id>/', views.add_review, name='add_review'),
    path('contact/', views.contact_us, name='contact_us'),
    path('resume/', views.submit_resume, name='submit_resume'),
    path('assign-task/', views.assign_task, name='assign_task'),
    path('track-tasks/', views.track_tasks, name='track_tasks'),
    path('update-task-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='internships:login'), name='logout'),
]
