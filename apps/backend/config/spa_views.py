"""Serve o index.html do build do SPA Svelte (assets vêm do WhiteNoise em /static/spa/)."""

from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View


class SpaView(View):
    def get(self, request):
        index = Path(settings.BASE_DIR) / "frontend" / "dist" / "index.html"
        if not index.exists():
            return HttpResponseNotFound("SPA não buildado. Rode: cd frontend && npm run build")
        return HttpResponse(index.read_text(encoding="utf-8"))
