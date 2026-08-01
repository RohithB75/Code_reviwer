from fastapi import APIRouter

from app.api.v1.routes.diagnostics import router as diagnostics_router
from app.api.v1.routes.documentation import router as documentation_router
from app.api.v1.routes.llm import router as llm_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.performance import router as performance_router
from app.api.v1.routes.report import router as report_router
from app.api.v1.routes.refactoring import router as refactoring_router
from app.api.v1.routes.security import router as security_router
from app.api.v1.routes.review import router as review_router
from app.api.v1.routes.unit_tests import router as unit_tests_router


def create_v1_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router)
    router.include_router(diagnostics_router)
    router.include_router(llm_router)
    router.include_router(review_router)
    router.include_router(security_router)
    router.include_router(performance_router)
    router.include_router(refactoring_router)
    router.include_router(unit_tests_router)
    router.include_router(documentation_router)
    router.include_router(report_router)
    return router