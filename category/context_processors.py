from .models import Category

def menu_links(request):
    """Bring all the list of categories and save it to the variable "link", so we can use it everywhere we want"""
    links = Category.objects.all()
    return dict(links=links)