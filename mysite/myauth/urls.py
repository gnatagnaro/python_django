# from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    MyLoginView,
    MyLogoutView,
    # login_view,
    # logout_view,
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
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
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),

    path('cookie/get/', get_cookie_view, name='cookie-get'),
    path('cookie/set/', set_cookie_view, name='cookie-set'),

    path('session/get/', get_session_view, name='session-get'),
    path('session/set/', set_session_view, name='session-set'),
]
