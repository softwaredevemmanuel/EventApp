import genericpath
from django.shortcuts import redirect, render
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from datetime import datetime, date
from .models import Event, Customer
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.contrib.auth import logout



# Create your views here.
def home(request):
    return render(request, "login.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_superuser:
                return redirect("admin_events_page")
            elif user.is_cashier:
                return redirect("admin_events_page")
            else:
                return redirect("login")
        else:
            messages.error(request, "Wrong Admin Details")
            return redirect("user_events_page")


def dashboard(request):
    return render(request, "events_page.html")


def free(request):
    return render(request, "add_free_events.html")

def paid(request):
    return render(request, "add_paid_events.html")


def create_free_event(request):
    if request.method == "POST" and request.FILES['header_images']:
        event_name = request.POST["event_name"]
        location = request.POST["location"]
        event_time = request.POST["event_time"]
        description = request.POST["description"]
        event_date = request.POST["event_date"]
        event_end_date = request.POST["event_end_date"]
        header_images = request.FILES["header_images"]


        a = Event(
            event_name=event_name,
            location=location,
            event_time=event_time,
            description=description,
            event_date=event_date,
            event_end_date=event_end_date,
            header_images=header_images,
        )
        a.save()
        messages.success(request, "Event Registered Successfully")
        return redirect("admin_events_page")

def create_paid_event(request):
    if request.method == "POST" and request.FILES['header_images']:
        event_name = request.POST["event_name"]
        location = request.POST["location"]
        price = request.POST["price"]
        space_capacity = request.POST["space_capacity"]
        event_end_date = request.POST["event_end_date"]
        event_time = request.POST["event_time"]
        description = request.POST["description"]
        event_date = request.POST["event_date"]
        header_images = request.FILES["header_images"]

        a = Event(
            event_name=event_name,
            location=location,
            description=description,
            event_date=event_date,
            event_time=event_time,
            header_images=header_images,
            event_end_date=event_end_date,
            space_capacity=space_capacity,
            price=price,
            slot_left = space_capacity
        )
        a.save()

        messages.success(request, "Event Registered Successfully")
        return redirect("admin_events_page")




class EventView(ListView):
    model = Event
    template_name = "events_page.html"
    paginate_by = 4



class EventDetailsView(DetailView):
    # modal = Free
    queryset = Event.objects.all()
    template_name = "EventDetails.html"

class FreeEventView(ListView):
    model = Event
    template_name = "free-event-page.html"
    paginate_by = 10


class PaidEventView(ListView):
    model = Event
    template_name = "paid-event-page.html"
    paginate_by = 10



class UpdateEventView(SuccessMessageMixin, UpdateView):
    model = Event
    template_name = 'update-event.html'
    fields = ['event_name', 'location', 'price', 'space_capacity', 'description', 'event_date', 'event_end_date']
    success_message = 'Event Updated successfully!!'

    

    def form_valid(self, form):

        event = self.get_object()
        print(event.space_capacity-event.bookings)
        space_capacity = form.cleaned_data['space_capacity']
        event.slot_left = space_capacity-event.bookings
        print(event.slot_left)

        if space_capacity < event.bookings:
            messages.error(self.request, "Space capacity cant be less than the number of bookings!!.")
            form.add_error('space_capacity', 'Space capacity can not be less than bookings')
            return self.form_invalid(form)
        
        event.slot_left = space_capacity-event.bookings
        event.space_capacity = space_capacity

        response = super().form_valid(form)
        event.save()
        return response

    

class UpdateFreeEvent(SuccessMessageMixin, UpdateView):
    model = Event
    template_name = 'update-event.html'
    fields = ['event_name', 'location', 'description', 'event_date', 'event_end_date']
    success_message = 'Event Updated successfully!!'


class DeleteEventView(SuccessMessageMixin, DeleteView):
    model = Event
    template_name = 'delete_post.html'
    success_url = reverse_lazy('admin_events_page')
    success_message = 'Event deleted successfully!!'

def Cancel(request, pk):
    poll=Event.objects.get(pk=pk)
    eventId = poll.bookings
    if eventId == 0:
        Event.objects.filter(id=pk).update(is_cancelled="True")
        messages.success(request, "Event has been Cancelled Successfully")
        return redirect("admin_events_page")
    else:
        messages.error(request, "Someone has registered and Event cannot be  Cancelled")
        return redirect("admin_events_page")

class CancelledView(ListView):
    model = Event
    template_name = "cancelled.html"
    paginate_by = 10


def UndoCancel(request, pk):
    Event.objects.filter(id=pk).update(is_cancelled="False")
    messages.success(request, "Event has been Restored Successfully")
    return redirect("admin_events_page")


def view_details(request, pk):
    poll=Event.objects.get(pk=pk)
    eventId = poll.id

#? Calculating the expected amount of money to be made in that event
    a = poll.space_capacity 
    b = poll.price
    c = int(a) * int(b)
    #print(poll.id)

    
    paid_candidates = Customer.objects.filter(event_id=eventId, verified=True)
    reg_candidates = Customer.objects.filter(event_id=eventId)
    booking = Customer.objects.filter(event_id=eventId)
    total_it = Customer.objects.filter(event_id=eventId, verified=True).aggregate(Sum("amount"))['amount__sum']



    context={
        'paid_candidate_count': paid_candidates.count(),
        'reg_candidate_count': reg_candidates.count(),
        'candidate': booking,
        'total_it': total_it,
        'c': c
    }
    return render(request, "admin.html", context)

def view_free_details(request, pk):
    poll=Event.objects.get(pk=pk)
    eventId = poll.id
    
    paid_candidates = Customer.objects.filter(event_id=eventId, verified=True)
    reg_candidates = Customer.objects.filter(event_id=eventId)
    booking = Customer.objects.filter(event_id=eventId)
    total_it = Customer.objects.filter(event_id=eventId, verified=True).aggregate(Sum("amount"))['amount__sum']



    context={
        'paid_candidate_count': paid_candidates.count(),
        'reg_candidate_count': reg_candidates.count(),
        'candidate': booking,
        'total_it': total_it,
    }
    return render(request, "admin.html", context)

def edit_paid_event(request):
    return render(request, "edit-page.html")

def logout_view(request):
    logout(request)
    return redirect("user_events_page")