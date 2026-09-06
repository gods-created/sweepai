from fastapi import UploadFile

from os import remove
from os.path import join, exists
from sys import executable
from subprocess import run
from uuid import uuid4
from typing import Tuple

from config import TEMPORARY_FILES_STORE

class ExecuteFileService:
    def __init__(
        self,
        uploaded_file: UploadFile
    ):
        self._uploaded_file = uploaded_file

    async def _py_executor(self) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'output': None
        }

        uploaded_file = self._uploaded_file
        filename = None

        try:
            filename = join(TEMPORARY_FILES_STORE, f'{uuid4().hex}.py')
            content = await uploaded_file.read()

            with open(filename, mode='wb') as file:
                file.write(content)

            result = run(
                args=[executable, filename],
                check=True,
                text=True,
                capture_output=True
            )

            if result.returncode != 0:
                raise Exception(result.stderr or 'File couldn\'t to be executable')

            response['output'] = result.stdout
            response['status'] = True 

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if filename is not None and exists(filename):
                remove(filename)

        return response

    async def __call__(self) -> Tuple[bool, str]:
        EXECUTORS = {
            'py': self._py_executor
        }

        filename = str(self._uploaded_file.filename)
        extension = filename.split('.')[-1] 

        if not extension in EXECUTORS:
            return False, 'Unsupported file format'

        response = await EXECUTORS[extension]()

        if not response['status']:
            return False, response['err_description']

        return True, response['output']
