from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Loja pública na raiz do domínio.
    path("", include("loja.urls")),
    # Mantém os endereços antigos durante a transição.
    path("loja/", include("loja.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
