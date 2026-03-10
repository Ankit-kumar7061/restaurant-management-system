from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView as AuthLoginView
from Base_App.models import BookTable, AboutUs, Feedback, ItemList, Items, Cart
from django.contrib.auth import logout
from django.urls import reverse_lazy


# ---------------- CART ---------------- #

def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Items, id=item_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            item=item
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'message': 'Item added to cart'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_cart_items(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('item')

        items = [
            {
                'name': cart_item.item.Item_name,
                'quantity': cart_item.quantity,
                'price': cart_item.item.Price,
                'total': cart_item.quantity * cart_item.item.Price,
            }
            for cart_item in cart_items
        ]

        return JsonResponse({'items': items})

    return JsonResponse({'error': 'User not authenticated'}, status=401)


# ---------------- LOGIN ---------------- #

class LoginView(AuthLoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('Home')


def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('Home')


# ---------------- SIGNUP ---------------- #

def SignupView(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'login.html', {'tab': 'signup'})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'login.html', {'tab': 'signup'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()

        login(request, user)

        messages.success(request, f"Welcome {username}! Your account has been created.")

        return redirect('Home')

    return render(request, 'login.html', {'tab': 'signup'})


# ---------------- HOME ---------------- #

def HomeView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()
    review = Feedback.objects.all().order_by('-id')[:5]

    return render(request, 'home.html', {
        'items': items,
        'list': list,
        'review': review
    })


# ---------------- ABOUT ---------------- #

def AboutView(request):
    data = AboutUs.objects.all()
    return render(request, 'about.html', {'data': data})


# ---------------- MENU ---------------- #

def MenuView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()

    return render(request, 'menu.html', {
        'items': items,
        'list': list
    })


# ---------------- BOOK TABLE ---------------- #

def BookTableView(request):

    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    if request.method == 'POST':
        name = request.POST.get('user_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('user_email')
        total_person = request.POST.get('total_person')
        booking_data = request.POST.get('booking_data')

        if name != '' and len(phone_number) == 10 and email != '' and total_person != '0' and booking_data != '':

            data = BookTable(
                Name=name,
                Phone_number=phone_number,
                Email=email,
                Total_person=total_person,
                Booking_date=booking_data
            )

            data.save()

            subject = 'Booking Confirmation'
            message = f"Hello {name},\n\nYour booking has been successfully received.\nTotal persons: {total_person}\nBooking date: {booking_data}"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )

            messages.success(request, 'Booking request submitted successfully!')

            return render(request, 'feedback.html', {
                'success': 'Booking request submitted successfully!'
            })

    return render(request, 'book_table.html', {
        'google_maps_api_key': google_maps_api_key
    })


# ---------------- FEEDBACK ---------------- #

def FeedbackView(request):

    if request.method == 'POST':

        name = request.POST.get('User_name')
        feedback = request.POST.get('Description')
        rating = request.POST.get('Rating')
        image = request.FILES.get('Selfie')

        if name != '':

            feedback_data = Feedback(
                User_name=name,
                Description=feedback,
                Rating=rating,
                Image=image
            )

            feedback_data.save()

            messages.success(request, 'Feedback submitted successfully!')

            return render(request, 'feedback.html', {
                'success': 'Feedback submitted successfully!'
            })

    return render(request, 'feedback.html')


# ---------------- USER BOOKINGS ---------------- #

def MyBookingsView(request):

    if not request.user.is_authenticated:
        return redirect('login')

    bookings = BookTable.objects.filter(Email=request.user.email)

    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })


# ---------------- CANCEL BOOKING ---------------- #

def CancelBookingView(request, id):

    booking = get_object_or_404(BookTable, id=id)

    if request.user.email == booking.Email:
        booking.delete()
        messages.success(request, "Booking cancelled successfully")

    return redirect('my_bookings')


# ---------------- USER DASHBOARD ---------------- #

def DashboardView(request):

    if not request.user.is_authenticated:
        return redirect('login')

    total_bookings = BookTable.objects.filter(Email=request.user.email).count()

    return render(request, 'dashboard.html', {
        'user': request.user,
        'total_bookings': total_bookings
    })

# ---------------- ADMIN ANALYTICS DASHBOARD ---------------- #

@staff_member_required
def AdminDashboardView(request):

    total_users = User.objects.count()
    total_bookings = BookTable.objects.count()
    total_feedback = Feedback.objects.count()
    total_items = Items.objects.count()

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_feedback': total_feedback,
        'total_items': total_items
    })