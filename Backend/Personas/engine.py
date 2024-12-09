from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from modules.schema_classes.generic import StatusCheck
from modules.utils.generate_log_file import logger

router = APIRouter(
    prefix="/engine",
    tags=["/engine"]
)

@router.post("/status")
async def status_check(request : StatusCheck):
    try:  
        logger.info(request)
        assessment_id = request.assessment_id
        assessment_type = request.assessment_type
        
        #Fetch results from DB related to assessment_id and assessment_type
        logger.info("---------Generation of Skill Based Questions started--------")

        result = {'status': "In Progress/Completed",
                  "message": "", "data": []}
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)

