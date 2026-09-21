from fastapi import APIRouter
from pydantic import BaseModel
from src.external_sources.external_sources_utils import get_curated_library
from src.external_sources.models import LIBRARY


router = APIRouter()


@router.get('/api/library')
def get_library() -> LIBRARY:
    library = get_curated_library()
    return library
