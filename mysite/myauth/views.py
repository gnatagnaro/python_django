from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView

from .models import Profile


class AboutMeView(TemplateView):
    template_name = 'myauth/about-me.html'


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(self.object)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


class MyLoginView(LoginView):
    template_name = 'myauth/login.html'
    redirect_authenticated_user = True


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


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


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


@login_required
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default_value')
    return HttpResponse(f'Cookie value: {value!r}')


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default_value')
    return HttpResponse(f'Session value: {value!r}')
