from django.conf.urls import url


from otp_site import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^otp_generation/$',views.otp_generation,name='otp_generation'),
    url(r'^login/$',views.login,name='login'),
    url(r'^validation/$',views.validation,name='validation')


]
