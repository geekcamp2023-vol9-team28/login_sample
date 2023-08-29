from datetime import datetime, timedelta
from jose import jwt, JWTError #pip install python-jose[cryptography]

import os
from dotenv import load_dotenv  #pip install python-dotenv
load_dotenv()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ["JWT_ALGORITHM"]

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def check_jwt_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None,None, "Invalid token."
        email: str = payload.get("email")
        return user_id, email, "sucess"
    except JWTError:
        return None,None, "Invalid token."
