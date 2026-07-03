from apps.settings.models import CompanySetting


def website_settings(request):
    settings = CompanySetting.objects.first()
    return {'company': settings}
