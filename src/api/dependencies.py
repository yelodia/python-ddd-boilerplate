from fastapi import Depends

from common.use_case_base import UseCase
from infra.usecases_builder import UseCasesBuilder


def use_case_factory(use_case_class: type[UseCase]):
    async def dependency(
        builder: UseCasesBuilder = Depends(UseCasesBuilder),
    ) -> UseCase:
        return builder.get_use_case(use_case_class)
    return dependency

def build(use_case_class: type[UseCase]):
    return Depends(use_case_factory(use_case_class))
