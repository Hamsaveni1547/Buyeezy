
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='store.category')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'unique_together': {('name', 'parent')},
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('available', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='store_produ_slug_e4adbf_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['available'], name='store_produ_availab_0c4d5d_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['featured'], name='store_produ_feature_408939_idx'),
        ),
    ]
