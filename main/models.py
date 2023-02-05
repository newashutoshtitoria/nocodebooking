from django.db import models
from core.settings import AUTH_USER_MODEL
from datetime import date

class Category(models.Model):
    """
    Model for Category of the packages/services
    """
    category = models.CharField(unique=True, max_length=50, null=False, blank=False)
    icon = models.ImageField(null=False, blank=False, upload_to='Category_Icon')
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.category


class PriceTag(models.Model):
    """
    Model for Price Tag of the packages/services
    """
    price_tag = models.CharField(unique=True, max_length=50, null=False, blank=False)


    def __str__(self):
        return self.price_tag



class Package(models.Model):
    """
        Model for packages/services
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_package', blank=False, null= False)
    icon = models.ImageField(upload_to="package_Icons", blank=True)
    package_name = models.CharField(max_length=100, null=False, blank=False)
    original_price = models.FloatField(null=True, blank=True)
    offering_price = models.FloatField(null=True, blank=True)
    price_tag = models.ForeignKey(PriceTag, on_delete=models.SET_NULL, related_name='pricetag_package', blank=True, null= True)
    description = models.TextField()
    total_time = models.CharField(max_length=100, null=True)
    offer = models.BooleanField(default=False)
    status = models.BooleanField(default=True)


    created_on = models.DateField(auto_now_add=True, editable=True)


    def __str__(self):
        return self.package_name

class Variants(models.Model):
    """
        Model for Variants of a packages/services
    """
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='package_variants', blank=False, null=False)
    variant = models.CharField(max_length=100, null=False, blank=False)
    original_price = models.FloatField(null=True, blank=True)
    offering_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.variant

class AddOns(models.Model):
    """
        Model for Add-On of a packages/services
    """
    package = models.ForeignKey(Package, on_delete=models.CASCADE,related_name='package_addons', blank=False, null=False)
    add_on_name = models.CharField(max_length=100, null=False, blank=False)
    additional_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.add_on_name




Select_Type=(
    ('static', 'static'),
    ('link', 'link'),
    ('package', 'package'),
    ('category', 'category')
)


class Carousel(models.Model):
    """
        Model for Carousel
    """
    order_by = models.IntegerField()
    carousel_img = models.ImageField(upload_to="Carousel_Image", null=False, blank=False)
    select_type = models.CharField(choices=Select_Type,default="static", max_length=100, null=True, blank=True)

    select_type_ids = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)

    status = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    validity = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_select_type(self):
        lst =[]
        try:
            for package in eval(self.select_type_ids):
                lst.append(Package.objects.get(id=package))
        except:
            pass
        return lst



Coupon_Type = (
    ('percentage_discount', 'percentage_discount'),
    ('flat_discount', 'flat_discount')
)

Apply_Coupon = (
    ('category', 'category'),
    ('package', 'package'),
    ('all', 'all'),
)

class DiscountedCoupons(models.Model):
    """
        Model for Coupons
    """
    select_coupon_type = models.CharField(choices=Coupon_Type,default="static", max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    coupon_code = models.CharField(max_length=30)
    flat_percent_value = models.FloatField(null=True, blank=True)
    uses_per_customer = models.PositiveIntegerField(blank=True, null=True)

    minimum_order_value = models.FloatField(null=False, blank=False)
    maximum_order_value = models.FloatField(null=True, blank=True)

    apply_coupon_on = models.CharField(choices=Apply_Coupon,default="all", max_length=100, null=True, blank=True)

    packages = models.ManyToManyField(Package, blank=True, related_name='package_discountcoupons', null=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='categories_discountcoupons', null=True)

    show_coupons_to_customer = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)

    from_date = models.DateField()
    from_time = models.TimeField()
    to_date = models.DateField()
    to_time = models.TimeField()

    def __str__(self):
        return self.title

    def check_validity(self, amount):
        if self.from_date <= date.today() and self.to_date >=date.today() and self.active:
            if self.minimum_order_value:
                if self.minimum_order_value <=amount:
                    if self.select_coupon_type == 'percentage_discount':
                        newval = amount*float(self.flat_percent_value)/100
                    elif self.select_coupon_type == 'flat_discount':
                        newval = amount-float(self.flat_percent_value)
                else:
                    newval = amount

            if self.minimum_order_value and self.maximum_order_value:
                if self.minimum_order_value <=amount and self.maximum_order_value >=amount:
                    if self.select_coupon_type == 'percentage_discount':
                        newval = amount*float(self.flat_percent_value)/100
                    elif self.select_coupon_type == 'flat_discount':
                        newval = amount-float(self.flat_percent_value)
                else:
                    newval = amount

            return newval
        raise ValueError("Discount Error")



ADDRESS_TYPE = {
    ('Home', 'Home'),
    ('Others', 'Others')
}


class UserAddress(models.Model):
    """
    Model for storing multiple address of user.
    """
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_useraddress')
    house_no = models.TextField(default=" ", null=True, blank=True)
    street = models.TextField(default=" ", null=False, blank=False)
    city = models.TextField(default=" ", null=False, blank=False)
    postal_code = models.CharField(null=True, blank=True, default="", max_length=6)
    state = models.TextField(default="", null=False, blank=False)
    address_type = models.CharField(max_length=20, null=True, blank=True, choices=ADDRESS_TYPE)

    def __str__(self):
        return "Address of %s" % (self.user.name,)





PACKAGE_STAGES = (
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
)

class Checkout(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_checkout')
    address = models.TextField(blank=False, null=False)
    coupon = models.ForeignKey(DiscountedCoupons, on_delete=models.SET_NULL, related_name='coupon_checkout', blank=True, null=True)

    package_stages = models.CharField(choices=PACKAGE_STAGES, max_length=100, null=True, blank=True)
    payment_stages = models.CharField(max_length=100, null=True, blank=True)

    price_paid = models.FloatField(default=0)
    refund = models.BooleanField(default=False)
    read = models.BooleanField(default=False)

    appointment_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)



class PackageCheckout(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, blank=True, null=True, related_name='package_checkouts')
    packages = models.ForeignKey(Package,on_delete=models.CASCADE, blank=True, null=True, related_name='packages_packagescheckout')
    variants = models.ForeignKey(Variants,on_delete=models.CASCADE,  blank=True, null=True, related_name='variants_packagecheckouts')
    addon = models.ManyToManyField(AddOns, blank=True, null=True, related_name='addon_packagecheckout')
