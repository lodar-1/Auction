from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:formtype>", views.newlisting, name="newlisting"), 
    path("listing/<str:formtype>", views.newlisting, name="listing"),
    path("listing/<str:formtype>/<int:listingid>", views.newlisting, name="listing")
]
