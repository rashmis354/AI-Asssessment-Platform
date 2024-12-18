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

def is_duplicate(result, results_list):
    for res in results_list:
        if res['domain_name'] == result['domain_name'] and res['question_type'] == result['question_type']:
            return True
    return False

def generate_questions(assessment_id, assessment_type, total_questions, stack_details):
    try:
        tasks = []
        open_ai_obj_list = []
        logger.info(f"---------Inside generate_questions() for {assessment_id}---------------")
        
        for domain in stack_details:
            logger.info("Current domain details:")
            logger.info(domain)
            #Add a new key in every item of stack_details
            domain["q_and_a"] = []
            mcq_open_ai_call = []
            coding_open_ai_call = []
            domain_name = domain["technology"]
            domain_complexity = domain['complexity']
            mcqs = domain["questions"]["MCQ"]
            coding = domain["questions"]["Coding"]
            
            # Prompt prep for MCQs
            mcq_open_ai_call.append(create_openai_obj("system", MCQS_SKILL_SYSTEM_PROMPT))
            mcq_open_ai_call.append(create_openai_obj("user", MCQS_SKILL_USER_PROMPT.format(no_of_questions=mcqs, domain=domain_name, domain_complexity=domain_complexity)))
            open_ai_obj_list.append(mcq_open_ai_call)

            # Prompt prep for coding
            coding_open_ai_call.append(create_openai_obj("system", CODING_QUESTIONS_SKILL_SYSTEM_PROMPT))
            coding_open_ai_call.append(create_openai_obj("user", CODING_QUESTIONS_SKILL_USER_PROMPT.format(no_of_questions=coding, domain=domain_name, domain_complexity=domain_complexity)))
            open_ai_obj_list.append(coding_open_ai_call)
            start_time = time.time()

            # Scheduling LLM calls as tasks
            for open_ai_obj in open_ai_obj_list:
                logger.info("Before celery task begins, ")
                logger.info(open_ai_obj)
                tasks.append(openai_celery_task.apply_async(args=(open_ai_obj,)))
        
        openai_results = []   
        total_questions_generated = {"MCQ": 0, "Coding": 0}
        
        for task in tasks:
            db_conn = DBConnection()
            try:
                result = task.get()  # This will block until the task completes
                logger.info("Before checking duplicstion")
                logger.info(result)
                
                if not is_duplicate(result, openai_results):
                    openai_results.append(result)
                    no_of_questions = result.get('no_of_questions')
                    question_type = result.get('question_type')
                    logger.info(f"Q and A for {result.get('domain_name')} and {result.get('question_type')}  --- {no_of_questions}")

                    q_and_a = result.get('q_and_a')
                    logger.info(q_and_a)
                    logger.info(type(q_and_a))
                    q_and_a_json = json.dumps(q_and_a)
                    logger.info(type(q_and_a_json))
                    for domain in stack_details:
                        if domain["technology"] == result.get('domain_name'):
                            domain["q_and_a"].append(q_and_a)
                            
                    if question_type == 'MCQ':
                        total_questions_generated['MCQ'] += no_of_questions
                    else:
                        total_questions_generated['Coding'] += no_of_questions 

                    logger.info(f"Updating {total_questions_generated} in db for {result.get('domain_name')}")        
                    
                    query = '''
                        UPDATE assessment_details 
                        SET total_questions_generated = %s, 
                            stack_details = %s 
                        WHERE assessment_id = %s
                    ''', (json.dumps(total_questions_generated), json.dumps(stack_details), assessment_id,)
                    db_status, message, update_statement = db_conn.execute_query(query, "UPDATE")
                    logger.info(message)
                    if not db_status:
                        logger.info("--------Error while updating 'total_questions_generated'---------'")
                        raise HTTPException(status_code=500, detail="Error while updating database")
                
            except Exception as e:
                logger.info("--------Error in task.get()---------")
                logger.info(str(e))     
                
        logger.info("Total OpenAI results")
        logger.info(openai_results)

        total = total_questions['MCQ'] + total_questions['Coding'] 
        logger.info("Total questions")
        logger.info(total)

        total_generated = total_questions_generated['MCQ'] + total_questions_generated['Coding'] 

        if total_generated != total:
            logger.info("total_questions_generated till now")
            logger.info(total_generated)
            total_questions_generated = {"MCQ": 0, "Coding": 0}
        
        query = '''
            UPDATE assessment_details 
            SET total_questions_generated = %s,stack_details = %s 
            WHERE assessment_id = %s
        ''', (json.dumps(total_questions_generated),json.dumps(stack_details), assessment_id,)
        db_status, message, update_statement = db_conn.execute_query(query, "UPDATE")
        if not db_status:
            raise HTTPException(status_code=500, detail="Error while updating database")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for celery implementation: {elapsed_time:.2f} seconds")  
        
    except Exception as e:
        logger.info(str(e))   
        raise HTTPException(status_code=500, detail="Error while generating q_and_a")
    finally:
        db_conn.close_conn  

           
@router.post("/create-skill-based-assessment")
async def skill_based_assessment(request: SkillBasedAssessmentSchema,background_tasks: BackgroundTasks):
    db_conn = DBConnection()
    try:
        logger.info("In /create-skill-based-assessment API")
        logger.info(request)
        evaluator_id = request.evaluator_id
        assessment_type = "skill-based"
        created_on = datetime.utcnow().isoformat("#", "microseconds")
        assessment_id = create_uuid_from_string( 
                str(evaluator_id)  
                + "-"  
                + str(created_on)  
            )  
        logger.info("Assessment ID : "+str(assessment_id))
        stack_details = request.stackDetails
        total_questions = {"MCQ" : 0,"Coding" : 0}
        mcqs=0
        coding=0
        stack_detail_list = []
        
        logger.info(stack_details)
        
        for domain in stack_details:
            stack = {}
            stack["technology"] = domain.technology
            stack["questions"] = {"MCQ" : int(domain.questions.MCQ),"Coding" : int(domain.questions.Coding)}
            stack["complexity"] = domain.complexity
            logger.info("Stack:")
            logger.info(stack)
            stack_detail_list.append(stack)
            mcqs+=int(domain.questions.MCQ)
            coding+=int(domain.questions.Coding)

        logger.info("List of stacks:")
        logger.info(stack_detail_list)
        total_questions["MCQ"] = mcqs
        total_questions["Coding"] = coding 
        
        logger.info("Total questions: " + str(total_questions))   
        updated_on = created_on

        # query = "INSERT INTO assessment_details(assessment_id, evaluator_id, assessment_title, assessment_type, created_on,updated_on,total_questions, q_and_a, stack_details) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        query = "INSERT INTO assessment_details(assessment_id, evaluator_id, assessment_title, assessment_type, created_on,updated_on,total_questions, q_and_a, stack_details,test) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        params = (assessment_id, evaluator_id, request.assessment_title, assessment_type, created_on, updated_on,json.dumps(total_questions),json.dumps({}),json.dumps(stack_detail_list),json.dumps(stack_detail_list))
        db_status, message, insert_statement = db_conn.execute_query(query,"INSERT", params)
        logger.info(message)
        if not db_status:
            raise HTTPException(status_code=500, detail="Error while inserting into database")    
        # total_questions = stack_details['questions']['MCQ'] + stack_details['questions']['Coding']

        logger.info("---------Generation of Skill Based Questions started--------")
        background_tasks.add_task(generate_questions, assessment_id,assessment_type,total_questions,stack_detail_list)
        result = {'status': "success",
                  "message": "Generation of QnA started", "data": assessment_id}
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
    
    finally:
        db_conn.close_conn


@router.post("/status")
async def status_check(request : StatusCheck):
    try:  
        logger.info("-----------In /status API------------")
        logger.info(request)
        assessment_id = request.assessment_id
        assessment_type = request.assessment_type
        db_conn = DBConnection()
        query = '''SELECT total_questions,total_questions_generated FROM assessment_details WHERE assessment_id = %s''',(assessment_id,)
        db_status, message, query_results = db_conn.execute_query(query,"SELECT")
        if not db_status:
            raise HTTPException(status_code=500, detail="Error while fetching data from database")
        logger.info(query_results)
        total_questions_generated = query_results[0]["total_questions_generated"]
        total_generated = total_questions_generated['MCQ'] + total_questions_generated['Coding']
        total_questions = query_results[0]["total_questions"]
        total = total_questions['MCQ'] + total_questions['Coding']
        
        total_questions = query_results[0]["total_questions"]
        
        #If error occured while sending JSON response check for the validity of format of 'total_questions_generated' in data
        if total_generated == 0:
            result = {'status': "Error Occured",
                "message": "Empty JSON", "data": []}
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        
        elif total_generated == total:
            result = {'status': "Completed",
                    "message": "Generation of Q and A Completed", "data": total_questions_generated}
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        
        elif total_generated != total:
            result = {'status': "In-Progress",
                    "message": "Generation of Q and A In-Progress", "data": total_questions_generated}
            return JSONResponse(status_code=status.HTTP_200_OK, content=result)
        else:
            result = {'status': "Error Occured",
                "message": "Error occured", "data": []}
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
    
    except Exception as e:
        logger.exception("Error while creating skill based application " + str(e))
        result = {'status': "failed",
                  "message": "Something went wrong. Please try again later.", "data": []}
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=result)
    
    finally:
        db_conn.close_conn

