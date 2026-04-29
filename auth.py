import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Extracted directly from your React authConfig.ts
TENANT_ID = "ab57129b-dbfd-4cac-aa77-fc74c40364af"
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

# PyJWKClient automatically fetches and caches Microsoft's public keys
jwks_client = PyJWKClient(JWKS_URL)

# FastAPI security scheme to extract the Bearer token from the request header
security = HTTPBearer()

def verify_microsoft_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Middleware function to intercept incoming requests, extract the Microsoft JWT,
    and mathematically verify its signature against Entra ID's public keys.
    """
    token = credentials.credentials
    
    try:
        # 1. Ask Microsoft's key set which specific key signed this token
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # 2. Decode the token payload
        # Note: In production, you must set audience="YOUR_AZURE_CLIENT_ID" 
        # to ensure the token was generated specifically for your application.
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False} # Set to True once Client ID is added
        )
        
        # 3. Return the verified user data (email, name, etc.)
        return payload

    except jwt.exceptions.PyJWKClientError:
        raise HTTPException(status_code=500, detail="Unable to fetch Entra ID public keys.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")