from pydantic import BaseModel,Field
from typing import List,Optional,Literal

class QuestionType(BaseModel):
    MCQ: int
    Coding: int

class Technologies(BaseModel):
    technology_name: str
    
class stackDetails(BaseModel):
    technology: str
    questions: QuestionType
    complexity:  Literal['Beginner', 'Intermediate', 'Complex', 'Advanced'] = Field(..., description="Complexity level of the assessment")
    
class SkillBasedAssessmentSchema(BaseModel):
    evaluator_id: str
    assessment_title: str
    selectedStacks: List[str]
    stackDetails: List[stackDetails]