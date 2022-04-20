from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApproachView,
    AreaOfExpertiesView,
    AudienceView,
    COEView,
    CognosIdView,
    DeleteHospitalView,
    EventTypeView,
    HcpRoleView,
    HospiatlPaginationView,
    HospitalCountryView,
    HospitalGetView,
    HospitalUpdateView,
    HospitalView,
    HospitalViewSet,
    HospitalZoneView,
    JustHospitalView,
    LanguageView,
    ProductView,
    RegionView,
    SolutionView,
    SpecialityView,
)

router = DefaultRouter()
router.register(r"hospital-datatable", HospitalViewSet)

app_name = "api"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("hospital-country", HospitalCountryView.as_view(), name="hospital-country"),
    path("coe-view", COEView.as_view(), name="coe-view"),
    path("hospital-zone", HospitalZoneView.as_view(), name="hospital-of-zone"),
    path("cognos-id-view", CognosIdView.as_view(), name="cognos-id-view"),
    path("only-hospital", JustHospitalView.as_view(), name="only-hospital"),
    path("hospital-listing", HospiatlPaginationView.as_view(), name="hospital listing"),
    path("experties", AreaOfExpertiesView.as_view(), name="experties"),
    path("experties/<int:pk>", AreaOfExpertiesView.as_view(), name="experties-by-id"),
    path("approach", ApproachView.as_view(), name="approach"),
    path("approach/<int:pk>", ApproachView.as_view(), name="approach-by-id"),
    path("solution", SolutionView.as_view(), name="solution"),
    path("solution/<int:pk>", SolutionView.as_view(), name="solution"),
    path("region", RegionView.as_view(), name="region"),
    path("region/<int:pk>", RegionView.as_view(), name="region"),
    path("audience/", AudienceView.as_view(), name="audience"),
    path("audience/<int:pk>", AudienceView.as_view(), name="audience"),
    path("language/", LanguageView.as_view(), name="language"),
    path("language/<int:pk>", LanguageView.as_view(), name="language"),
    path("products/", ProductView.as_view(), name="products"),
    path("products/<int:pk>", ProductView.as_view(), name="product"),
    path("hospital/", HospitalView.as_view(), name="hospitals"),
    path("hospital/<int:pk>", HospitalView.as_view(), name="hospital"),
    path("hospital-update", HospitalUpdateView.as_view(), name="hospital-update"),
    path(
        "hospital-update/<int:pk>", HospitalUpdateView.as_view(), name="hospital-update"
    ),
    path(
        "hospital-country/", HospitalCountryView.as_view(), name="hospital-country-vise"
    ),
    path("hospital-get", HospitalGetView.as_view(), name="hospital-get"),
    path("hospital-get/<int:pk>", HospitalGetView.as_view(), name="hospital-get"),
    path("hcp-role", HcpRoleView.as_view(), name="hcp-roles"),
    path("hcp-role/<int:pk>", HcpRoleView.as_view(), name="hcp-role"),
    path("master-proctorship/", include("api.masterproctorship.urls")),
    path(
        "deleted-hospital/<int:pk>",
        DeleteHospitalView.as_view(),
        name="deleted-hospital",
    ),
    path("trainee/", include("api.trainee.urls")),
    path("proctorship/", include("api.proctorship.urls")),
    path("preceptorship/", include("api.preceptorship.urls")),
    path("zone/", include("api.zone.urls")),
    path("users/", include("api.users.urls")),
    path("proctors/", include("api.proctors.urls")),
    path("status/", include("api.status.urls")),
    path("feedback/", include("api.feedback.urls")),
    path("invoice/", include("api.invoice.urls")),
    path("speakingevent/", include("api.speakingevent.urls")),
    path("get-event-constant", EventTypeView.as_view(), name="event-types"),
    path("get-speciality-constant", SpecialityView.as_view(), name="speciality"),
    path("new-mics/", include("api.newmics.urls")),
]
