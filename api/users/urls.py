from django.urls import path
from api.users.views import PasswordView, UserPaginationView, DeleteUsersView, UpdateUserFormView, \
    BlockedUnBlockedUsersView, UpdateProfile, LoginView, AddUserView, GetUserView, LocalAdminListingView, \
    SalesManagerListingView, SuperAdminListingView, ForgotPasswordView, ChangePasswordView, UserLogoutView


app_name ='users'


urlpatterns = [
	path('add-users', AddUserView.as_view(), name = 'add-users'),
    path('login', LoginView.as_view(), name='login'),

    path('update-profile', UpdateProfile.as_view(), name = 'update-profile'),
    
    path ('listing', GetUserView.as_view(), name = 'users-listing'),
    path ('listing/<int:pk>', GetUserView.as_view(), name = 'users-listing'),

    path ('local-admin-listing', LocalAdminListingView.as_view(), name = 'local-admin-listing'),

    path ('super-admin-listing', SuperAdminListingView.as_view(), name = 'super-admin-listing'),

    path ('sales-manager-listing', SalesManagerListingView.as_view(), name = 'sales-manager-listing'),

    path('blocked-unblocked-user/<int:pk>', BlockedUnBlockedUsersView.as_view(), name = 'blocked-unblocked-user'), 


    path('update-user-form', UpdateUserFormView.as_view(), name = 'updata-user-form'),
    path('update-user-form/<int:pk>', UpdateUserFormView.as_view(), name = 'updata-user-form'),

    path('delete-users/<int:pk>', DeleteUsersView.as_view(), name = 'delete-users'),

    path('users-listings', UserPaginationView.as_view(), name = "users-listings"),

    path('set-password', PasswordView.as_view(),name = 'set-password'),

    path("forgot-password", ForgotPasswordView.as_view(), name="users_forgot_password"),

    path("update-password", ChangePasswordView.as_view(), name = "update-user-password"),

    path("user-logout", UserLogoutView.as_view(), name= 'user logout')
]