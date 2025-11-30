from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import PollModel, VoteRecord, Category, PollAnalytics
from .forms import PollForm, CategoryForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import json

@login_required
def home(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'newest')
    
    # Base queryset
    polls = PollModel.objects.filter(status='active')
    
    # Apply filters
    if search_query:
        polls = polls.filter(
            Q(question__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        polls = polls.filter(category_id=category_filter)
    
    # Apply sorting
    if sort_by == 'popular':
        polls = polls.annotate(total_votes_count=Count('voterecord')).order_by('-total_votes_count')
    elif sort_by == 'oldest':
        polls = polls.order_by('created_at')
    else:  # newest
        polls = polls.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(polls, 6)
    page_number = request.GET.get('page')
    polls_page = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'polls': polls_page,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }
    return render(request, "home.html", context)

def ulogin(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("un")
        password = request.POST.get("pw")
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "ulogin.html")

def usignup(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("un")
        password = request.POST.get("pw")
        confirm_password = request.POST.get("cpw")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        else:
            try:
                user = User.objects.get(username=username)
                messages.error(request, f"Username '{username}' already exists.")
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, password=password)
                messages.success(request, "Account created successfully! Please log in.")
                return redirect("ulogin")
    
    return render(request, "usignup.html")

def ulogout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("ulogin")

@login_required
def view(request, poll_id):
    poll = get_object_or_404(PollModel, id=poll_id)
    
    # Check if poll is active
    if not poll.is_active:
        messages.warning(request, "This poll is no longer active.")
        return redirect("home")
    
    # Track poll view
    analytics, created = PollAnalytics.objects.get_or_create(poll=poll)
    analytics.views_count += 1
    analytics.save()
    
    # Check if user already voted
    try:
        vote_record = VoteRecord.objects.get(user=request.user, poll=poll)
        messages.info(request, "You have already voted on this poll.")
        return render(request, "view.html", {"poll": poll, "has_voted": True, "user_choice": vote_record.choice})
    except VoteRecord.DoesNotExist:
        pass
    
    if request.method == "POST":
        choice = request.POST.get("choice")
        if choice in ['op1', 'op2', 'op3']:
            # Update vote counts
            if choice == "op1":
                poll.op1c += 1
            elif choice == "op2":
                poll.op2c += 1
            else:
                poll.op3c += 1
            
            poll.save()
            
            # Create vote record
            VoteRecord.objects.create(
                user=request.user,
                poll=poll,
                choice=choice,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Update analytics
            analytics.unique_voters += 1
            analytics.save()
            
            messages.success(request, "Your vote has been recorded!")
            return redirect("result", poll_id=poll.id)
        else:
            messages.error(request, "Please select a valid option.")
    
    return render(request, "view.html", {"poll": poll, "has_voted": False})

@login_required
def result(request, poll_id):
    poll = get_object_or_404(PollModel, id=poll_id)
    
    # Prepare data for charts
    chart_data = {
        'labels': [poll.op1, poll.op2, poll.op3],
        'data': [poll.op1c, poll.op2c, poll.op3c],
        'total': poll.total_votes
    }
    
    # Calculate percentages
    percentages = []
    if poll.total_votes > 0:
        percentages = [
            round((poll.op1c / poll.total_votes) * 100, 1),
            round((poll.op2c / poll.total_votes) * 100, 1),
            round((poll.op3c / poll.total_votes) * 100, 1)
        ]
    
    context = {
        'poll': poll,
        'chart_data': json.dumps(chart_data),
        'percentages': percentages,
    }
    return render(request, "result.html", context)

@staff_member_required
def create(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user
            poll.save()
            
            # Create analytics record
            PollAnalytics.objects.create(poll=poll)
            
            messages.success(request, "Poll created successfully!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PollForm()
    
    return render(request, "create.html", {"form": form})

@staff_member_required
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect("create")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()
    
    return render(request, "create_category.html", {"form": form})

@login_required
def dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect("home")
    
    # Get analytics data
    total_polls = PollModel.objects.count()
    active_polls = PollModel.objects.filter(status='active').count()
    total_votes = sum(poll.total_votes for poll in PollModel.objects.all())
    
    # Recent polls
    recent_polls = PollModel.objects.order_by('-created_at')[:5]
    
    # Most popular polls
    popular_polls = PollModel.objects.annotate(
        vote_count=Count('voterecord')
    ).order_by('-vote_count')[:5]
    
    context = {
        'total_polls': total_polls,
        'active_polls': active_polls,
        'total_votes': total_votes,
        'recent_polls': recent_polls,
        'popular_polls': popular_polls,
    }
    return render(request, "dashboard.html", context)

def vote_ajax(request, poll_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    poll = get_object_or_404(PollModel, id=poll_id)
    
    if not poll.is_active:
        return JsonResponse({'error': 'Poll is not active'}, status=400)
    
    try:
        VoteRecord.objects.get(user=request.user, poll=poll)
        return JsonResponse({'error': 'Already voted'}, status=400)
    except VoteRecord.DoesNotExist:
        pass
    
    if request.method == "POST":
        data = json.loads(request.body)
        choice = data.get('choice')
        
        if choice in ['op1', 'op2', 'op3']:
            # Update vote counts
            if choice == "op1":
                poll.op1c += 1
            elif choice == "op2":
                poll.op2c += 1
            else:
                poll.op3c += 1
            
            poll.save()
            
            # Create vote record
            VoteRecord.objects.create(
                user=request.user,
                poll=poll,
                choice=choice,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({
                'success': True,
                'op1c': poll.op1c,
                'op2c': poll.op2c,
                'op3c': poll.op3c,
                'total': poll.total_votes
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
































