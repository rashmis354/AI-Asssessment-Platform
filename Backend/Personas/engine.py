from fastapi import APIRouter,status, HTTPException
from fastapi.responses import JSONResponse
from modules.schema_classes.generic import QnA
from modules.utils.generate_log_file import logger
from modules.db.db_connectivity import DBConnection

router = APIRouter(
    prefix="/engine",
    tags=["/engine"]
)

# @rashmi: Test this API - @tezu: Tested and working <3
@router.post("/preview")
async def status_check(request : QnA):
    try:  
        logger.info("-----------In /status API------------")
        logger.info(request)
        assessment_id = request.assessment_id
        
        db_conn = DBConnection()
        query = '''SELECT stack_details FROM assessment_details WHERE assessment_id = %s''',(assessment_id,)
        db_status, message, query_results = db_conn.execute_query(query,"SELECT")
        if not db_status:
            raise HTTPException(status_code=500, detail="Error while fetching data from database")
        logger.info("Query Results")
        logger.info(query_results)
        generated_q_and_a = query_results[0]["stack_details"]
        logger.info("Q&A  :"+str(generated_q_and_a))
        result = {'status': "success",
                "message": "Generated Q and A", "data": generated_q_and_a} #Send in progress or Completed}
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
    
    finally:
        db_conn.close_conn



