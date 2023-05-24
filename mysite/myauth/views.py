from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy


# Create your views here.

class MyLoginView(LoginView):
    template_name = 'myauth/login.html'
    redirect_authenticated_user = True


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:logout')


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('myauth:login'))


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return redirect('/admin/')
    return render(request, 'myauth/login.html', {'error': 'Invalid username or password'})


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default_value')
    return HttpResponse(f'Cookie value: {value!r}')


def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default_value')
    return HttpResponse(f'Session value: {value!r}')
