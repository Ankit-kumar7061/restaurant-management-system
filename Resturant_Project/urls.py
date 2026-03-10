from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Base_App.views import *

urlpatterns = [

    path('admin/', admin.site.urls),

    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView, name='signup'),
    path('logout/', LogoutView, name='logout'),

    path('', HomeView, name='Home'),
    path('menu/', MenuView, name='Menu'),
    path('about/', AboutView, name='About'),

    path('book_table/', BookTableView, name='Book_Table'),
    path('feedback/', FeedbackView, name='Feedback_Form'),

    # USER BOOKINGS
    path('my-bookings/', MyBookingsView, name='my_bookings'),

    # CANCEL BOOKING
    path('cancel-booking/<int:id>/', CancelBookingView, name='cancel_booking'),

    # USER DASHBOARD
    path('dashboard/', DashboardView, name='dashboard'),

    path('admin-dashboard/', AdminDashboardView, name='admin_dashboard'),

    # CART
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('get-cart-items/', get_cart_items, name='get_cart_items'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)