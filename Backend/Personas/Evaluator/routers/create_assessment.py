import time
import json
import uuid
import hashlib
from datetime import datetime
from typing import List
from fastapi import APIRouter,status,BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from modules.utils.generate_log_file import logger
from modules.schema_classes.generic import APIResponse
from Personas.Evaluator.schema_class import SkillBasedAssessmentSchema, StatusCheck
from modules.tasks.celery_tasks import openai_celery_task
from modules.openai.open_ai_helper_functions import create_openai_obj
from modules.db.db_connectivity import DBConnection
from modules.db.db_operations import insert_into_azure_cosmos
from Personas.Evaluator.prompts import MCQS_SKILL_SYSTEM_PROMPT, MCQS_SKILL_USER_PROMPT, CODING_QUESTIONS_SKILL_SYSTEM_PROMPT, CODING_QUESTIONS_SKILL_USER_PROMPT

router = APIRouter(
    prefix="/evaluator",
    tags=["/evaluator"]
)

def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))

def generate_questions(assessment_id,assessment_type,total_questions,stack_details):
    tasks = []
    open_ai_obj_list = []
    logger.info(f"---------Inside generate_questions() for {assessment_id}---------------")
    total_questions_generated = 0
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
        db_conn = DBConnection()
        try :
            result = task.get()# This will block until the task completes
            openai_results.append(result)
            technology = result.get('domain_name')
            question_type = result.get('question_type')
            no_of_questions = result.get('no_of_questions')
            q_and_a = result.get('q_and_a')
            logger.info(q_and_a)
            logger.info(type(q_and_a))
            if question_type == "MCQ":
                logger.info("----------MCQ question type----------")
                query ='''UPDATE assessments
                        SET 
                            stack_details = jsonb_set(
                                stack_details,
                                '{0,generated_questions,MCQ}',
                                to_jsonb((stack_details->0->'generated_questions'->>'MCQ')::int + %s)
                            ),
                            q_and_a = q_and_a || %s::jsonb
                        WHERE 
                            assessment_id = %s
                            AND stack_details->0->>'technology' = %s;''',(no_of_questions, json.dumps(q_and_a),assessment_id,technology,)
            else:
                logger.info("----------Coding question type----------")
                query = '''UPDATE assessments
                        SET 
                            stack_details = jsonb_set(
                                stack_details,
                                '{0,generated_questions,Coding}',
                                to_jsonb((stack_details->0->'generated_questions'->>'Coding')::int + %s)
                            ),
                            q_and_a = q_and_a || %s::jsonb
                        WHERE 
                            assessment_id = %s
                            AND stack_details->0->>'technology' = %s;''',(no_of_questions, json.dumps(q_and_a),assessment_id,technology,)
            
            db_status, message, update_statement = db_conn.execute_query(query,"UPDATE")
            if not db_status:
                raise HTTPException(status_code=500, detail="Error while inserting into database")    
            
            #Update in the db with id,assessment_type and type of questions 
            
        except Exception as e:
            logger.info("--------Error in task.get()---------")
            logger.info(str(e))
        
        finally:
            db_conn.close_conn
            
    if total_questions_generated != total_questions:
        total_questions_generated = -1
        
    end_time = time.time()
    elapsed_time = end_time-start_time
    logger.info(f"Time taken for celery implementation: {elapsed_time:.2f} seconds")        
    # return openai_results
           
@router.post("/create-skill-based-assessment")
async def skill_based_assessment(request: SkillBasedAssessmentSchema,background_tasks: BackgroundTasks):
    db_conn = DBConnection()
    try:  

        logger.info(request)
        evaluator_id = request.evaluator_id
        assessment_type = "skill-based"
        logger.info("In /create-skill-based-assessment API")
        created_on = datetime.utcnow().isoformat("#", "microseconds")
        assessment_id = create_uuid_from_string( 
                str(evaluator_id)  
                + "-"  
                + str(created_on)  
            )  
        logger.info("Assessment ID : "+str(assessment_id))
        stack_details = request.stackDetails
        logger.info(stack_details)
        total_questions = {"MCQ" : 0,"Coding" : 0}
        mcqs=0
        coding=0
        stack_detail_list = []
        stack = {}
        for domain in stack_details:
            stack["technology"] = domain.technology
            stack["questions"] = {"MCQ" : int(domain.questions.MCQ),"Coding" : int(domain.questions.Coding)}
            stack["generated_questions"] = {"MCQ" : 0,"Coding" : 0}
            stack["complexity"] = domain.complexity
            stack_detail_list.append(stack)
            mcqs+=int(domain.questions.MCQ)
            coding+=int(domain.questions.Coding)
        total_questions["MCQ"] = mcqs
        total_questions["Coding"] = coding 
        logger.info(stack_detail_list)
        logger.info(total_questions)   
        updated_on = created_on
        
        query = "INSERT INTO assessments(assessment_id, evaluator_id, assessment_title, assessment_type, created_time,updated_time,total_questions,stack_details) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = (assessment_id, evaluator_id, request.assessment_title, assessment_type, created_on, updated_on,json.dumps(total_questions),json.dumps(stack_detail_list),)
        db_status, message, insert_statement = db_conn.execute_query(query,"INSERT", params)
        if not db_status:
            raise HTTPException(status_code=500, detail="Error while inserting into database")    
        # total_questions = stack_details['questions']['MCQ'] + stack_details['questions']['Coding']
        logger.info("---------Generation of Skill Based Questions started--------")
        background_tasks.add_task(generate_questions, assessment_id,assessment_type,total_questions,stack_details)
        result = {'status': "success",
                  "message": "Generation of QnA started", "data": assessment_id}
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)


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

