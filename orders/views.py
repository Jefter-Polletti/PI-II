import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Count
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_GET, require_POST
from .models import Product,Customer,Address,Quote,QuoteItem,Order
from .services import compute_price
from .forms import QuoteForm

def home(request):
    return render(request,'orders/home.html',{'products':Product.objects.filter(active=True)})

def _price_params(data):
    return {k:data.get(k) for k in ('product_id','width_cm','height_cm','quantity','material','finish')}

def _serialize_price(result):
    return {'unit_price':str(result['unit_price']),'total':str(result['total']),'currency':'BRL'}

@require_GET
def api_products(request):
    products=Product.objects.filter(active=True).values('id','name','description')
    return JsonResponse({'products':list(products)})

@require_POST
def api_calculate(request):
    try:
        data=json.loads(request.body)
        if not isinstance(data,dict):return JsonResponse({'error':'Objeto JSON obrigatório.'},status=400)
        result=compute_price(**_price_params(data))
    except (ValueError,TypeError,json.JSONDecodeError,ValidationError) as e:
        message=e.messages[0] if isinstance(e,ValidationError) else 'Parâmetros inválidos.'
        return JsonResponse({'error':message},status=400)
    return JsonResponse(_serialize_price(result))

@require_POST
def submit_quote(request):
    form=QuoteForm(request.POST)
    if not form.is_valid():return render(request,'orders/home.html',{'products':Product.objects.filter(active=True),'form':form},status=400)
    values=form.cleaned_data
    try: price=compute_price(**_price_params(values))
    except ValidationError as e:return render(request,'orders/home.html',{'products':Product.objects.filter(active=True),'form':form,'error':e.messages[0]},status=400)
    with transaction.atomic():
        customer=Customer.objects.create(name=values['name'],email=values['email'],phone=values['phone'])
        address=Address.objects.create(customer=customer,**{k:values[k] for k in ('zipcode','street','number','neighborhood','city','state')})
        quote=Quote.objects.create(customer=customer,address=address,total=price['total'])
        QuoteItem.objects.create(quote=quote,product=price['product'],width_cm=price['width_cm'],height_cm=price['height_cm'],quantity=price['quantity'],material=price['material'],finish=price['finish'],unit_price=price['unit_price'],total=price['total'])
    return redirect('quote_detail',code=quote.code)

@require_GET
def quote_detail(request,code):
    quote=get_object_or_404(Quote.objects.select_related('customer').prefetch_related('items__product'),code=code)
    return render(request,'orders/quote_detail.html',{'quote':quote})

@require_POST
def convert_quote(request,code):
    quote=get_object_or_404(Quote,code=code)
    if request.POST.get('email','').strip().casefold()!=quote.customer.email.casefold():
        return JsonResponse({'error':'E-mail inválido.'},status=403)
    order,_=Order.objects.get_or_create(quote=quote)
    return redirect('order_status',code=quote.code)

@require_GET
def order_status(request,code):
    order=get_object_or_404(Order.objects.select_related('quote__customer'),quote__code=code)
    if request.GET.get('email','').strip().casefold()!=order.quote.customer.email.casefold():
        return render(request,'orders/status_lookup.html',{'code':code})
    return render(request,'orders/status.html',{'order':order})

@require_GET
def api_status(request,code):
    order=get_object_or_404(Order.objects.select_related('quote__customer'),quote__code=code)
    if request.GET.get('email','').strip().casefold()!=order.quote.customer.email.casefold():
        return JsonResponse({'error':'Pedido não encontrado.'},status=404)
    return JsonResponse({'code':str(code),'status':order.status,'status_label':order.get_status_display()})

@staff_member_required
def dashboard(request):
    return render(request,'orders/dashboard.html',{'products':Product.objects.count(),'quotes':Quote.objects.count(),'orders':Order.objects.count(),'revenue':Quote.objects.aggregate(total=Sum('total'))['total'] or Decimal('0')})
