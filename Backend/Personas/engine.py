from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from modules.schema_classes.generic import StatusCheck
from modules.utils.generate_log_file import logger

router = APIRouter(
    prefix="/engine",
    tags=["/engine"]
)



