import os
import json
from pathlib import Path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Product

def init_database():
    print("--- Initializing database for Render / Production ---")

    # 1. Khoi tao / cap nhat cac tai khoan Quan tri vien
    admin_accounts = [
        {'username': 'admin', 'email': 'admin@kingvolleyball.com'},
        {'username': 'admin17', 'email': 'kai1703@gmail.com'},
    ]

    for acc in admin_accounts:
        user, created = User.objects.get_or_create(
            username=acc['username'],
            defaults={
                'email': acc['email'],
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        status = "Created" if created else "Updated"
        print(f"[{status}] Admin user: {acc['username']} (password: admin123)")

    # 2. Khoi tao san pham mau hoac cap nhat anh
    json_path = Path(__file__).resolve().parent / 'init_products.json'
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        if Product.objects.count() == 0:
            created_count = 0
            for item in products_data:
                Product.objects.create(
                    name=item['name'],
                    product_type=item.get('product_type', 'accessories'),
                    category=item.get('category', 'normal'),
                    price=item['price'],
                    discount_percent=item.get('discount_percent', 0),
                    rating=item.get('rating', 0),
                    sold_count=item.get('sold_count', 0),
                    is_featured=item.get('is_featured', False),
                    description=item.get('description', ''),
                    image=item.get('image', '')
                )
                created_count += 1
            print(f"Loaded {created_count} initial products with images.")
        else:
            updated_images = 0
            for item in products_data:
                matching = Product.objects.filter(name=item['name'])
                for p in matching:
                    if not p.image and item.get('image'):
                        p.image = item['image']
                        p.save()
                        updated_images += 1
            print(f"Database has {Product.objects.count()} products. Updated images for {updated_images} products.")
    else:
        print("init_products.json not found, skipping product seed.")

    print("--- Database initialization complete! ---")

if __name__ == '__main__':
    init_database()
