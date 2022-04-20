from django.conf.urls import include, url
from django.urls import path
from rest_framework.routers import DefaultRouter

from api.zone.views import (
    AddZoneView,
    CountriesAnnoysView,
    CountriesOfZoneView,
    CountriesPaginationView,
    CountriesView,
    GetZoneView,
    UpdateZoneView,
    ZoneEnableDisableView,
    ZoneViewSet,
)

router = DefaultRouter()
router.register(r"zone-datatable", ZoneViewSet)
app_name = "zone"

urlpatterns = [
    url(r"", include(router.urls)),
    path("countries/", CountriesView.as_view(), name="countries"),
    path("countries/<int:pk>", CountriesView.as_view(), name="countries-by-id"),
    path("add-zone/", AddZoneView.as_view(), name="zone"),
    path("add-zone/<int:pk>", AddZoneView.as_view(), name="zone-by-id"),
    path("get-zone-pagination", GetZoneView.as_view(), name="zone get-zone-pagination"),
    path(
        "get-countries-pagination",
        CountriesPaginationView.as_view(),
        name="get-countries-pagination",
    ),
    path(
        "user-zone-countries", CountriesOfZoneView.as_view(), name="user-zone-countries"
    ),
    path("update-zone-view/<int:pk>", UpdateZoneView.as_view(), name="update-zone"),
    path(
        "zone-enabled-disabled/<int:pk>",
        ZoneEnableDisableView.as_view(),
        name="zone enableb disabled",
    ),
    path(
        "unknown-user-countries",
        CountriesAnnoysView.as_view(),
        name="unknown-user-countries",
    ),
    path(
        "unknown-user-countries/<int:pk>",
        CountriesAnnoysView.as_view(),
        name="unknown-user-countries",
    ),
]
