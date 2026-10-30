import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Product,PriceRule,Customer,Quote,Order
from .services import compute_price
class PriceTests(TestCase):
    def setUp(self):
        self.product=Product.objects.create(name='Teste')
        PriceRule.objects.create(product=self.product,material='vinil',finish='fosco',price_per_cm2=Decimal('0.10'),setup_fee=Decimal('5'),minimum_total=Decimal('10'),minimum_quantity=1)
        self.params={'product_id':self.product.pk,'width_cm':5,'height_cm':3,'quantity':100,'material':'vinil','finish':'fosco'}
    def test_price(self):
        self.assertEqual(compute_price(**self.params)['total'],Decimal('155.00'))
    def test_invalid_dimension(self):
        with self.assertRaises(ValidationError):compute_price(**{**self.params,'width_cm':0})
    def test_api(self):
        response=self.client.post(reverse('api_calculate'),json.dumps(self.params),content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['total'],'155.00')
    def test_home_accessibility(self):
        response=self.client.get('/')
        self.assertContains(response,'<main')
        self.assertContains(response,'<label')
    def test_quote_creation_and_conversion(self):
        form={**self.params,'name':'Cliente Teste','email':'cliente@example.com','phone':'','zipcode':'','street':'','number':'','neighborhood':'','city':'','state':''}
        response=self.client.post(reverse('submit_quote'),form)
        self.assertEqual(response.status_code,302)
        quote=Quote.objects.get()
        self.assertEqual(quote.total,Decimal('155.00'))
        response=self.client.post(reverse('convert_quote',args=[quote.code]),{'email':'cliente@example.com'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Order.objects.count(),1)
        self.assertEqual(self.client.get(reverse('api_status',args=[quote.code])+'?email=cliente@example.com').status_code,200)
        self.assertEqual(self.client.get(reverse('api_status',args=[quote.code])+'?email=other@example.com').status_code,404)
