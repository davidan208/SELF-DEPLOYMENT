from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

bearer_security = HTTPBearer()

def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_security)) -> str:
    if not credentials:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Invalid github access_token"
        )
    return credentials.credentials

async def get_admin_access(admin_token: HTTPAuthorizationCredentials = Depends(bearer_security)):
    return admin_token