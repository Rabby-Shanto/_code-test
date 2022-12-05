from django.views import generic
from django.shortcuts import render
from product.models import Variant,Product,ProductVariantPrice,ProductVariant
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Max


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'


    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context





def ListProduct(request):
    products  = Product.objects.all()
    paginator = Paginator(products,2)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    products_count = products.count()
    variations = Variant.objects.all()
    variants = ProductVariant.objects.all().values('variant_title').distinct()


    title_query = request.GET.get('title','')
    variant_query  = request.GET.get('variant','')
    date_query  = request.GET.get('date','')

    if title_query != '' and title_query is not None:
        paged_products = products.filter(title__icontains=title_query)
    if variant_query != '' and variant_query is not None:
        paged_products = Product.objects.prefetch_related("productvariant_set").filter(title__icontains=title_query,productvariant__variant_title__icontains=variant_query)


    if 'price_from' in request.GET:

        filter_price1 = request.GET.get('price_from')
        filter_price2 = request.GET.get('price_to')


        if filter_price1 =='':
            filter_price1=0
        if filter_price2=='':
            filter_price2=ProductVariantPrice.objects.all().aggregate(Max('price'))
            filter_price2 = float(filter_price2['price__max'])

        paged_products = Product.objects.prefetch_related("productvariantprice_set").filter(title__icontains=title_query,productvariantprice__price__range=(filter_price1,filter_price2))

    if date_query != '' and date_query is not None:
        
        paged_products = products.filter(created_at=date_query)


    context = {

                'products' : paged_products,
                'products_count' : products_count,
                'variations' : variations,
                'variants' : variants
    }

    return render(request,"products/list.html",context)