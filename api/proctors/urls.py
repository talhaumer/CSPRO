from django.urls import path

from api.proctors.views import (
    DeleteProctorsView,
    GloabalProctorsView,
    ProctorsOfCOEView,
    ProctorsOfZoneView,
    ProctorsPaginationView,
    ProctorsTestView,
    ProctorsUpdateView,
    ProctorsView,
    SpeakersProctorsView,
)

app_name = "proctors"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("add-proctors", ProctorsView.as_view(), name="proctors"),
    path("add-proctors/<int:pk>", ProctorsView.as_view(), name="proctor"),
    path("zone-proctors", ProctorsOfZoneView.as_view(), name="zone-proctors"),
    path("zone-proctors/<int:pk>", ProctorsOfZoneView.as_view(), name="zone-proctors"),
    path("global-proctors", GloabalProctorsView.as_view(), name="global-proctors"),
    path(
        "delete-proctors/<int:pk>", DeleteProctorsView.as_view(), name="delete-proctors"
    ),
    path("update-proctors", ProctorsUpdateView.as_view(), name="update-proctors"),
    path(
        "update-proctors/<int:pk>", ProctorsUpdateView.as_view(), name="update-proctors"
    ),
    path("proctors-listing", ProctorsPaginationView.as_view(), name="proctors-listing"),
    path("proctors-coe", ProctorsOfCOEView.as_view(), name="proctors-of-coe"),
    path(
        "speaker-proctor-view",
        SpeakersProctorsView.as_view(),
        name="speaker-proctor-view",
    ),
    path("testing", ProctorsTestView.as_view(), name="testing"),
]
