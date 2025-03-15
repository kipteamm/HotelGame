from hotel.auth.models import User
from hotel.extensions import db
from hotel.config import ALLOWED_CHARACTERS_REGEX

import typing as t


def validate_string(value: str, min_length: int=0, max_length: int=0, type: t.Optional[str]=None) -> tuple[t.Optional[str], str]:
    if len(value) < min_length:
        return None, "Too short"
    
    if len(value) > max_length:
        return None, "Too long"

    elif type == "username" and not ALLOWED_CHARACTERS_REGEX.match(value):
        return None, "Username invalid A-z, 0-9, -, _, ."
        
    return value, "No error"


def validate_int(value: int, min: int=0, max: int=0) -> tuple[t.Optional[int], str]:
    if value < min:
        return None, f"Minimum value is {min}."
    
    if value > max:
        return None, f"Maximum value is {max}"
    
    return value, "No error"


def validate_bool(value: t.Union[str, bool]) -> tuple[t.Optional[int], str]:
    if isinstance(value, bool):
        return value, "No error"
    
    if value == "on":
        return True, "No error"
    
    if value == "off":
        return False, "No error"
    
    return None, "Invalid boolean"
