from django.shortcuts import render, redirect
import os
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ResumeSubmission
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Internship, Application, Notification,Review
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReviewForm
from django.core.mail import send_mail
from .forms import ReviewForm, ContactForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import CustomUserCreationForm
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .models import Internship

def search_internships(request):
    internships = Internship.objects.all()  # Example query; adjust based on your logic
    if 'q' in request.GET:
        query = request.GET['q']
        internships = internships.filter(title__icontains=query)  # Example filtering
    return render(request, 'internships/search.html', {'internships': internships})

# Custom form for registration with email
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomLoginView(LoginView):
    template_name = 'internships/login.html'  # Use a custom template path
    redirect_authenticated_user = True  # Redirect if already logged in

    def get_success_url(self):
        return '/internships/search_internships/'  # Redirect to search page after login

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('internships:search_internships')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'internships/register.html', {'form': form})

def index(request):
    return render(request, 'internships/index.html')


#def register(request):
    #if request.method == "POST":
       # username = request.POST['username']
        #password = request.POST['password']
        #if User.objects.filter(username=username).exists():
           # messages.error(request, "Username already exists!")
            #return render(request, 'internships/register.html')
        #user = User.objects.create_user(username=username, password=password)
        ##login(request, user)
        #messages.success(request, "Registration successful!")
        #return redirect('internships:dashboard')
   # return render(request, 'internships/register.html')
@login_required
def add_review(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.internship = internship
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('internships:search_internships')
    else:
        form = ReviewForm()
    return render(request, 'internships/add_review.html', {'form': form, 'internship': internship})
@login_required
def dashboard(request):
    return render(request, 'internships/dashboard.html')

@login_required
def search_internships(request):
    query = request.POST.get('query', '')
    if query:
        internships = Internship.objects.filter(title__icontains=query) | Internship.objects.filter(company__icontains=query)
    else:
        internships = Internship.objects.all()
    # Add reviews to each internship for display
    for internship in internships:
        internship.reviews = Review.objects.filter(internship=internship)
    return render(request, 'internships/search.html', {'internships': internships})
@login_required
def apply_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    
    # Check if the user has already applied
    if Application.objects.filter(user=request.user, internship=internship).exists():
        messages.error(request, "You have already applied for this internship.")
        return redirect('internships:track_applications')
    
    if request.method == 'POST':
        resume = request.FILES.get('resume')  # Get the uploaded resume file
        if not resume:
            messages.error(request, "Please upload your resume.")
            return redirect('internships:apply_internship', internship_id=internship.id)
        
        # Create the application
        application = Application.objects.create(
            user=request.user,
            internship=internship,
            resume=resume
        )
        messages.success(request, "Application submitted successfully!")
        return redirect('internships:track_applications')
    
    return render(request, 'internships/apply.html', {'internship': internship})
@login_required
def track_applications(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'internships/track.html', {'applications': applications})
@login_required
def submit_resume(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if resume_file:
            resume_submission = ResumeSubmission(user=request.user, resume=resume_file)
            resume_submission.save()

            # Send resume to admin via Gmail
            admin_email = 'admin@example.com'  # Replace with actual admin email
            email = EmailMessage(
                subject=f"New Resume Submission from {request.user.username}",
                body=f"Resume submitted by {request.user.username} (Email: {request.user.email})\nView it at: {settings.MEDIA_URL}{resume_submission.resume.url}",
                from_email=settings.EMAIL_HOST_USER,
                to=[admin_email],
                attachments=[(resume_file.name, resume_file.read(), 'application/pdf')],  # Adjust MIME type if needed
            )
            email.send()

            # Send notification to user
            user_email = EmailMessage(
                subject="Resume Submission Confirmation",
                body=f"Dear {request.user.username},\nYour resume has been successfully submitted to the admin. We will review it soon.\nThank you!",
                from_email=settings.EMAIL_HOST_USER,
                to=[request.user.email],
            )
            user_email.send()

            messages.success(request, "Resume submitted successfully! You will be notified via email.")
            return redirect('internships:submit_resume')
        else:
            messages.error(request, "Please upload a resume file.")
    return render(request, 'internships/submit_resume.html')
@login_required
def assign_task(request):
    if not request.user.is_superuser:  # Restrict to admins (adjust as needed)
        raise PermissionDenied("You do not have permission to assign tasks.")
    
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        assigned_to = get_object_or_404(User, id=request.POST['assigned_to'])
        deadline = timezone.datetime.strptime(request.POST['deadline'], '%Y-%m-%dT%H:%M')
        task = Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            created_by=request.user,
            deadline=deadline
        )
        messages.success(request, f"Task '{title}' assigned successfully!")
        return redirect('internships:track_tasks')
    users = User.objects.all()
    return render(request, 'internships/assign_task.html', {'users': users})

@login_required
def track_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user) if not request.user.is_superuser else Task.objects.all()
    return render(request, 'internships/track_tasks.html', {'tasks': tasks})
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.assigned_to != request.user and not request.user.is_superuser:
        raise PermissionDenied("You do not have permission to update this task.")
    
    # Get the choices for the status field
    status_choices = Task._meta.get_field('status').choices
    
    if request.method == 'POST':
        task.status = request.POST['status']
        task.save()
        messages.success(request, f"Task '{task.title}' status updated to {task.status}.")
        return redirect('internships:track_tasks')
    
    return render(request, 'internships/update_task_status.html', {
        'task': task,
        'status_choices': status_choices  # Pass choices to the template
    })
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    for notification in notifications:
        notification.is_read = True
        notification.save()
    return render(request, 'internships/notifications.html', {'notifications': notifications})
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            # Send email to admin
            send_mail(
                subject=f"Contact Us: {subject}",
                message=f"From: {name} ({email})\n\n{message}",
                from_email=email,
                recipient_list=['admin@example.com'],  # Replace with your admin email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('internships:contact_us')
    else:
        form = ContactForm()
    return render(request, 'internships/contact_us.html', {'form': form})