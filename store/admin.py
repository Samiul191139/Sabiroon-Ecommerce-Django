from django.contrib import admin
from .models import Customer, Product, Order, Order_Product, Shipping

# Inline for Shipping inside Order
class ShippingInline(admin.TabularInline):
    model = Shipping
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [ShippingInline]

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_Product)
admin.site.register(Shipping)  # Keep this line to show Shipping as a separate table
