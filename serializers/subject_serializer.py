from .base import BaseSerializer

from sqlalchemy import select as select_query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import Subject

from typing import Optional

class SubjectSerializer(BaseSerializer):
    def __init__(self, db_connection: Session):
        super().__init__()
        self._db_connection = db_connection
        self._allowed_fields = [
            'teacher_id',
            'title'
        ]

    def insert(self, **fields) -> dict:
        response = self._std_response_json

        try:
            validated_field = self._validate_fields(fields, Subject, self._allowed_fields)
            subject = Subject(**validated_field)

            self._db_connection.add(subject)
            self._db_connection.commit()
            self._db_connection.refresh(subject)

            response['subject'] = subject
            response['status'] = True

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
            stmt = select_query(Subject)

            if id is None:
                stmt = stmt.filter_by(id=id)

            response['subjects'] = []
            for subject in self._db_connection.scalars(stmt):
                response['subjects'].append(subject)

            response['status'] = True 

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def update(self, item: Subject, **fields) -> dict:
        response = self._std_response_json
        
        try:
            validated_field = self._validate_fields(fields, Subject, self._allowed_fields)

            for field_name, field_value in validated_field.items():
                setattr(item, field_name, field_value)

            self._db_connection.commit()
            self._db_connection.refresh(item)

            response['subject'] = item
            response['status'] = True

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        finally:
            if response['err_description'] is not None:
                self._db_connection.rollback()

        return response

    def delete(self, item: Subject) -> dict:
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