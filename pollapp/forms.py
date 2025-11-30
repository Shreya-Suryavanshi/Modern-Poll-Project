from django import forms
from .models import PollModel, Category
from django.utils import timezone

class PollForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Optional: When should this poll expire?"
    )
    
    class Meta:
        model = PollModel
        fields = ["question", "description", "op1", "op2", "op3", "category", "expires_at", "is_anonymous"]
        widgets = {
            "question": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Enter your poll question here...",
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Optional description for your poll...",
                "class": "form-control"
            }),
            "op1": forms.TextInput(attrs={
                "placeholder": "First option",
                "class": "form-control"
            }),
            "op2": forms.TextInput(attrs={
                "placeholder": "Second option", 
                "class": "form-control"
            }),
            "op3": forms.TextInput(attrs={
                "placeholder": "Third option",
                "class": "form-control"
            }),
            "category": forms.Select(attrs={"class": "form-control"}),
            "is_anonymous": forms.CheckboxInput(attrs={"class": "form-check-input"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category (optional)"
        
        # Set default expiration to 7 days from now
        if not self.instance.pk:  # Only for new polls
            default_expiry = timezone.now() + timezone.timedelta(days=7)
            self.fields['expires_at'].initial = default_expiry.strftime('%Y-%m-%dT%H:%M')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "color"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Category name",
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Category description...",
                "class": "form-control"
            }),
            "color": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color"
            })
        }