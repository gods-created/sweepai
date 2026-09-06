from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse

from models import Task
from exceptions import UnicornException
from serializers import TaskSerializer
from services import ExecuteFileService, ToEmbeddingsService, CompareEmbeddingsService

from langgraph.graph.state import CompiledStateGraph

from typing import Optional, Any

async def _if_db_connection_exists(request: Request) -> None:
    if not hasattr(request.app.state, 'db_connection'):
        raise UnicornException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description='The connection with DB does\'t established'
        )

async def _if_ai_agent_exists(request: Request) -> None:
    if not hasattr(request.app.state, 'agent'):
        raise UnicornException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description='The AI agent is not running'
        )

async def _if_task_exists(request: Request, task_id: str | int) -> None:
    db_connection = request.app.state.db_connection
    serializer = TaskSerializer(db_connection=db_connection)
    response = serializer.select(id=task_id)
    if not response['status']:
        raise UnicornException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description=response['err_description']
        )

    tasks = response['tasks']

    if not tasks:
        raise UnicornException(
            status=status.HTTP_404_NOT_FOUND, 
            err_description='Task doesn\'t exist'
        )

    task: Task = tasks[0]
    request.state.task = task

async def _receive_answer(
    request: Request, 
    answer_by_string: Optional[str] = None,
    answer_by_file: Optional[UploadFile] = None
) -> None:
    if not any((answer_by_string, answer_by_file)):
        raise UnicornException(
            status=status.HTTP_400_BAD_REQUEST, 
            err_description='One of the answer variants has to be specified'
        )

    answer = None

    if answer_by_string is not None:
        answer = answer_by_string

    elif answer_by_file is not None and answer_by_string is None:
        service = ExecuteFileService(uploaded_file=answer_by_file)
        response = await service()

        if not response[0]:
            raise UnicornException(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                err_description=response[1]
            )

        answer = response[1]

    request.state.answer = answer
    
def _receive_evaluate(from_student: Any, from_task: Any) -> dict:
    to_embeddings_service = ToEmbeddingsService(from_student, from_task)

    response = to_embeddings_service()

    if not response['status']:
        raise UnicornException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description=response['err_description']
        )

    compare_embeddings_service = CompareEmbeddingsService(
        embeddings=response['embeddings']
    )

    response = compare_embeddings_service()

    if not response['status']:
        raise UnicornException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description=response['err_description']
        )

    return response

router = APIRouter(
    prefix='/api',
    default_response_class=JSONResponse,
    dependencies=[Depends(_if_db_connection_exists), Depends(_if_ai_agent_exists)]
)

@router.post('/answer_evaluate', dependencies=[Depends(_if_task_exists), Depends(_receive_answer)])
async def answer_evaluate(
    request: Request,
    task_id: str | int,
    answer_by_string: Optional[str] = None,
    answer_by_file: Optional[UploadFile] = None,
) -> JSONResponse:    
    task: Task = request.state.task
    answer: str = request.state.answer

    if task.answer is None:
        raise UnicornException(
            status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            err_description='The task answer is None. Use \'check_solution\' endpoint'
        )

    response = _receive_evaluate(answer, task.answer)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'evaluate': response['evaluate']
        }
    )

@router.post('/check_solution', dependencies=[Depends(_if_task_exists)])
async def check_solution(
    request: Request,
    task_id: str | int,
    solution: UploadFile
) -> JSONResponse:    
    agent: CompiledStateGraph = request.app.state.agent
    task: Task = request.state.task

    content_in_bytes: bytes = await solution.read()
    content_in_str: str = content_in_bytes.decode('utf-8')

    response = _receive_evaluate(
        from_student=content_in_str,
        from_task=task.solution
    )

    evaluate = response['evaluate']

    invoke_response = agent.invoke({
        'messages': [
            (
                'human',
                f'''
                    Right task solution:

                    {task.solution}

                    Student solution:

                    {content_in_str}

                    Comparing mark:

                    {evaluate}

                    Create a personalized notification for the student.
                '''
            )
        ]
    })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'evaluate': evaluate,
            'notification': invoke_response['messages'][-1].content
        }
    )