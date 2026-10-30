from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from .models import PriceRule, Product

MONEY=Decimal('0.01')
def compute_price(*, product_id, width_cm, height_cm, quantity, material, finish):
    try:
        width=Decimal(str(width_cm));height=Decimal(str(height_cm));qty=int(quantity)
        if not width.is_finite() or not height.is_finite() or width<=0 or height<=0 or qty<1 or qty>1000000:
            raise ValueError()
    except (InvalidOperation,TypeError,ValueError,OverflowError):
        raise ValidationError('Dimensões e quantidade devem ser positivas e válidas.')
    try: product=Product.objects.get(pk=product_id,active=True)
    except (Product.DoesNotExist,ValueError,TypeError):raise ValidationError('Produto indisponível.')
    try: rule=PriceRule.objects.get(product=product,material=material,finish=finish,active=True)
    except PriceRule.DoesNotExist:raise ValidationError('Não existe regra de preço ativa para esta configuração.')
    if qty<rule.minimum_quantity:raise ValidationError(f'Quantidade mínima: {rule.minimum_quantity}.')
    total=max((width*height*rule.price_per_cm2*qty + rule.setup_fee),rule.minimum_total).quantize(MONEY,rounding=ROUND_HALF_UP)
    unit=(total/qty).quantize(MONEY,rounding=ROUND_HALF_UP)
    return {'product':product,'rule':rule,'total':total,'unit_price':unit,'width_cm':width,'height_cm':height,'quantity':qty,'material':material,'finish':finish}
