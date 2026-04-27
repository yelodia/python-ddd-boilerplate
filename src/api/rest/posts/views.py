from fastapi import APIRouter

from api.dependencies import build
from api.rest.posts.responses import PostsResponse, Post
from application.posts.use_cases import GetPostsUseCase

posts_router = APIRouter(prefix="/posts", tags=["posts"])


@posts_router.get("/", response_model=PostsResponse)
async def show_few_posts(
        page: int = 1,
        limit: int = 20,
        use_case: GetPostsUseCase = build(GetPostsUseCase),
) -> PostsResponse:
    cmd = use_case.cmd(page=page, limit=limit)
    current_page, client_response = await use_case.execute(cmd)

    return PostsResponse(
        page=current_page,
        per_page=cmd.limit,
        total=client_response.total,
        posts=[Post.model_validate(x, from_attributes=True) for x in client_response.posts],
    )
