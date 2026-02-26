"""
Finance Tracker Views
=====================
Class-Based Views for all features. Every queryset is filtered by request.user.
"""
import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)
from django.conf import settings

from .forms import (
    UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm,
    CategoryForm, ExpenseForm, IncomeForm, ExpenseFilterForm, DateRangeFilterForm
)
from .models import Category, Expense, Income, UserProfile


# ─── Helper Functions ─────────────────────────────────────────────────────────

DEFAULT_CATEGORIES = [
    # Expense categories
    {'name': 'Food & Dining', 'category_type': 'expense', 'icon': 'bi-cup-hot', 'color': '#e74c3c'},
    {'name': 'Transportation', 'category_type': 'expense', 'icon': 'bi-car-front', 'color': '#3498db'},
    {'name': 'Shopping', 'category_type': 'expense', 'icon': 'bi-bag', 'color': '#9b59b6'},
    {'name': 'Entertainment', 'category_type': 'expense', 'icon': 'bi-controller', 'color': '#e67e22'},
    {'name': 'Healthcare', 'category_type': 'expense', 'icon': 'bi-heart-pulse', 'color': '#1abc9c'},
    {'name': 'Utilities', 'category_type': 'expense', 'icon': 'bi-lightning', 'color': '#f1c40f'},
    {'name': 'Housing', 'category_type': 'expense', 'icon': 'bi-house', 'color': '#e91e63'},
    {'name': 'Education', 'category_type': 'expense', 'icon': 'bi-book', 'color': '#00bcd4'},
    # Income categories
    {'name': 'Salary', 'category_type': 'income', 'icon': 'bi-cash-stack', 'color': '#27ae60'},
    {'name': 'Freelance', 'category_type': 'income', 'icon': 'bi-laptop', 'color': '#2980b9'},
    {'name': 'Investment', 'category_type': 'income', 'icon': 'bi-graph-up-arrow', 'color': '#8e44ad'},
    {'name': 'Other Income', 'category_type': 'income', 'icon': 'bi-plus-circle', 'color': '#16a085'},
]


def create_default_categories(user):
    """Create default categories for a new user."""
    for cat in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=user,
            name=cat['name'],
            defaults={**cat, 'is_default': True}
        )


def get_financial_summary(user, date_from=None, date_to=None):
    """Calculate total income, expenses, and balance for a user."""
    expenses_qs = Expense.objects.filter(user=user)
    income_qs = Income.objects.filter(user=user)

    if date_from:
        expenses_qs = expenses_qs.filter(date__gte=date_from)
        income_qs = income_qs.filter(date__gte=date_from)
    if date_to:
        expenses_qs = expenses_qs.filter(date__lte=date_to)
        income_qs = income_qs.filter(date__lte=date_to)

    total_expenses = expenses_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    balance = total_income - total_expenses

    return {
        'total_expenses': total_expenses,
        'total_income': total_income,
        'balance': balance,
        'expenses_qs': expenses_qs,
        'income_qs': income_qs,
    }


# ─── Public Views ─────────────────────────────────────────────────────────────

class LandingView(TemplateView):
    """Public landing page. Redirect authenticated users to dashboard."""
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


# ─── Auth Views ───────────────────────────────────────────────────────────────

class RegisterView(View):
    """User registration. Redirect if already logged in."""
    template_name = 'registration/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UserRegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile
            UserProfile.objects.create(user=user)
            # Create default categories
            create_default_categories(user)
            login(request, user)
            messages.success(request, f"Welcome aboard, {user.first_name or user.username}! 🎉 Your account is ready.")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """User login. Redirect if already logged in."""
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! 👋")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    """Logout and redirect to landing."""
    def post(self, request):
        logout(request)
        messages.info(request, "You've been logged out. See you soon!")
        return redirect('landing')


class ProfileView(LoginRequiredMixin, View):
    """View and update user profile."""
    template_name = 'expenses/profile.html'

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully! ✅")
            return redirect('profile')

        context = {'user_form': user_form, 'profile_form': profile_form}
        return render(request, self.template_name, context)


class ToggleDarkModeView(LoginRequiredMixin, View):
    """AJAX toggle dark mode."""
    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.dark_mode = not profile.dark_mode
        profile.save()
        return JsonResponse({'dark_mode': profile.dark_mode})


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    """Main dashboard with analytics and chart data."""
    template_name = 'expenses/dashboard.html'

    def get(self, request):
        filter_form = DateRangeFilterForm(request.GET or None)
        date_from = date_to = None

        if filter_form.is_valid():
            date_from = filter_form.cleaned_data.get('date_from')
            date_to = filter_form.cleaned_data.get('date_to')

        summary = get_financial_summary(request.user, date_from, date_to)

        # Recent transactions (last 5)
        recent_expenses = Expense.objects.filter(user=request.user).select_related('category')[:5]
        recent_income = Income.objects.filter(user=request.user).select_related('category')[:5]

        # Monthly expense summary (last 6 months)
        six_months_ago = date.today() - timedelta(days=180)
        monthly_expenses = (
            Expense.objects.filter(user=request.user, date__gte=six_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        monthly_income = (
            Income.objects.filter(user=request.user, date__gte=six_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Category breakdown for pie chart
        category_expenses = (
            summary['expenses_qs']
            .values('category__name', 'category__color')
            .annotate(total=Sum('amount'))
            .order_by('-total')[:8]
        )

        # Chart data serialization
        chart_labels = [item['month'].strftime('%b %Y') for item in monthly_expenses]
        chart_expense_data = [float(item['total']) for item in monthly_expenses]
        chart_income_data = []
        for label in chart_labels:
            match = next(
                (float(i['total']) for i in monthly_income if i['month'].strftime('%b %Y') == label),
                0
            )
            chart_income_data.append(match)

        pie_labels = [item['category__name'] or 'Uncategorized' for item in category_expenses]
        pie_data = [float(item['total']) for item in category_expenses]
        pie_colors = [item['category__color'] or '#6c757d' for item in category_expenses]

        context = {
            'filter_form': filter_form,
            'total_income': summary['total_income'],
            'total_expenses': summary['total_expenses'],
            'balance': summary['balance'],
            'recent_expenses': recent_expenses,
            'recent_income': recent_income,
            'chart_labels': json.dumps(chart_labels),
            'chart_expense_data': json.dumps(chart_expense_data),
            'chart_income_data': json.dumps(chart_income_data),
            'pie_labels': json.dumps(pie_labels),
            'pie_data': json.dumps(pie_data),
            'pie_colors': json.dumps(pie_colors),
            'date_from': date_from,
            'date_to': date_to,
        }
        return render(request, self.template_name, context)


# ─── Expense CRUD ─────────────────────────────────────────────────────────────

class ExpenseListView(LoginRequiredMixin, ListView):
    """Paginated expense list with search and filters."""
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = getattr(settings, 'EXPENSES_PER_PAGE', 10)

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user).select_related('category')
        form = ExpenseFilterForm(self.request.GET, user=self.request.user)

        if form.is_valid():
            if form.cleaned_data.get('search'):
                qs = qs.filter(
                    Q(title__icontains=form.cleaned_data['search']) |
                    Q(description__icontains=form.cleaned_data['search'])
                )
            if form.cleaned_data.get('category'):
                qs = qs.filter(category=form.cleaned_data['category'])
            if form.cleaned_data.get('date_from'):
                qs = qs.filter(date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                qs = qs.filter(date__lte=form.cleaned_data['date_to'])
            if form.cleaned_data.get('amount_min') is not None:
                qs = qs.filter(amount__gte=form.cleaned_data['amount_min'])
            if form.cleaned_data.get('amount_max') is not None:
                qs = qs.filter(amount__lte=form.cleaned_data['amount_max'])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ExpenseFilterForm(self.request.GET, user=self.request.user)
        context['total_filtered'] = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        return context


class ExpenseCreateView(LoginRequiredMixin, View):
    """Create a new expense."""
    template_name = 'expenses/expense_form.html'

    def get(self, request):
        form = ExpenseForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'title': 'Add Expense'})

    def post(self, request):
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' added successfully! 💸")
            return redirect('expense_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add Expense'})


class ExpenseUpdateView(LoginRequiredMixin, View):
    """Edit an existing expense (user-owned only)."""
    template_name = 'expenses/expense_form.html'

    def get_object(self, request, pk):
        return get_object_or_404(Expense, pk=pk, user=request.user)

    def get(self, request, pk):
        expense = self.get_object(request, pk)
        form = ExpenseForm(instance=expense, user=request.user)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Expense', 'object': expense})

    def post(self, request, pk):
        expense = self.get_object(request, pk)
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Expense updated successfully! ✅")
            return redirect('expense_list')
        return render(request, self.template_name, {'form': form, 'title': 'Edit Expense', 'object': expense})


class ExpenseDeleteView(LoginRequiredMixin, View):
    """Delete expense via AJAX or normal POST."""
    def post(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk, user=request.user)
        title = expense.title
        expense.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f"'{title}' deleted."})

        messages.success(request, f"Expense '{title}' deleted.")
        return redirect('expense_list')


# ─── Income CRUD ──────────────────────────────────────────────────────────────

class IncomeListView(LoginRequiredMixin, ListView):
    """Income list with pagination."""
    model = Income
    template_name = 'expenses/income_list.html'
    context_object_name = 'incomes'
    paginate_by = getattr(settings, 'EXPENSES_PER_PAGE', 10)

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_income'] = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        return context


class IncomeCreateView(LoginRequiredMixin, View):
    """Create a new income record."""
    template_name = 'expenses/income_form.html'

    def get(self, request):
        form = IncomeForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'title': 'Add Income'})

    def post(self, request):
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, f"Income '{income.title}' added! 💰")
            return redirect('income_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add Income'})


class IncomeUpdateView(LoginRequiredMixin, View):
    """Edit income record."""
    template_name = 'expenses/income_form.html'

    def get_object(self, request, pk):
        return get_object_or_404(Income, pk=pk, user=request.user)

    def get(self, request, pk):
        income = self.get_object(request, pk)
        form = IncomeForm(instance=income, user=request.user)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Income', 'object': income})

    def post(self, request, pk):
        income = self.get_object(request, pk)
        form = IncomeForm(request.POST, instance=income, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Income updated successfully! ✅")
            return redirect('income_list')
        return render(request, self.template_name, {'form': form, 'title': 'Edit Income', 'object': income})


class IncomeDeleteView(LoginRequiredMixin, View):
    """Delete income record."""
    def post(self, request, pk):
        income = get_object_or_404(Income, pk=pk, user=request.user)
        title = income.title
        income.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f"'{title}' deleted."})
        messages.success(request, f"Income '{title}' deleted.")
        return redirect('income_list')


# ─── Category CRUD ────────────────────────────────────────────────────────────

class CategoryListView(LoginRequiredMixin, ListView):
    """List all user categories."""
    model = Category
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, View):
    """Create a new category."""
    template_name = 'expenses/category_form.html'

    def get(self, request):
        form = CategoryForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add Category'})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f"Category '{category.name}' created! 🏷️")
            return redirect('category_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add Category'})


class CategoryUpdateView(LoginRequiredMixin, View):
    """Edit a category."""
    template_name = 'expenses/category_form.html'

    def get_object(self, request, pk):
        return get_object_or_404(Category, pk=pk, user=request.user)

    def get(self, request, pk):
        category = self.get_object(request, pk)
        form = CategoryForm(instance=category)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Category', 'object': category})

    def post(self, request, pk):
        category = self.get_object(request, pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated! ✅")
            return redirect('category_list')
        return render(request, self.template_name, {'form': form, 'title': 'Edit Category', 'object': category})


class CategoryDeleteView(LoginRequiredMixin, View):
    """Delete a category."""
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk, user=request.user)
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('category_list')


# ─── Export ───────────────────────────────────────────────────────────────────

class ExportExpensesCSVView(LoginRequiredMixin, View):
    """Export user expenses to CSV file."""
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Description', 'Created At'])

        expenses = Expense.objects.filter(user=request.user).select_related('category')
        for expense in expenses:
            writer.writerow([
                expense.title,
                expense.amount,
                expense.category.name if expense.category else '',
                expense.date,
                expense.description or '',
                expense.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response


class ExportIncomeCSVView(LoginRequiredMixin, View):
    """Export user income to CSV file."""
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="income.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Description', 'Created At'])

        incomes = Income.objects.filter(user=request.user).select_related('category')
        for income in incomes:
            writer.writerow([
                income.title,
                income.amount,
                income.category.name if income.category else '',
                income.date,
                income.description or '',
                income.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response


# ─── Error Handlers ───────────────────────────────────────────────────────────

def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
