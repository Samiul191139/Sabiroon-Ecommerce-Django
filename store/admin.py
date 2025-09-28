from django.contrib import admin
from .models import Customer, Product, Order, Order_Product, Shipping

# Inline for Shipping inside Order
class ShippingInline(admin.TabularInline):
    model = Shipping
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [ShippingInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')   # Show these columns in product list
    search_fields = ('name',)          # Search by product name
    list_filter = ('price',)           # Filter sidebar by price
    fields = ('name', 'price', 'description', 'image')  # Fields in form


# Keep the rest as before
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_Product)
admin.site.register(Shipping)
