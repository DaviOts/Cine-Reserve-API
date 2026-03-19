from django.urls import path

from .views import MyTicketsListView, TicketViewSet

urlpatterns = [
    path('purchase/', TicketViewSet.as_view(), name='ticket-purchase'),

    path('my-tickets/', MyTicketsListView.as_view(), name='my-tickets'),
]