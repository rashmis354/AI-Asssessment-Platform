import time
from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from modules.utils.generate_log_file import logger
from Personas.Evaluator.schema_class import SkillBasedAssessmentSchema
from modules.tasks.celery_tasks import openai_celery_task
from modules.openai.open_ai_helper_functions import create_openai_obj
from Personas.Evaluator.prompts import MCQS_SKILL_SYSTEM_PROMPT, MCQS_SKILL_USER_PROMPT, CODING_QUESTIONS_SKILL_SYSTEM_PROMPT, CODING_QUESTIONS_SKILL_USER_PROMPT

router = APIRouter(
    prefix="/evaluator",
    tags=["/evaluator"]
)


def generate_questions(stack_details):
    tasks = []
    open_ai_obj_list = []
    logger.info("---------Inside generate_questions()---------------")
    for domain in stack_details:
        logger.info(domain)
        mcq_open_ai_call = []
        coding_open_ai_call = []
        domain_name = domain.technology
        domain_complexity = domain.complexity
        mcqs = domain.questions.MCQ
        coding = domain.questions.Coding
        
        mcq_open_ai_call.append(create_openai_obj("system",MCQS_SKILL_SYSTEM_PROMPT))
        mcq_open_ai_call.append(create_openai_obj("user",MCQS_SKILL_USER_PROMPT.format(no_of_questions = mcqs, domain = domain_name, domain_complexity = domain_complexity)))
        open_ai_obj_list.append(mcq_open_ai_call)
        coding_open_ai_call.append(create_openai_obj("system",CODING_QUESTIONS_SKILL_SYSTEM_PROMPT))
        coding_open_ai_call.append(create_openai_obj("user",CODING_QUESTIONS_SKILL_USER_PROMPT.format(no_of_questions = coding, domain = domain_name, domain_complexity = domain_complexity)))
        open_ai_obj_list.append(coding_open_ai_call)
        start_time = time.time()
        for open_ai_obj in open_ai_obj_list:
            logger.info("Before implementing celery")
            logger.info(open_ai_obj)
            tasks.append(openai_celery_task.apply_async(args=(open_ai_obj,)))
    
    openai_results = []    
    for task in tasks:
        try :
            result = task.get()# This will block until the task completes
            openai_results.append(result)
        except Exception as e:
            logger.info("--------Error in task.get()---------")
            logger.info(str(e))
    end_time = time.time()
    elapsed_time = end_time-start_time
    logger.info(f"Time taken for celery implementation: {elapsed_time:.2f} seconds")        
    return openai_results
            
@router.post("/create-skill-based-assessment")
def skill_based_assessment(request: SkillBasedAssessmentSchema):
    try:  
        logger.info(request)
        logger.info("In /create-skill-based-assessment API")
        stack_details = request.stackDetails
        logger.info(stack_details)
        questions_generated = generate_questions(stack_details)
        logger.info("---------Generated Skill Based Questions--------")
        logger.info(questions_generated)
         
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
 