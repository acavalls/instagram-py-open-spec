from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostReadSerializer,
    PostUpdateSerializer,
)
from apps.posts.services import PostService
from apps.posts.use_cases import (
    CreatePostInput,
    CreatePostUseCase,
    DeletePostInput,
    DeletePostUseCase,
    GetPostInput,
    GetPostUseCase,
    ListPostsInput,
    ListPostsUseCase,
    UpdatePostInput,
    UpdatePostUseCase,
)


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        use_case = ListPostsUseCase(post_service=PostService())
        output = use_case.execute(
            ListPostsInput(user_id=request.user.id, limit=limit, offset=offset)
        )

        serializer = PostListSerializer(
            output.posts,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        media_files = []
        for idx, uploaded_file in enumerate(serializer.validated_data.get("media", [])):
            media_files.append(
                {
                    "file": uploaded_file,
                    "order": idx,
                }
            )

        use_case = CreatePostUseCase(post_service=PostService())
        output = use_case.execute(
            CreatePostInput(
                owner_id=request.user.id,
                caption=serializer.validated_data["caption"],
                media_files=media_files,
            )
        )

        if not output.success:
            return Response({"error": output.error}, status=status.HTTP_400_BAD_REQUEST)

        post = PostService.get_by_id(output.post_id)  # type: ignore[arg-type]
        return Response(
            PostReadSerializer(post, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: str) -> Response:
        use_case = GetPostUseCase(post_service=PostService())
        output = use_case.execute(GetPostInput(post_id=pk))  # type: ignore[arg-type]

        if not output.success:
            return Response({"error": output.error}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostReadSerializer(output.post, context={"request": request})
        return Response(serializer.data)

    def patch(self, request: Request, pk: str) -> Response:
        serializer = PostUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = UpdatePostUseCase(post_service=PostService())
        output = use_case.execute(
            UpdatePostInput(
                post_id=pk,  # type: ignore[arg-type]
                user_id=request.user.id,
                caption=serializer.validated_data["caption"],
            )
        )

        if not output.success:
            if "own" in (output.error or "").lower():
                status_code = status.HTTP_403_FORBIDDEN
            else:
                status_code = status.HTTP_404_NOT_FOUND
            return Response({"error": output.error}, status=status_code)

        post = PostService.get_by_id(output.post_id)  # type: ignore[arg-type]
        return Response(
            PostReadSerializer(post, context={"request": request}).data,
        )

    def delete(self, request: Request, pk: str) -> Response:
        use_case = DeletePostUseCase(post_service=PostService())
        output = use_case.execute(
            DeletePostInput(post_id=pk, user_id=request.user.id)  # type: ignore[arg-type]
        )

        if not output.success:
            if "own" in (output.error or "").lower():
                status_code = status.HTTP_403_FORBIDDEN
            else:
                status_code = status.HTTP_404_NOT_FOUND
            return Response({"error": output.error}, status=status_code)

        return Response(status=status.HTTP_204_NO_CONTENT)
