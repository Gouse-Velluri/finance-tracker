"""
Finance Tracker Models
======================
Models: UserProfile, Category, Expense, Income
All user-specific data is filtered by user FK for security.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile with picture and preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        default=None
    )
    currency = models.CharField(max_length=10, default='$')
    dark_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None


class Category(models.Model):
    """Expense/Income categories, user-specific."""
    CATEGORY_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    icon = models.CharField(max_length=50, default='bi-tag', help_text='Bootstrap icon class')
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'category_type']),
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Core expense model with full CRUD support."""
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        return f"{self.title} - ${self.amount}"


class Income(models.Model):
    """Income model, mirrors expense structure."""
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes'
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.title} - ${self.amount}"
