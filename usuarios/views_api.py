from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, serializers
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework.permissions import IsAuthenticated
from usuarios.validaciones_movil import validar_rol_para_api
from rest_framework.exceptions import APIException
from django.contrib.auth import authenticate
# Excepción personalizada para devolver un mensaje con estructura clara
class CustomLoginRoleException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"error": "Su rol debe ingresar desde la web"}
    default_code = "invalid_login"

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError({"error": "Se requieren todos los campos"})

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError({"error": "Credenciales incorrectas"})

        if not validar_rol_para_api(user):
            raise serializers.ValidationError({"error": "Su rol debe ingresar desde la web"})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Usuario inactivo"})

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return {
            "refresh": str(refresh),
            "access": access,
            "user": UsuarioSerializer(user).data
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_actual(request):
    usuario = request.user
    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data)
