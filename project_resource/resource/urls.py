from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from resource import views,fileCheck

router = DefaultRouter(trailing_slash=False)
router.register('device', views.DeviceListViewSet, basename='device'),
router.register('algorithm', views.AlgorithmListViewSet, basename='algorithm'),
router.register('policy', views.PolicyListViewSet, basename='policy'),
router.register('version', views.VersionListViewSet, basename='version')
router.register('get_configuration', views.ConfigFilesListViewSet, basename='get_configuration')
router.register('get_loadjson', views.LoadFilesListViewSet, basename='get_loadjson')
router.register('category', views.CategoryListViewSet, basename='category')
# router.register('login', views.LoginView, basename='login')

urlpatterns = [
    path('import',views.ImportConView.as_view()),
    path('load',views.LoadJsonView.as_view()),
    path('save',views.SaveJsonView.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view()),
    # path('save',views.SaveAsJsonView.as_view()),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)

urlpatterns += router.urls

