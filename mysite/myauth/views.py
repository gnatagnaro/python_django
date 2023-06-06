from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, View, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import AvatarForm
from .models import Profile, User


class AboutMeView(LoginRequiredMixin, UpdateView):
    template_name = 'myauth/about-me.html'
    form_class = AvatarForm
    model = Profile
    success_url = reverse_lazy('myauth:about-me')
    context_object_name = 'profile'

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     profile = self.get_object()
    #     context['profile'] = profile
    #     return context

    def form_valid(self, form):
        profile = self.get_object()
        profile.avatar = form.cleaned_data['avatar']
        profile.save()
        return super().form_valid(form)


class UsersListView(LoginRequiredMixin, ListView):
    template_name = 'myauth/user_list.html'
    model = User
    context_object_name = 'users'


class UsersDetailView(LoginRequiredMixin, DetailView):
    template_name = 'myauth/user_detail.html'
    model = User
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('user-details', kwargs={'pk': self.kwargs['pk']})


class UpdateProfileView(UserPassesTestMixin, UpdateView):
    template_name = 'myauth/update_profile.html'
    model = Profile
    form_class = AvatarForm
    success_url = reverse_lazy('myauth:about-me')

    # def get_success_url(self):
    #     return reverse('myauth:user-detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        user = self.request.user
        return self.request.user.is_staff or user == self.request.user

    def get_object(self, queryset=None):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile
    # def form_valid(self, form):
    #     profile = self.request.user
    #     profile.avatar = form.cleaned_data['avatar']
    #     profile.save()
    #     return super().form_valid(form)


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


# @login_required
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


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': "eggs"})
