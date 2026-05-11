from django.contrib import admin
from apps.billing.products.product_profile.models import Product
from apps.billing.products.product_category.models import ProductCategory
from apps.billing.products.product_type.models import ProductType
from apps.billing.products.product_status.models import ProductStatus
from apps.billing.orders.order_log.models import Order
from apps.billing.payments.payment_log.models import Payment


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'product_type', 'status', 'base_price', 'is_active', 'is_public', 'created_at']
    list_filter = ['status', 'product_type', 'category', 'is_active', 'is_public']
    search_fields = ['title', 'slug', 'sku', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'product_type', 'status')
        }),
        ('توضیحات', {
            'fields': ('short_description', 'description')
        }),
        ('قیمت و کد', {
            'fields': ('base_price', 'sku')
        }),
        ('تنظیمات', {
            'fields': ('is_active', 'is_public', 'sort_order')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['title', 'slug', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'is_active', 'requires_fulfillment', 'sort_order']
    list_filter = ['is_active', 'requires_fulfillment']
    search_fields = ['title', 'code', 'description']
    prepopulated_fields = {'code': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductStatus)
class ProductStatusAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'is_active', 'is_public', 'sort_order']
    list_filter = ['is_active', 'is_public']
    search_fields = ['title', 'code', 'description']
    prepopulated_fields = {'code': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'user', 'gateway', 'status', 'amount', 'created_at', 'paid_at']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['tracking_code', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'payment', 'tracking_code')
        }),
        ('جزئیات پرداخت', {
            'fields': ('gateway', 'status', 'amount', 'product_id')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'paid_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'gateway', 'status', 'amount', 'created_at', 'paid_at']
    list_filter = ['status', 'gateway', 'manual_review_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'zarinpal_authority', 'bale_wallet_transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'gateway', 'status', 'amount', 'product_id')
        }),
        ('زرین‌پال', {
            'fields': ('zarinpal_authority', 'zarinpal_ref_id'),
            'classes': ('collapse',)
        }),
        ('کارت به کارت', {
            'fields': ('card_to_card_receipt', 'card_to_card_verified_by', 'card_to_card_verified_at'),
            'classes': ('collapse',)
        }),
        ('کیف پول بله', {
            'fields': ('bale_wallet_transaction_id', 'bale_wallet_verified_by', 'bale_wallet_verified_at'),
            'classes': ('collapse',)
        }),
        ('بررسی دستی', {
            'fields': ('manual_review_status', 'manual_review_notes', 'manual_review_by', 'manual_review_at'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'paid_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
