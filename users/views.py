from django.contrib.auth import logout
from django.views.generic import CreateView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import User

from .forms import (
    UserLoginForm,
    UserProfileForm, 
    CompanyForm, 
    UserRegistrationForm
)

from django.views.generic import (
    CreateView, 
    UpdateView, 
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin
)

from django.contrib.auth.views import (
    LoginView, 
    LogoutView
)


class RegisterCompanyView(CreateView):
    """Сторінка реєстрації компанії та її адміністратора."""

    template_name = 'users/register_company.html'
    form_class = CompanyForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)
    

class RegisterUserView(CreateView):
    """Сторінка реєстрації користувача."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register_user.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        return super().form_valid(form)


class UserLoginView(LoginView):
    """Сторінка входу до системи."""
    template_name = 'users/login.html'
    authentication_form = UserLoginForm


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Редагування профілю поточного користувача."""

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user
    

class UserLogoutView(LogoutView):
    """Вихід користувача з системи."""
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ProfileDeleteView(LoginRequiredMixin, View):
    """Повне видалення користувача."""
    
    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            user.delete()
            logout(request)
            return redirect('login')
        
        except Exception as e:
            return redirect('profile')
    