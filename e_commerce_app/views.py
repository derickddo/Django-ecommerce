from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, Order, OrderItem, Category, UserProfile, Payment
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import CheckoutForm
import random
import string

# Create your views here.
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class HomeView(View):
    def get(self, request):
        if self.request.GET.get('search'):
            search = self.request.GET.get('search')
        else:
            search = ""
        if self.request.GET.get('q'):
            query_param =  self.request.GET.get('q')
        else:
             query_param = ""
        items = Item.objects.filter(Q(category__name__icontains=query_param)|Q(title__icontains=search))
        paginator = Paginator(items, per_page=10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
       
        categories = Category.objects.all()
        context = {
            'object_list':page,
            'categories':categories
        }
        return render(self.request, 'home.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
    

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class CheckoutView(View, LoginRequiredMixin):
    def get(self, request):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            context = {
                'order':order,
                'form':CheckoutForm()
            }
            return render(request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("checkout")
        
    def post(self, request):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            user = UserProfile.objects.filter(user = request.user).first()
            if not user:
               user = UserProfile.objects.create(
                   user=request.user, 
                   first_name= form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], 
                   address=form.cleaned_data['address'], 
                   phone_number=form.cleaned_data['phone_number']
                )
            payment = Payment.objects.create(
                user=user, 
                amount=order.get_total()
            )
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(request, "Your order was successful!") 
            return redirect('home')
        

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)

