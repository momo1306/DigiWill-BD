from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import EmailTokenSerializer, RegisterSerializer, UserSerializer


def tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    """Create an account and sign the user in straight away (returns tokens)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, **tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Email + password -> access/refresh tokens + user profile."""

    serializer_class = EmailTokenSerializer
    throttle_scope = "auth"


class LogoutView(APIView):
    """Blacklist the refresh token so it can't be used again."""

    def post(self, request):
        token = request.data.get("refresh")
        if token:
            try:
                RefreshToken(token).blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """The signed-in user's own profile (read + edit name/phone/language)."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user