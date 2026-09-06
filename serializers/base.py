from abc import ABC, abstractmethod

from sqlalchemy.orm import DeclarativeBase

from typing import Optional, List

class BaseSerializer(ABC):
    def __init__(self):
        self._std_response_json = {
            'status': False,
            'err_description': None
        }

    def _validate_fields(self, fields: dict, model: object, allowed_fields: Optional[List[str]]) -> dict:
        validated_fields = {}

        for field_name, field_value in fields.items():
            if all((
                hasattr(model, field_name),
                allowed_fields is not None and field_name in allowed_fields
            )):
                validated_fields[field_name] = field_value

        return validated_fields

    @abstractmethod
    def insert(self, **fields) -> dict:
        pass 

    @abstractmethod
    def select(self, id: Optional[int | str]) -> dict:
        pass 

    @abstractmethod
    def update(self, item: object, **fields) -> dict:
        pass 

    @abstractmethod
    def delete(self, item: object) -> dict:
        pass 
    
