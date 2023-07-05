from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import secrets



# Create your models here.

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price = models.CharField(max_length=100, blank=True, null=True,)
    space_capacity = models.IntegerField(blank=True, null=True,)
    description = models.TextField(max_length=5000, blank=True, null=True,)
    event_date = models.DateField(null=True, blank=True)
    event_time = models.TimeField(null=True, blank=True)
    event_end_date = models.DateTimeField(null=True, blank=True)
    bookings = models.IntegerField(default=0)
    slot_left = models.IntegerField(default=0)
    header_images = models.ImageField(null=True, blank=True, upload_to="images/")
    is_cancelled = models.BooleanField(default=False)


    def __str__(self):
        return self.event_name + " event in " + str(self.location)
 
    def get_absolute_url(self):
        # ------------Return to Details View ---------------
        # return reverse("article-detail", kwargs={"pk": self.pk})
        #-----------Return to Home View-------------
        return reverse("admin_events_page")  

#----------------in settings.py changed Time-ZONE to "Africa/Lagos" to get the correct time zone ------------
    def expired_reg(self):
        mydate = timezone.now()
        if mydate > self.event_end_date:
            return True

    def expired_event(self):
        mydate = timezone.now().date()
        if mydate > self.event_date:
            return True
    
    def bookDate(self):
        d0 = datetime.now().date()
        d1 = self.event_end_date.date()
        print(d1)

        d2 = d1 - d0
        delta = d2.days

        if delta == 1:
            me = str(delta)
            return "You have " + me + " day left to register"
        elif delta > 0:
            me = str(delta)
            return "You have " + me + "days left to register"
        else:
            return "No more registration"







class Customer(models.Model):
    email = models.CharField(max_length=100)
    phone = models.IntegerField()
    event_id = models.CharField(max_length=100)
    ref = models.CharField(max_length=200,  null=True,)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_date = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.verified)



    class Meta:
        ordering = ()
    
    # def __str__(self) -> str:
    #     return f"Payment: {self.amount}"
    
    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Customer.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)
    

    def amount_value(self):
        return int(self.amount) * 100
    

    def verify_payment(self):
        self.verified = True
        self.email
        self.save()
    
