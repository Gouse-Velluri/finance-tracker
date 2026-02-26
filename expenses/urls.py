"""
Finance Tracker URL Configuration for expenses app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ─── Public ───────────────────────────────────────────────────────────────
    path('', views.LandingView.as_view(), name='landing'),

    # ─── Auth ─────────────────────────────────────────────────────────────────
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('toggle-dark-mode/', views.ToggleDarkModeView.as_view(), name='toggle_dark_mode'),

    # ─── Dashboard ────────────────────────────────────────────────────────────
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ─── Expenses ─────────────────────────────────────────────────────────────
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('expenses/export/', views.ExportExpensesCSVView.as_view(), name='export_expenses'),

    # ─── Income ───────────────────────────────────────────────────────────────
    path('income/', views.IncomeListView.as_view(), name='income_list'),
    path('income/add/', views.IncomeCreateView.as_view(), name='income_create'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_update'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    path('income/export/', views.ExportIncomeCSVView.as_view(), name='export_income'),

    # ─── Categories ───────────────────────────────────────────────────────────
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
