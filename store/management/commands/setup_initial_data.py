from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Setup initial categories, products, and admin user'

    def handle(self, *args, **kwargs):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))

        # Add your category & product creation logic here
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Latest gadgets and electronic devices'
            },
            {
                'name': 'Clothing',
                'description': 'Fashionable clothing for all occasions'
            },
            {
                'name': 'Books',
                'description': 'Educational and entertainment books'
            },
            {
                'name': 'Home & Garden',
                'description': 'Everything for your home and garden'
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Sports equipment and fitness gear'
            },
            {
                'name': 'Beauty & Health',
                'description': 'Beauty products and health supplements'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Fetch categories
        electronics = Category.objects.get(name='Electronics')
        clothing = Category.objects.get(name='Clothing')
        books = Category.objects.get(name='Books')
        home = Category.objects.get(name='Home & Garden')
        sports = Category.objects.get(name='Sports & Fitness')
        beauty = Category.objects.get(name='Beauty & Health')

        # Product data
        products_data = [
            # add your product dicts here exactly as you have above...
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))
