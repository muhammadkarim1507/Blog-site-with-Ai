from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, UserUpdateForm


class RegisterView(View):
    """Ro'yxatdan o'tish"""
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('post_list')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Signal avtomatik Profile yaratadi!
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}! Akkauntingiz yaratildi.")
            return redirect('hpost_list e')
        else:
            messages.error(request, "Xatolik yuz berdi. Iltimos tekshiring.")
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """Tizimga kirish"""
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('post_list')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}!")

            # next parametr bo'lsa shu sahifaga yo'naltirish
            next_url = request.GET.get('next', 'post_list')
            return redirect(next_url)
        else:
            messages.error(request, "Username yoki parol noto'g'ri!")
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """Tizimdan chiqish"""
    def post(self, request):
        logout(request)
        messages.info(request, "Tizimdan chiqdingiz.")
        return redirect('login')


@login_required
def profile_view(request):
    """Profil ko'rish va tahrirlash"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profilingiz yangilandi!")
            return redirect('profile')
        else:
            messages.error(request, "Xatolik yuz berdi.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)


def home_view(request):
    """Bosh sahifa (keyinchalik blog postlari bo'ladi)"""
    return render(request, 'home.html')