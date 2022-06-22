from django.views.generic.base import TemplateView


# Статичные страницы
class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
