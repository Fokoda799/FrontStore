from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models


# =======================
#         Filters
# =======================
class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "LOW"), (">10", "OK")]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        if self.value() == ">10":
            return queryset.filter(inventory__gte=10)


# =======================
#         Inlines
# =======================
class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ["product"]
    extra = 0


# =======================
#          Models
# =======================
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    list_per_page = 10
    search_fields = ["title__istartswith"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html('<a href="{}">{} unites</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "inventory_status", "collection_title"]
    list_editable = ["price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    actions = ["clear_inventory"]
    search_fields = ["title__istartswith"]
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "LOW"
        return "OK"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{update_count} products were successfully updated",
            messages.SUCCESS,
        )


@admin.register(models.Costumer)
class CostumerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders_count(self, costumer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"costumer__id": str(costumer.id)})
        )
        return format_html('<a href="{}">{}</a>', url, costumer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "costumer", "payment_status"]
    list_per_page = 10
    ordering = ["placed_at"]
    inlines = [OrderItemInline]

    def order_number(self, order):
        return f"ORDER-{order.id}"


admin.site.register(models.Promotion)
admin.site.register(models.OrderItem)
admin.site.register(models.Cart)
admin.site.register(models.CartItem)
admin.site.register(models.Address)
