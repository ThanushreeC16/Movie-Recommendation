from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def movies_home():
    return {"message": "Movies route working"}