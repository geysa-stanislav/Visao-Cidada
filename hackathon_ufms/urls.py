from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
# IMPORTAÇÕES DA MÍDIA:
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('painel.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='painel/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='/'), name='logout_direto'),
]

# ESTA É A LINHA QUE CONFIGURA O DJANGO PARA MOSTRAR AS IMAGENS DO CARROSSEL E DOS PARCEIROS
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)