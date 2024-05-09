"""
URL configuration for wrs_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from wrs_api import views
from wrs_api import seed_functions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('seed-summoner-overviews/', seed_functions.seed_summoner_overviews),
    path('seed-summoner-matches/', seed_functions.seed_summoner_matches),
    path('summoner/', views.get_summoner),
    path('ladder/', views.get_ranked_ladder),
    path('testing/', views.testing)
    # path('summoner-update/', views.get_summoner_update),
    # path('match-history/', views.get_match_history),
    # path('test-dup-match/', seed_functions.test_repeat_match),
    # path('test-all-matches/', views.test_all_matches),
    # path('test/', views.xxx),
    # # path('summoner-data-external/', views.get_summoner_details_from_riot),
    # # path('match-history/', views.get_more_match_details_from_riot),
    # # path('get-one/', views.get_one_game),
    # path('get-timeline/', views.get_one_timeline)
]
