from django.urls import path, include

app_name = 'admin_api'

urlpatterns = [
    path('goods/', include('api.v1.admin.goods.urls')),
    path('tool/', include('api.v1.admin.tool.urls')),
    path('ingredient/', include('api.v1.admin.ingredient.urls')),
    path('recipe/', include('api.v1.admin.recipe.urls')),
    path('profile/', include('api.v1.admin.profile.urls')),
    path('point/', include('api.v1.admin.point.urls')),
    path('sup/', include('api.v1.admin.support.urls')),
    path('auth/', include('api.v1.admin.auth.urls')),
    path('referral/', include('api.v1.admin.referral.urls')),
    path('promo/', include('api.v1.admin.promo.urls')),
    path('ads/', include('api.v1.admin.ads.urls')),
    path('mailing/', include('api.v1.admin.mailing.urls')),
    path('FAQ/', include('api.v1.admin.faq.urls')),
    path('statistics/', include('api.v1.admin.statistics.urls')),
    path('permissions/', include('api.v1.admin.permissions.urls')),
]
