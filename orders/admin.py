from django.contrib import admin
from .models import Product,PriceRule,Customer,Address,Quote,QuoteItem,Order
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):list_display=['name','active'];list_filter=['active'];search_fields=['name']
@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):list_display=['product','material','finish','price_per_cm2','setup_fee','active'];list_filter=['active','material','finish']
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):list_display=['name','email','phone'];search_fields=['name','email']
admin.site.register(Address)
class QuoteItemInline(admin.TabularInline):model=QuoteItem;extra=0;readonly_fields=['product','width_cm','height_cm','quantity','material','finish','unit_price','total'];can_delete=False
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):list_display=['code','customer','total','created_at'];inlines=[QuoteItemInline];readonly_fields=['code','customer','address','total']
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):list_display=['quote','status','created_at'];list_filter=['status']
