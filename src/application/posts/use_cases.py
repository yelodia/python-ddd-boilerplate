from application.posts.commands import RequestPostCmd
from application.posts.external_tool_interface import ExternalToolApiClient, PostsResponseDTO
from application.use_case_base import UseCase


class GetPostsUseCase(UseCase):
    cmd = RequestPostCmd

    def __init__(self, client: ExternalToolApiClient):
        self.client = client

    async def execute(self, cmd: RequestPostCmd) -> tuple[int, PostsResponseDTO]:
        client_response = await self.client.get_posts(cmd.page, cmd.limit)
        return cmd.page, client_response
