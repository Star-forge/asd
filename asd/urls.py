"""asd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from asdrm import views
# REST
from django.contrib.auth.models import User
from rest_framework import routers

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # Открывать админку, если после адреса сайта идёт "admin/"
    url(r'^admin/', admin.site.urls),
    #url(r'^login2/$',views.user_login_view, name='login2'),
    # Просто адрес сайта это основное представление
    url(r'^$', views.asdrm_main, name='asdrm_main'),
    # Представление списка ранее выполненных диагностик
    url(r'^list/', views.asdrm_testsuite_list, name='asdrm_testsuite_list'),
    # Представление ранее выполненной диагностики
    url(r'^complete/(?P<pk>[0-9]+)/$', views.asdrm_testsuite_complete, name='asdrm_testsuite_complete'),
    url(r'^register/$', views.RegisterFormView.as_view(), name='register'),
    #url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url('^', include('django.contrib.auth.urls')),
    # REST
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

