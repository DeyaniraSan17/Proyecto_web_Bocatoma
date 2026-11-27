from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('members/', include('members.urls')),
    path('bocatoma/', include('bocatoma.urls')),
    path('', RedirectView.as_view(pattern_name='bocatoma:inicio', permanent=False)),
]
