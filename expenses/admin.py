from django.contrib import admin
from .models import Category, Expense, Income, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'dark_mode', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user', 'is_default', 'color']
    list_filter = ['category_type', 'is_default']
    search_fields = ['name', 'user__username']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'user']
    list_filter = ['category', 'date']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'user']
    list_filter = ['category', 'date']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'date'
