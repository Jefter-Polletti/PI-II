import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    name=models.CharField('Nome',max_length=120)
    description=models.TextField('Descrição',blank=True)
    active=models.BooleanField('Ativo',default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['name'];verbose_name='Produto'
    def __str__(self):return self.name

class PriceRule(models.Model):
    MATERIALS=[('papel','Papel'),('vinil','Vinil'),('tecido','Tecido')]
    FINISHES=[('fosco','Fosco'),('brilho','Brilho'),('sem','Sem acabamento')]
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='price_rules')
    material=models.CharField(max_length=20,choices=MATERIALS)
    finish=models.CharField(max_length=20,choices=FINISHES)
    price_per_cm2=models.DecimalField(max_digits=12,decimal_places=5,validators=[MinValueValidator(Decimal('0'))])
    setup_fee=models.DecimalField(max_digits=10,decimal_places=2,default=0,validators=[MinValueValidator(Decimal('0'))])
    minimum_total=models.DecimalField(max_digits=10,decimal_places=2,default=0,validators=[MinValueValidator(Decimal('0'))])
    minimum_quantity=models.PositiveIntegerField(default=1)
    active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['product','material','finish'],name='unique_product_material_finish')]
        verbose_name='Regra de preço'
    def __str__(self):return f'{self.product} / {self.material} / {self.finish}'

class Customer(models.Model):
    name=models.CharField(max_length=150)
    email=models.EmailField(db_index=True)
    phone=models.CharField(max_length=30,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):return f'{self.name} ({self.email})'

class Address(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='addresses')
    zipcode=models.CharField(max_length=9,blank=True)
    street=models.CharField(max_length=150,blank=True)
    number=models.CharField(max_length=20,blank=True)
    neighborhood=models.CharField(max_length=100,blank=True)
    city=models.CharField(max_length=100,blank=True)
    state=models.CharField(max_length=2,blank=True)
    def __str__(self):return f'{self.city}/{self.state}'

class Quote(models.Model):
    code=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    customer=models.ForeignKey(Customer,on_delete=models.PROTECT,related_name='quotes')
    address=models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True)
    total=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):return str(self.code)

class QuoteItem(models.Model):
    quote=models.ForeignKey(Quote,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    width_cm=models.DecimalField(max_digits=9,decimal_places=2)
    height_cm=models.DecimalField(max_digits=9,decimal_places=2)
    quantity=models.PositiveIntegerField()
    material=models.CharField(max_length=20,choices=PriceRule.MATERIALS)
    finish=models.CharField(max_length=20,choices=PriceRule.FINISHES)
    unit_price=models.DecimalField(max_digits=12,decimal_places=2)
    total=models.DecimalField(max_digits=12,decimal_places=2)

class Order(models.Model):
    RECEIVED='recebido';IN_PROGRESS='producao';FINISHED='concluido';CANCELLED='cancelado'
    STATUSES=[(RECEIVED,'Recebido'),(IN_PROGRESS,'Em produção'),(FINISHED,'Concluído'),(CANCELLED,'Cancelado')]
    quote=models.OneToOneField(Quote,on_delete=models.PROTECT,related_name='order')
    status=models.CharField(max_length=20,choices=STATUSES,default=RECEIVED)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):return f'Pedido {self.quote.code}'
