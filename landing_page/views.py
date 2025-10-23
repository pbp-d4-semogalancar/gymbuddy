from django.shortcuts import render

def landing_page_view(request):
    context = {}
    return render(request, 'pages/landing_page.html', context)