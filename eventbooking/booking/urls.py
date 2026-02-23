from django.urls import path
from .views import seats_data, book_seat, cancel_seat

urlpatterns = [
    path("seats/", seats_data),
    path("book/", book_seat),
    path("cancel/", cancel_seat),
]