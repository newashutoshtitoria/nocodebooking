from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login(request):
    print("777777777777777777777777777777777777")

    context = {
    }
    template = 'publiclanding/login.html'
    return render(request, template, context)