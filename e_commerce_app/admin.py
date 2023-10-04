from .models import Item, Order, OrderItem, Category, ItemImage, Payment, UserProfile
from django.contrib import admin
from django.contrib import messages
from django import forms

def make_order_delivered(modeladmin, request, queryset):
    queryset.update(being_delivered=True)
    modeladmin.message_user(request, f"Selected orders marked as received.")

def make_order_not_delivered(modeladmin, request, queryset):
    queryset.update(being_delivered=False)
    modeladmin.message_user(request, f"Selected orders marked as not delivered.")

def make_order_received(modeladmin, request, queryset):
    # Loop through the selected orders in the queryset
    for order in queryset:
        # Check if the order is being delivered
        if order.being_delivered:
            # Update the 'received' field to True for each order
            order.received = True
            order.save()
            # Refresh the admin change list page
            modeladmin.message_user(request, f"Selected orders marked as received.")
        else:
            # If the order is not being delivered, display an error message
            messages.error(request, f"Order for {order.user} cannot be marked as received because it is not being delivered.")
    


def make_order_not_received(modeladmin, request, queryset):
    queryset.update(received=False)
    modeladmin.message_user(request, f"Selected orders marked as not received.")


make_order_delivered.short_description = 'Update orders as being delivered'
make_order_not_delivered.short_description = 'Update orders as not being delivered'
make_order_received.short_description = 'Update orders as received'
make_order_not_received.short_description = 'Update orders as not received'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'payment',
        'ref_code',
        
        
       
    ]
    list_display_links = [
        'user',
        'payment',
        
        
    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'ref_code',
    
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_order_delivered, make_order_not_received, make_order_received, make_order_not_delivered]
class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 0  # Set the maximum number of extra forms to 3
    # max_num = 3
    form = ItemImageForm

    
    def get_max_num(self, request, obj=None, **kwargs):
        return 3

    def has_delete_permission(self, request, obj=None):
        # Allow deleting images
        return True
    
  
    
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "item":
    #         # Set the item field to the current item being edited
    #         kwargs["queryset"] = Item.objects.filter(id=request.resolver_match.kwargs['object_id'])
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def has_add_permission(self, request, obj=None):
    #     messages.warning(request, f"You can only add {self.max_num} images for this item.")
           

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemImageInline]
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, ItemImageInline):
                # Calculate the number of existing images for the item
                count = ItemImage.objects.filter(item=obj).count()
                max_num = inline.get_max_num(request, obj)
                if count >= max_num:
                    # Display a message if the maximum number of images is reached
                    messages.warning(request, f"You can only add {max_num} images for this item.")
                break
        return super().get_formsets_with_inlines(request, obj)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'timestamp']
    search_fields = ['user']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phone_number', 'address']

admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Category)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)