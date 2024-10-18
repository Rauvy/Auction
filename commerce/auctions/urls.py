from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="new_listing"),
    path("listing/<int:listing_id>", views.display_listing, name="display_listing"),
    path("categories", views.categories_listing, name="categories_listing"),
    path("categories/<str:category>", views.listing_in_category, name="listing_in_category"),
    path('watchlist/', views.watchlist_page, name='watchlist_page'),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:listing_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
