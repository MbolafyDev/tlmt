from django.shortcuts import render

def apropos_view(request):
    return render(request, 'apropos/apropos.html')
