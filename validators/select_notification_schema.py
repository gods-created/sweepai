from pydantic import BaseModel, Field

class SelectNotificationSchema(BaseModel):
    from_task: str = Field(description='Th real solution from the task created by teacher')
    from_student: str = Field(description='The solution from student')
    evaluate: float = Field(description='The comparing mark of real solution and student solution')