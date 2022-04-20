from django.urls import include, path

from api.masterproctorship.views import (
    ApproveMasterProctorshipTraineeView,
    AttendanceFormMasterProctorshipView,
    InvoiceMasterProctorshipView,
    MasterProctorshipAddReportView,
    MasterProctorshipConstantDataView,
    MasterProctorshipFeedbackView,
    MasterProctorshipListingApiView,
    MasterProctorshipStatusView,
    MasterProctorshipTraineeProfileAddView,
    MasterProctorshipTraineeProfileView,
    MasterProctorshipView,
    MDateUpdateView,
    RevokeMasterProctorshipTraineeProfileView,
    StatusMTestingView,
)

app_name = "masterproctorship"


# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("", MasterProctorshipView.as_view(), name="master-proctorship"),
    path("<int:pk>", MasterProctorshipView.as_view(), name="master-proctorship-get-id"),
    path(
        "master-proctorship-constant-data",
        MasterProctorshipConstantDataView.as_view(),
        name="master-proctorship-constant-data",
    ),
    path(
        "master-proctorship-status-view",
        MasterProctorshipStatusView.as_view(),
        name="master-proctorship-status-view",
    ),
    path(
        "master-proctorship-approve-trainee/<int:pk>",
        ApproveMasterProctorshipTraineeView.as_view(),
        name="master-proctorship-approve-trainee",
    ),
    path(
        "master-proctorship-revoke-trainee/<int:pk>",
        RevokeMasterProctorshipTraineeProfileView.as_view(),
        name="master-proctorship-revoke-trainee",
    ),
    path(
        "master-proctorshi-trainee",
        MasterProctorshipTraineeProfileView.as_view(),
        name="master-proctorshi-trainee",
    ),
    path(
        "master-proctorship-add-report",
        MasterProctorshipAddReportView.as_view(),
        name="master-proctorship-add-report",
    ),
    path(
        "master-proctorship-add-report/<int:pk>",
        MasterProctorshipAddReportView.as_view(),
        name="mastermaster-proctorship-add-report",
    ),
    path(
        "master-proctorship-add-trainee",
        MasterProctorshipTraineeProfileAddView.as_view(),
        name="master-proctorship-add-trainee",
    ),
    path(
        "master-proctorship-add-trainee/<int:pk>",
        MasterProctorshipTraineeProfileAddView.as_view(),
        name="master-proctorship-add-trainee",
    ),
    path(
        "masterproctorship-feedback", MasterProctorshipFeedbackView.as_view(), name=""
    ),
    path(
        "masterproctorship-feedback/<int:pk>",
        MasterProctorshipFeedbackView.as_view(),
        name="",
    ),
    path("master-updat-date/<int:pk>", MDateUpdateView.as_view(), name="updat-date"),
    path(
        "master-proctorship-listing",
        MasterProctorshipListingApiView.as_view(),
        name="master-proctorship-listing",
    ),
    path(
        "masterproctorship-invoice-data",
        InvoiceMasterProctorshipView.as_view(),
        name="invoice-data",
    ),
    path(
        "masterproctorship-invoice-data/<int:pk>",
        InvoiceMasterProctorshipView.as_view(),
        name="invoice-data",
    ),
    path(
        "masterproctorship-attendance-form-data",
        AttendanceFormMasterProctorshipView.as_view(),
        name="attendance-form-data",
    ),
    path(
        "masterproctorship-attendance-form-data/<int:pk>",
        AttendanceFormMasterProctorshipView.as_view(),
        name="attendance-form-data",
    ),
    path(
        "masterproctorship-status-testing",
        StatusMTestingView.as_view(),
        name="masterproctorship-status-testing",
    ),
]
