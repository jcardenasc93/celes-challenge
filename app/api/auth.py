import json

import pyrebase
from fastapi import APIRouter, HTTPException, Request, status
from firebase_admin import auth, credentials
from firebase_admin import initialize_app as firebase_init_app
from requests.exceptions import HTTPError

from app.config import app_settings, get_logger
from app.schemas.auth import AccessTokenSchema, AuthTokenResponseSchema, UserAuthSchema
from app.schemas.base_response import BaseResponse

cred = credentials.Certificate(app_settings().FIREBASE_KEY_PATH)
firebase_init_app(cred)

firebase_app = pyrebase.initialize_app(app_settings().FIREBASE_APP_CONFIG)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

logger = get_logger()


@router.post("/signup", summary="Allows user creation", status_code=status.HTTP_200_OK)
async def signup(signup_data: UserAuthSchema) -> BaseResponse:
    """This endpoint is used to create users"""
    try:
        user = auth.create_user(email=signup_data.email, password=signup_data.password)
    except auth.EmailAlreadyExistsError as e:
        logger.warning(msg="Signup with existent email", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {signup_data.email} already exists",
        )
    except Exception as e:
        logger.error(msg=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"An error ocurred during user creation. Try it later",
        )

    return BaseResponse(data={"msg": "User created successfuly", "user_uuid": user.uid})


@router.post("/login", summary="Generates auth token", status_code=status.HTTP_200_OK)
async def signin(login_data: UserAuthSchema) -> AuthTokenResponseSchema:
    """This endpoint is used to generate authentication token"""
    app_auth = firebase_app.auth()
    try:
        user = app_auth.sign_in_with_email_and_password(
            email=login_data.email,
            password=login_data.password,
        )
    except auth.EmailNotFoundError:
        logger.warning("Attempt to login with no existent email")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email: {login_data.email} not found",
        )
    except HTTPError as e:
        logger.warning("Attempt to login with invalid credentials")
        error_json = e.args[1]
        error = json.loads(error_json)["error"]["message"]
        if error == "INVALID_LOGIN_CREDENTIALS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
            )
    except Exception as e:
        breakpoint()
        logger.error(msg=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"An error ocurred during JWT token generation. Try it later",
        )
    token = AccessTokenSchema(token_id=user["idToken"], expires_in=user["expiresIn"])
    return AuthTokenResponseSchema(data=token)


async def validate_token(request: Request) -> bool:
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )
    try:
        auth.verify_id_token(token)
    except auth.TokenSignError:
        logger.warning("Atempt to use an invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    except auth.ExpiredIdTokenError:
        logger.warning("Atempt to use an expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Given token expired"
        )
    except Exception as e:
        logger.error(msg="Token couldn't be validated", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token couldn't be validated",
        )
    return True
