from django.shortcuts import render

def about(request):
    return render(request, 'core/about.html')

def contact_us(request):
    return render(request, 'core/contact.html')