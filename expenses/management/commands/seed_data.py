"""
Management command: seed_data
Creates a demo user with sample expenses and income for testing.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random
from expenses.models import Category, Expense, Income, UserProfile
from expenses.views import create_default_categories


class Command(BaseCommand):
    help = 'Seed database with sample data for testing'

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@financetracker.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('Demo@1234')
            user.save()
            UserProfile.objects.create(user=user)
            create_default_categories(user)
            self.stdout.write(self.style.SUCCESS('Demo user created: demo / Demo@1234'))
        else:
            self.stdout.write('Demo user already exists.')

        # Sample expenses
        categories = Category.objects.filter(user=user, category_type='expense')
        expense_data = [
            ('Grocery shopping', 85.50),
            ('Netflix subscription', 15.99),
            ('Uber ride', 22.00),
            ('Restaurant dinner', 67.80),
            ('Gym membership', 45.00),
            ('Electric bill', 120.00),
            ('Coffee & snacks', 18.50),
            ('Online course', 49.99),
            ('Medicine', 32.00),
            ('Books', 28.00),
        ]

        for i, (title, amount) in enumerate(expense_data):
            d = date.today() - timedelta(days=random.randint(0, 60))
            Expense.objects.get_or_create(
                user=user,
                title=title,
                defaults={
                    'amount': amount,
                    'category': categories[i % categories.count()] if categories.exists() else None,
                    'date': d,
                    'description': f'Sample expense: {title}',
                }
            )

        # Sample income
        income_categories = Category.objects.filter(user=user, category_type='income')
        income_data = [
            ('Monthly Salary', 3500.00),
            ('Freelance Project', 800.00),
            ('Investment Dividend', 150.00),
            ('Bonus', 500.00),
        ]
        for i, (title, amount) in enumerate(income_data):
            d = date.today() - timedelta(days=random.randint(0, 30))
            Income.objects.get_or_create(
                user=user,
                title=title,
                defaults={
                    'amount': amount,
                    'category': income_categories[i % income_categories.count()] if income_categories.exists() else None,
                    'date': d,
                    'description': f'Sample income: {title}',
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Sample data seeded successfully!'))
        self.stdout.write('Login with: demo / Demo@1234')
