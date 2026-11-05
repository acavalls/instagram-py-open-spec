from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import (
    LoginSerializer,
    UserCreateSerializer,
    UserReadSerializer,
)
from apps.accounts.services import UserService
from apps.accounts.use_cases import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
    RegisterUserInput,
    RegisterUserUseCase,
)


class RegisterAPIView(APIView):
    permission_classes: list[type] = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = RegisterUserUseCase(user_service=UserService())
        input_dto = RegisterUserInput(**serializer.validated_data)
        output = use_case.execute(input_dto)

        if not output.success:
            return Response({"error": output.error}, status=status.HTTP_409_CONFLICT)

        user = UserService().get_by_id(output.user_id)  # type: ignore[arg-type]
        return Response(UserReadSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes: list[type] = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = AuthenticateUserUseCase(user_service=UserService())
        input_dto = AuthenticateUserInput(**serializer.validated_data)
        output = use_case.execute(input_dto)

        if not output.success:
            return Response(
                {"error": output.error}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(output.user)  # type: ignore
        return Response(
            {
                "user": UserReadSerializer(output.user).data,  # type: ignore[arg-type]
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
