from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Seat

# 1️⃣ GET seats
@api_view(["GET"])
def seats_data(request):
    allSeats = list(Seat.objects.values("seat_id","booked","name"))
    bookedSeats = list(Seat.objects.filter(booked=True).values("seat_id","name"))
    availableSeats = list(Seat.objects.filter(booked=False).values("seat_id"))

    return Response({
        "allSeats": allSeats,
        "bookedSeats": bookedSeats,
        "availableSeats": availableSeats
    })


# 2️⃣ BOOK seat
@api_view(["POST"])
def book_seat(request):
    name = request.data.get("name")
    seat_ids = request.data.get("seat_id")   # list expected

    if not name or not seat_ids:
        return Response({"error":"name and seat required"},status=400)

    if not isinstance(seat_ids, list):
        seat_ids = [seat_ids]

    # max 10 seats per user
    user_count = Seat.objects.filter(name=name, booked=True).count()
    if user_count + len(seat_ids) > 10:
        return Response({"error":"max 10 seats"},status=400)

    with transaction.atomic():
        seats = Seat.objects.filter(seat_id__in=seat_ids)

        if seats.count() != len(seat_ids):
            return Response({"error":"seat not exist"},status=404)

        already_booked = seats.filter(booked=True)
        if already_booked.exists():
            return Response({
                "error":"some seats already booked",
                "seats": list(already_booked.values_list("seat_id",flat=True))
            },status=400)

        seats.update(booked=True, name=name)

    return Response({"message":"seats booked"})

# 3️⃣ CANCEL seat


@api_view(["POST"])
def cancel_seat(request):
    name = request.data.get("name")
    seat_ids = request.data.get("seat_id")

    if not name or not seat_ids:
        return Response({"error":"name and seat required"},status=400)

    if not isinstance(seat_ids, list):
        seat_ids = [seat_ids]

    with transaction.atomic():
        seats = Seat.objects.filter(seat_id__in=seat_ids)

        if seats.count() != len(seat_ids):
            return Response({"error":"seat not exist"},status=404)

        mismatch = seats.exclude(name=name)
        if mismatch.exists():
            return Response({
                "error":"name mismatch",
                "seats": list(mismatch.values_list("seat_id",flat=True))
            },status=400)

        seats.update(booked=False, name=None)

    return Response({"message":"seats cancelled"})