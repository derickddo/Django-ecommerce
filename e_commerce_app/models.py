from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django.template.defaultfilters import date, time

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.PositiveBigIntegerField(null=True)
    address = models.CharField(max_length=50, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'user'


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    slug = models.SlugField(null=True, blank=True, unique=True,editable=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def save(self):
        self.slug = slugify(f"{self.title} {self.pk}")
        return super().save()

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            'slug': self.slug
        })
    class Meta:
        db_table = 'item'
    




class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_query_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')

    class Meta:
        db_table = 'item_image'


    
class OrderItem(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.quantity} x {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price

    
    class Meta:
        db_table = 'order_item'

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'Order {self.pk} by {self.user.username}'

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total
    
    def phone_number(self):
        return f"{self.user.phone_number}"
    
    def address(self):
        return f"{self.user.address}"
    
    def timestamp(self):
        return f'{date(self.payment.timestamp)} {time(self.payment.timestamp)}'
    
    
    class Meta:
        db_table = 'order'


class Payment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.amount} GHS'
    
    class Meta:
        db_table = 'payment'



