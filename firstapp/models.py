from django.db import models

from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User

from multiselectfield import MultiSelectField

from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

from django.contrib.auth.models import PermissionsMixin

from django.db.models import Q


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255, default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # WITH HELP OF BOOLEAN FIELD
    # is_customer = models.BooleanField(default=True)
    # is_seller = models.BooleanField(default=False)

    # type = (
    #     (1, 'SELLER'),
    #     (2, 'Customer')
    # )
    # user_type = models.IntegerField(choices=type, default=1)

    # usertype = models.ManyToManyField(UserType)    

    class Types(models.TextChoices):
        SELLER = "Seller", "SELLER"
        CUSTOMER = "Customer", "CUSTOMER"


    default_type = Types.CUSTOMER

    #type = models.CharField(_('Type'), max_length=255, choices=Types.choices, default=default_type)
    type = MultiSelectField(choices=Types.choices, default=[], null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    # if the code is not below then accessing default values in User model not in proxy models
    def save(self, *args, **kwargs):
        if not self.id:
            #self.type = self.default_type
            self.type.append(self.default_type)
        return super().save(*args, **kwargs)


class CustomerAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.user.email


class SellerAdditional(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gst = models.CharField(max_length=10)
    warehouse_location = models.CharField(max_length=500)

    def __str__(self):
        return self.user.email


# Created custom query_set // Model managers for the proxy models
class SellerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        #return super().get_queryset(*args, **kwargs).filter(type = CustomUser.Types.SELLER)
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = CustomUser.Types.SELLER))

class CustomerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        #return super().get_queryset(*args, **kwargs).filter(type = CustomUser.Types.CUSTOMER)
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = CustomUser.Types.CUSTOMER))


# Proxy Models ::: They do not create a seperate table
class Seller(CustomUser):
    default_type = CustomUser.Types.SELLER
    objects = SellerManager()

    class Meta:
        proxy = True
    
    def sell(self):
        print("I can sell")
    
    @property
    def showAdditional(self):
        return self.selleradditional

class Customer(CustomUser):
    default_type = CustomUser.Types.CUSTOMER
    objects = CustomerManager()
    class Meta:
        proxy = True
    
    def buy(self):
        print("I can buy")
    
    @property
    def showAdditional(self):
        return self.customeradditional


class Contact(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=20, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{14}$', message="the format : '+919163862585'. Upto 14 digits allowed.")
    phone = models.CharField(max_length=255, validators=[phone_regex])
    query = models.TextField()

    def __str__(self):
        return self.email

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    price = models.FloatField()

    @classmethod
    def updatePrice(cls, product_id, price):
        product = cls.objects.filter(product_id = product_id)
        product = product.first()
        product.price = price
        product.save()
        return product
    
    @classmethod
    def create(cls, product_name, price):
        product = Product(product_name=product_name, price=price)
        product.save()
        return product

    def __str__(self):
        return self.product_name

class CartManager(models.Manager):
    def create_cart(self, user):
        cart = self.create(user=user)
        #try performing more operations
        return cart

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    objects = CartManager()

class ProductInCart(models.Model):
    class Meta:
        unique_together = (('cart', 'product'),)
    product_in_cart_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class Order(models.Model):
    status_choices = (
        (1, 'Not Packed'),
        (2, 'Ready For Shipment'),
        (3, 'Shipped'),
        (4, 'Delivered'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choices, default=1)  

class Deal(models.Model):
    user = models.ManyToManyField(CustomUser)
    deal_name = models.CharField(max_length=255)




# Old code : Not satisfied
# class UserType(models.Model):
#     CUSTOMER = 1
#     SELLER = 2
#     TYPE_CHOICES = (
#         (SELLER, 'Seller'),
#         (CUSTOMER, 'Customer')
#     )

#     id = models.PositiveIntegerField(choices=TYPE_CHOICES, primary_key=True)

#     def __str__(self):
#         return self.get_id_display()
# class Customer(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     address = models.CharField(max_length=500)

#     def __str__(self):
#         return self.user.email


# class Seller(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     gst = models.CharField(max_length=10)
#     warehouse_location = models.CharField(max_length=500)

#     def __str__(self):
#         return self.user.email


# class CustomUser(AbstractUser):
#     username = None
#     email = models.EmailField(_('email address'), unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.email