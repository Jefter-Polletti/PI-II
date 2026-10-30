from decimal import Decimal
from django.core.management.base import BaseCommand
from orders.models import Product,PriceRule
class Command(BaseCommand):
    help='Cria produtos e regras de preço FICTÍCIAS para demonstração acadêmica.'
    def handle(self,*args,**kwargs):
        for name in ['Etiqueta adesiva','Etiqueta para roupas','Tag personalizada']:
            product,_=Product.objects.get_or_create(name=name,defaults={'description':'Produto demonstrativo'})
            for material,rate in [('papel','0.025'),('vinil','0.040'),('tecido','0.055')]:
                for finish in ('fosco','brilho','sem'):
                    PriceRule.objects.get_or_create(product=product,material=material,finish=finish,defaults={'price_per_cm2':Decimal(rate),'setup_fee':Decimal('5.00'),'minimum_total':Decimal('20.00'),'minimum_quantity':10})
        self.stdout.write(self.style.SUCCESS('Dados demonstrativos criados. Substitua por preços reais antes de usar comercialmente.'))
