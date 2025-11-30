from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color code
    
    def __str__(self):
        return self.name

class PollModel(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    
    question = models.TextField(validators=[MinLengthValidator(10)])
    description = models.TextField(blank=True, help_text="Optional description for the poll")
    op1 = models.CharField(max_length=100)
    op2 = models.CharField(max_length=100)
    op3 = models.CharField(max_length=100)
    
    op1c = models.IntegerField(default=0)
    op2c = models.IntegerField(default=0)
    op3c = models.IntegerField(default=0)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_polls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_anonymous = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question
    
    @property
    def total_votes(self):
        return self.op1c + self.op2c + self.op3c
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_active(self):
        return self.status == 'active' and not self.is_expired

class VoteRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    poll = models.ForeignKey(PollModel, on_delete=models.CASCADE)
    choice = models.CharField(max_length=10)  # 'op1', 'op2', or 'op3'
    voted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ("user", "poll")
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} voted on {self.poll.question[:30]}"

class PollAnalytics(models.Model):
    poll = models.OneToOneField(PollModel, on_delete=models.CASCADE, related_name='analytics')
    views_count = models.IntegerField(default=0)
    unique_voters = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.poll.question[:30]}"