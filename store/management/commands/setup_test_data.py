# store/management/commands/setup_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product

class Command(BaseCommand):
    help = 'Creates initial test data for the store'

    def handle(self, *args, **kwargs):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))

        # Create test categories
        categories = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Clothing', 'slug': 'clothing'},
        ]

        for cat in categories:
            Category.objects.get_or_create(
                name=cat['name'],
                slug=cat['slug']
            )
        
        # Create test products
        electronics = Category.objects.get(slug='electronics')
        Product.objects.get_or_create(
            name='Test Laptop',
            slug='test-laptop',
            category=electronics,
            description='A test laptop for development',
            price=999.99,
            stock=10,
            available=True,
            featured=True
        )

        self.stdout.write(self.style.SUCCESS('Test data created successfully'))
