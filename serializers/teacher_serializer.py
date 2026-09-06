from .base import BaseSerializer

from sqlalchemy import select as select_query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import Teacher

from typing import Optional

class TeacherSerializer(BaseSerializer):
    def __init__(self, db_connection: Session):
        super().__init__()
        self._db_connection = db_connection
        self._allowed_fields = [
            'email',
            'password',
            'fullname',
        ]

    def insert(self, **fields) -> dict:
        response = self._std_response_json

        try:
            validated_field = self._validate_fields(fields, Teacher, self._allowed_fields)
            teacher = Teacher(**validated_field)

            self._db_connection.add(teacher)
            self._db_connection.commit()
            self._db_connection.refresh(teacher)

            response['teacher'] = teacher
            response['status'] = True

        except IntegrityError as e:
            message = str(e)

            if 'unique' in message.lower():
                response['err_description'] = 'Teacher with so email already exists'
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

    def select(self, id: Optional[str | int] = None) -> dict:
        response = self._std_response_json

        try:
            stmt = select_query(Teacher)

            if id is None:
                stmt = stmt.filter_by(id=id)

            response['teachers'] = []
            for teacher in self._db_connection.scalars(stmt):
                response['teachers'].append(teacher)

            response['status'] = True 

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def update(self, item: Teacher, **fields) -> dict:
        response = self._std_response_json
        
        try:
            validated_field = self._validate_fields(fields, Teacher, self._allowed_fields)

            for field_name, field_value in validated_field.items():
                setattr(item, field_name, field_value)

            self._db_connection.commit()
            self._db_connection.refresh(item)

            response['teacher'] = item
            response['status'] = True

        except IntegrityError as e:
            message = str(e)

            if 'unique' in message.lower():
                response['err_description'] = 'Teacher with so email already exists'
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

    def delete(self, item: Teacher) -> dict:
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