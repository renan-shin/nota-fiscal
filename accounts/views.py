from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '')
        senha = request.POST.get('senha', '')

        user = auth.authenticate(request, username=usuario, password=senha)

        if not user:
            messages.error(request, 'Usuário e/ou senha inválidos')
            return render(request, 'accounts/login.html')

        auth.login(request, user)
        url_next = request.session['next']
        del(request.session['next'])

        return redirect(url_next)
    
    request.session['next'] = request.GET.get('next') or 'core_index'
    
    if not request.user.is_anonymous:
        return redirect(request.session['next'])

    return render(request, 'accounts/login.html')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('accounts_login')