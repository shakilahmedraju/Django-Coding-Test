

# Create your views here.
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from datetime import datetime
from .models import *


def home(request):
    return render(request, 'home.html',)

def create_product(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        sku = request.POST.get('sku')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Create the product
        product = Product.objects.create(title=title, sku=sku, description=description)

        # Create product variants and prices
        variant_names = request.POST.getlist('variants')
        prices = request.POST.getlist('prices')
        stocks = request.POST.getlist('stocks')

        for i in range(len(variant_names)):
            variant_name = variant_names[i]
            price = prices[i]
            stock = stocks[i]

            # Create or get the Variant instance
            variant, _ = Variant.objects.get_or_create(title=variant_name)

            # Create the ProductVariant instance
            product_variant = ProductVariant.objects.create(variant=variant, product=product)

            ProductVariantPrice.objects.create(
                product_variant_one=product_variant,
                price=price,
                stock=stock,
                product=product
            )

        # Create product image
        ProductImage.objects.create(product=product, file_path=image)

        return redirect('product_list')
    else:
        return render(request, 'create_product.html')


def product_list(request):
    title = request.GET.get('title')
    variant = request.GET.get('variant')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    date = request.GET.get('date')

    products = Product.objects.all()

    if title:
        products = products.filter(title__icontains=title)

    if variant:
        products = products.filter(productvariant__variant_id=variant)

    

    if min_price and max_price:
        variant_prices = ProductVariantPrice.objects.filter(
            product_variant_one__product__in=products,
            price__gte=min_price, price__lte=max_price
        )
        product_ids = set(vp.product_variant_one.product_id for vp in variant_prices)
        products = products.filter(id__in=product_ids)

    if date:
        date = datetime.strptime(date, "%Y-%m-%d")
        products = products.filter(created_at__date=date.date())

    
    

    # Prefetch related variant prices to reduce database queries
    products = products.prefetch_related('productvariantprice_set')

    paginator = Paginator(products, 3)  # 10 items per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    variants = Variant.objects.all()

    return render(request, 'product_list.html', {
        'products': products, 
        'variants': variants, 
        })

