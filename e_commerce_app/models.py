from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.text import slugify
from django.urls import reverse

    
class Category(models.Model):
    name = models.CharField(max_length = 30, null = False, blank = False, unique = True)
    def __str__(self) -> str:
        return f'{self.name}'
    class Meta:
        verbose_name_plural = 'categories'
        db_table = 'category'



class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    slug = models.SlugField(null=True, blank=True, unique=True)
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
    


class Size(models.Model):
    SIZE_CHOICES = [
        ('Small','S'), 
        ('Medium', 'M'), 
        ('Large', 'L'),
        ('Extra Large', 'XL'),
        ('Extra Extra Large', '2XL'),
    ]
    name = models.CharField(max_length=30)
    code = models.CharField(choices=SIZE_CHOICES, max_length=30)
    
    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'size'



class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_query_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')

    class Meta:
        db_table = 'item_image'


    
class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.quantity} x {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    
    class Meta:
        db_table = 'order_item'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
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
            total += order_item.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        return total
    
    class Meta:
        db_table = 'order'


class Payment(models.Model):
    user = models.ForeignKey('UserProfile',on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.amount} GHS'

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    phone_number = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

