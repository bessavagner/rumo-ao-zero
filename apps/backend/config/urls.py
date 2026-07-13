"""Rotas do projeto: admin, API (router DRF), auth/token e docs OpenAPI."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from config.spa_views import SpaView

from apps.backlog.views import (
    BacklogItemViewSet,
    CompraViewSet,
    ConsultaViewSet,
    DecisionViewSet,
)
from apps.baseline.views import (
    BaselineProfileViewSet,
    IfThenPlanViewSet,
    SubstitutionViewSet,
    TaxonomiaEstadosView,
    TaxonomiaGatilhosView,
    TaxonomiaSubstituicoesView,
    ValueViewSet,
)
from apps.log.metrics_views import DashboardView, HumorSeriesView
from apps.log.views import CravingEventViewSet, DailyEntryViewSet, PulsoViewSet, SlipViewSet

router = DefaultRouter()
# log (graváveis — alvo da ingestão de transcrições)
router.register("log/daily", DailyEntryViewSet)
router.register("log/cravings", CravingEventViewSet)
router.register("log/slips", SlipViewSet)
router.register("log/pulsos", PulsoViewSet)
# baseline (Dia 0 + bibliotecas)
router.register("baseline/profile", BaselineProfileViewSet)
router.register("baseline/values", ValueViewSet)
router.register("baseline/substitutions", SubstitutionViewSet)
router.register("baseline/ifthen", IfThenPlanViewSet)
# backlog (preenchido pelo assistente)
router.register("backlog/items", BacklogItemViewSet)
router.register("backlog/decisions", DecisionViewSet)
router.register("backlog/consultas", ConsultaViewSet)
router.register("backlog/compras", CompraViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/series/humor/", HumorSeriesView.as_view(), name="series-humor"),
    path("api/taxonomia/gatilhos/", TaxonomiaGatilhosView.as_view(), name="taxonomia-gatilhos"),
    path("api/taxonomia/estados/", TaxonomiaEstadosView.as_view(), name="taxonomia-estados"),
    path("api/taxonomia/substituicoes/", TaxonomiaSubstituicoesView.as_view(), name="taxonomia-substituicoes"),
    path("api/auth/", include("rest_framework.urls")),  # login da browsable API
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("", SpaView.as_view(), name="spa"),
]
