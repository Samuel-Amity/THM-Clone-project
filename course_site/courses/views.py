from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, CustomAuthenticationForm  
from .models import Course, Chapter

# Home view
def home(request):
    return render(request, 'courses/home.html')

# Coordinator check
def is_coordinator(user):
    return user.is_staff

# Create course (restricted to coordinators)
@login_required
@user_passes_test(is_coordinator)
def create_course(request):
    if request.method == 'POST':
        pass
    return render(request, 'courses/create_course.html')

# List of courses (restricted to logged-in users)
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

# Course detail view (restricted to logged-in users)
@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    chapters = course.chapters.all()

    # Handle form submission via AJAX
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        chapter_id = int(request.POST.get('chapter_id'))
        user_answer = request.POST.get('user_answer')
        chapter = get_object_or_404(Chapter, id=chapter_id)

        # Check if the answer is correct or not
        correct = user_answer.strip().lower() == chapter.answer.strip().lower()
        return JsonResponse({'correct': correct})

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'chapters': chapters,
    })

# Custom login
def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home after login
            else:
                return render(request, 'courses/login.html', {'form': form, 'error': 'Invalid username or password.'})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'courses/login.html', {'form': form})

# Signup
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_login')  # Redirect to login after signup
    else:
        form = SignUpForm()
    return render(request, 'courses/signup.html', {'form': form})

# Custom logout
def custom_logout(request):
    logout(request)
    return redirect('custom_login')  # Redirect to login after logout


# chat -------------------------------------------------

from .models import Message
from .forms import MessageForm
from django.contrib.auth.models import User


def is_staff_user(user):
    return user.is_staff

# User chat view (for both staff and users)
@login_required
def user_chat(request):
    # Fetch all messages, regardless of the sender or receiver
    messages = Message.objects.all().order_by('timestamp')  

    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            # For simplicity, send to the first staff user if not specified
            message.receiver = User.objects.filter(is_staff=True).first()  
            message.save()
            return redirect('user_chat')

    return render(request, 'courses/user_chat.html', {'form': form, 'messages': messages})

# Staff chat view
@login_required
@user_passes_test(is_staff_user)
def staff_chat(request):
    messages = Message.objects.filter(receiver=request.user) | Message.objects.filter(sender=request.user)
    messages = messages.order_by('timestamp')
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = message.receiver  # Staff replies to the same user
            message.save()
            return redirect('staff_chat')

    return render(request, 'courses/staff_chat.html', {'form': form, 'messages': messages})


# pvt chat -----------------------------------------------
from .models import UserToStaffMessage
# Check if the user is staff
def is_staff_user(user):
    return user.is_staff

# User sends a message to staff
from django.contrib import messages as django_messages  # For error messaging
from django.db.models import Q

@login_required
def send_message_to_staff(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            # Send a new message to the first available staff user
            staff_user = User.objects.filter(is_staff=True).first()
            if not staff_user:
                return render(request, 'courses/send_message.html', {'error': 'No staff available.'})
            UserToStaffMessage.objects.create(
                sender=request.user,
                recipient=staff_user,
                message=message
            )
            return redirect('send_message_to_staff')

    # Fetch messages where the user is either sender or recipient
    messages = UserToStaffMessage.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')

    return render(request, 'courses/send_message.html', {'messages': messages})




# Staff views all user messages
@login_required
@user_passes_test(is_staff_user)
def view_messages(request):
    # Include all messages sent to any staff member
    messages = UserToStaffMessage.objects.filter(recipient__is_staff=True).order_by('-timestamp')
    return render(request, 'courses/view_messages.html', {'messages': messages})


# Staff replies to a specific message
@login_required
@user_passes_test(is_staff_user)
def reply_to_message(request, message_id):
    # Get the original message
    original_message = get_object_or_404(UserToStaffMessage, id=message_id, recipient=request.user)
    
    if request.method == 'POST':
        reply = request.POST.get('reply')
        if reply:
            # Create a reply and set the original sender as the recipient
            UserToStaffMessage.objects.create(
                sender=request.user,  # Staff user sending the reply
                recipient=original_message.sender,  # Reply to the original user
                message=reply
            )
            return redirect('view_messages')  # Redirect back to the staff's message view

    return render(request, 'courses/reply_message.html', {'original_message': original_message})
