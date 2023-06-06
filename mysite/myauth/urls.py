# from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    MyLoginView,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    # login_view,
    # logout_view,
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    FooBarView,
    UsersListView,
    UsersDetailView,
    UpdateProfileView,
    HelloView,
)

app_name = 'myauth'

urlpatterns = [
    # path('login/', login_view, name='login'),
    # path(
    #     'login/',
    #     LoginView.as_view(
    #         template_name='myauth/login.html',
    #         redirect_authenticated_user=True,
    #     ),
    #     name='login'
    # ),
    path('hello/', HelloView.as_view(), name='hello'),

    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about-me'),
    path('register/', RegisterView.as_view(), name='register'),

    path('cookie/get/', get_cookie_view, name='cookie-get'),
    path('cookie/set/', set_cookie_view, name='cookie-set'),

    path('session/get/', get_session_view, name='session-get'),
    path('session/set/', set_session_view, name='session-set'),

    path('foo-bar/', FooBarView.as_view(), name='foo-bar'),

    path('users/', UsersListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UsersDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UpdateProfileView.as_view(), name='update-profile'),
]
