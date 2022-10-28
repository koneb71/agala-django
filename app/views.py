from django.shortcuts import render


def index(request):
    context = {
        "breadcrumb":
            {
                "parent": "Color Version", "child": "Layout Light"
            }
    }
    return render(request, 'app/index.html',context)
