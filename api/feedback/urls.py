from django.urls import path

from api.feedback.views import (
    CertificateFormView,
    MemoProctorFeedBackView,
    PercevelDriverDataView,
    ProctorFeedbackView,
    RatingDataView,
    ReasonDataView,
    SoloSmartProctorFeedBackView,
    TraineeFeedbackView,
)

app_name = "feedback"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path(
        "perceval-driver-data",
        PercevelDriverDataView.as_view(),
        name="perceval-driver-data",
    ),
    path("reason-data", ReasonDataView.as_view(), name="reason-data"),
    path("rating-data", RatingDataView.as_view(), name="rating-data"),
    path(
        "add-proctorship-feedback",
        ProctorFeedbackView.as_view(),
        name="proctorship-feedback",
    ),
    path(
        "add-proctorship-feedback/<int:pk>",
        ProctorFeedbackView.as_view(),
        name="proctorship-feedback",
    ),
    path(
        "add-trainee-feedback", TraineeFeedbackView.as_view(), name="trainee-feedback"
    ),
    path(
        "add-trainee-feedback/<int:pk>",
        TraineeFeedbackView.as_view(),
        name="trainee-feedback",
    ),
    path(
        "add-memo-proctor-feedback",
        MemoProctorFeedBackView.as_view(),
        name="memo-proctor-feedback",
    ),
    path(
        "add-memo-proctor-feedback/<int:pk>",
        MemoProctorFeedBackView.as_view(),
        name="memo-proctor-feedback",
    ),
    path(
        "add-solo-proctor-feedback",
        SoloSmartProctorFeedBackView.as_view(),
        name="solo-proctor-feedback",
    ),
    path(
        "add-solo-proctor-feedback/<int:pk>",
        SoloSmartProctorFeedBackView.as_view(),
        name="solo-proctor-feedback",
    ),
    path(
        "certificate-form-data",
        CertificateFormView.as_view(),
        name="certificate-form-data",
    ),
    path(
        "certificate-form-data/<int:pk>",
        CertificateFormView.as_view(),
        name="certificate-form-data",
    ),
]
