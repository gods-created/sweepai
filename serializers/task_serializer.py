from .base import BaseSerializer

from sqlalchemy import select as select_query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import Task

from typing import Optional

class TaskSerializer(BaseSerializer):
    def __init__(
        self,
        db_connection: Session
    ):
        super().__init__()
        self._db_connection = db_connection
        self._allowed_fields = [
            'subject_id',
            'title', 
            'description', 
            'solution',
            'answer'
        ]

    def insert(self, **fields) -> dict:
        response = self._std_response_json.copy()

        try:
            validated_fields = self._validate_fields(
                fields=fields,
                model=Task,
                allowed_fields=self._allowed_fields
            )

            task = Task(**validated_fields)
            self._db_connection.add(task)
            self._db_connection.commit()
            self._db_connection.refresh(task)

            response['task'] = task
            response['status'] = True 

        except IntegrityError as e:
            message = str(e)

            if 'unique' in message.lower():
                response['err_description'] = 'The similar task is already existing'
            else:
                response['err_description'] = message

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def select(self, id: Optional[int | str] = None) -> dict:
        response = self._std_response_json.copy()
        
        try:
            stmt = select_query(Task)
            if id is not None:
                stmt = stmt.filter_by(id=id)

            response['tasks'] = []
            for task in self._db_connection.scalars(stmt):
                response['tasks'].append(task)

            response['status'] = True 

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def update(self, item: Task, **fields) -> dict:
        response = self._std_response_json.copy()
        
        try:
            validated_fields = self._validate_fields(
                fields=fields,
                model=Task,
                allowed_fields=self._allowed_fields
            )

            for field_name, field_value, in validated_fields.items():
                setattr(item, field_name, field_value)

            self._db_connection.commit()
            self._db_connection.refresh(item)

            response['task'] = item
            response['status'] = True 

        except IntegrityError as e:
            message = str(e)

            if 'unique' in message.lower():
                response['err_description'] = 'The similar task is already existing'
            else:
                response['err_description'] = message

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def delete(self, item: Task) -> dict:
        response = self._std_response_json.copy()
                
        try:
            self._db_connection.delete(item)
            self._db_connection.commit()

            response['status'] = True 

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response