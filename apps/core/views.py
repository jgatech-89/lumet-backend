from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_all_choices_for_api


class ChoicesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_all_choices_for_api()
        return Response(data)
