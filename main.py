from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import (
    DB_URL, TEMPORARY_FILES_STORE, 
    PERMANENT_FILES_STORE, OLLAMA_BASE_URL,
    OLLAMA_MODEL_NAME, TEMPLATE
)

from middlewares import IfEndpointNotExists
from exceptions import UnicornException
from routers import api_router
from services import InitAgentService

from loguru import logger

from os import makedirs
from os.path import exists

from uvicorn import run

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not exists(TEMPORARY_FILES_STORE):
        makedirs(TEMPORARY_FILES_STORE, exist_ok=True)

    if not exists(PERMANENT_FILES_STORE):
        makedirs(PERMANENT_FILES_STORE, exist_ok=True)

    try:
        if DB_URL is None:
            raise ValueError('\'DB_URL\' is not specified')

        if OLLAMA_BASE_URL is None:
            raise ValueError('\'OLLAMA_BASE_URLL\' is not specified')

        if OLLAMA_MODEL_NAME is None:
            raise ValueError('\'OLLAMA_MODEL_NAME\' is not specified')
        
        bind = create_engine(url=DB_URL, echo=False, pool_size=5)
        db_connection = Session(bind=bind)

        app.state.db_connection = db_connection
        logger.success('The connection with DB is established')

        service = InitAgentService(
            template=TEMPLATE,
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL_NAME,
            temperature=0.6
        )

        agent = service()

        app.state.agent = agent 
        logger.success('The AI agent is running')

        yield

        db_connection.close_all()

    except ValueError as e:
        logger.error(str(e))

    except Exception as e:
        logger.error(f'Unexpected error during service run: {str(e)}')

app = FastAPI(
    title='SweepAI',
    description='SweepAI - An AI agent that grades your students\' assignments without your involvement',
    version='0.0.1',
    redoc_url=None,
    lifespan=lifespan
)

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status,
        content={'status': False, 'err_description': exc.err_description},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'status': False, 'err_description': str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error = errors[0]
    msg = error.get('msg')

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'status': False, 'err_description': msg},
    )

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_headers=['*'],
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_origins=['*']
)

app.add_middleware(IfEndpointNotExists)

app.include_router(router=api_router, tags=['API'])

if __name__ == '__main__':
    run('main:app', host='0.0.0.0', port=8001, reload=True)