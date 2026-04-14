from django.shortcuts import redirect

def home(request):
    """Legacy /home/ route redirect."""
    return redirect('home')
