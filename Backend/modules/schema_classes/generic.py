from pydantic import BaseModel
class RoleNotValid(Exception):
    def __init__(self, role: str):
        self.message = f"{role} is not a valid role."
        super().__init__(self.message)
        
class APIResponse:
    def __init__(self, status="", message="", data=None, uploadId = None):
        self.status = status
        self.message = message
        self.data = data 
        
class StatusCheck(BaseModel):
    assessment_id: str
    assessment_type: str