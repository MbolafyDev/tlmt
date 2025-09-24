from .models import Categorie

def categories(request):
    return {
        "categories_menu": Categorie.objects.all()
    }
