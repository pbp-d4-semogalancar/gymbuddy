from django.shortcuts import render

# Requirement #2, #3, #4
def landing_page_view(request):
    context = {}
    return render(request, 'pages/landing_page.html', context)