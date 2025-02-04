from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

# Videresender til Swagger dokumentasjonsiden
@router.get("/", include_in_schema=False)
async def redirect_main() -> RedirectResponse:
    return RedirectResponse(url="/docs")