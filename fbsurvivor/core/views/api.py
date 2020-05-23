from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class Hello(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request):
        user = get_user_model().objects.get(id=request.user.id)
        data = {
            "user": user.username,
            "email": user.email,
        }
        return Response(data)
