from django import forms

from .models import ReviewRating


class ReviewForm(forms.ModelForm):
    """Form class for creating a review."""
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']