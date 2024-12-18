from fastapi import APIRouter,status,HTTPException
from fastapi.responses import JSONResponse
from modules.utils.generate_log_file import logger
from Personas.Evaluator.schema_class import EvaluatorDashbosardSchema
from modules.db.db_connectivity import DBConnection
from modules.db.db_operations import insert_into_azure_cosmos

router = APIRouter(
    prefix="/evaluator",
    tags=["/evaluator"]
)
def calculate_progress(assessment):
    total_questions_generated = assessment["total_questions_generated"]
    total_generated = total_questions_generated['MCQ'] + total_questions_generated['Coding']
    total_questions = assessment["total_questions"]
    total = total_questions['MCQ'] + total_questions['Coding']
    
    if total_generated == 0:
        return "Error Occured"
    elif total_generated == total:
        return "Completed" 
    elif total_generated != total:
        return "In-Progress"
    else:
        return "Error Occured"

def get_constructed_result(assessments_list):
    logger.info("In get_constructed_result()")
    formated_result = []
    for assessment in assessments_list:
        result_json = {}
        result_json["assessment_id"] = assessment["assessment_id"]
        result_json["assessment_title"] = assessment["assessment_title"]
        result_json["assessment_type"] = assessment["assessment_type"]
        result_json["created_on"] = assessment["created_on"]
        result_json["updated_on"] = assessment["updated_on"]
        result_json["stacks"] = [item['technology'] for item in assessment["stack_details"]]
        result_json["progress"] = calculate_progress(assessment)
        formated_result.append(result_json)
        
    logger.info(formated_result)
    return formated_result

def get_evaluator_assessments_by_id(evaluator_id):
    logger.info("In get_evaluator_assessments_by_id()")
    db_conn = DBConnection()
    query = '''SELECT assessment_id,assessment_title,assessment_type,created_on,updated_on,stack_details,total_questions,total_questions_generated FROM assessment_details WHERE evaluator_id = %s''',(evaluator_id,)
    db_status, message, query_results = db_conn.execute_query(query,"SELECT")
    logger.info(message)
    if not db_status:
        raise HTTPException(status_code=500, detail="Error while fetching assessment de from database")
    
    logger.info(query_results)
    final_result = get_constructed_result(query_results)
    return final_result
    
    
    
@router.post("/manage-assessment")
async def evaluator_dashboard(request: EvaluatorDashbosardSchema):
    db_conn = DBConnection()
    try:
        logger.info("In /Evaluator /manage-assessment API")
        logger.info(request)
        evaluator_id = request.evaluator_id
        evaluator_assessments = get_evaluator_assessments_by_id(evaluator_id)
        result = {'status': "success",
                  "message": "Fetched evaluator's assessment details successfuly.", "data": evaluator_assessments}
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
    
    finally:
        db_conn.close_conn

