"""Utilidades compartilhadas entre os apps da API."""

from rest_framework import permissions, viewsets


class OwnedModelViewSet(viewsets.ModelViewSet):
    """ViewSet que escopa tudo ao usuário autenticado.

    Filtra o queryset por ``request.user`` e injeta o ``user`` no create. Mantém o
    código pronto para multi-user sem expor ``user`` no payload da API.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
