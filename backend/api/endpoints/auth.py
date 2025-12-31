from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy import select
import traceback

from backend.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI, FRONTEND_URL, IS_PROD
from backend.database import async_session, User

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
    authorize_params={"prompt": "select_account"}
)

@router.get("/login")
async def login(request: Request):
    dynamic_uri = str(request.url_for("auth"))
    redirect_uri = REDIRECT_URI or dynamic_uri
    if IS_PROD: 
        redirect_uri = redirect_uri.replace("http://", "https://")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        print(f"OAuth Error: {error.error}")
        return HTMLResponse(f'<h1>OAuth Error</h1><pre>{error.error}</pre>')
    
    user_info = token.get("userinfo")
    if user_info:
        try:
            async with async_session() as session:
                async with session.begin():
                    stmt = select(User).where(User.google_id == user_info["sub"])
                    result = await session.execute(stmt)
                    user = result.scalar_one_or_none()
                    if not user:
                        user = User(google_id=user_info["sub"], email=user_info["email"], name=user_info["name"], picture=user_info.get("picture"))
                        session.add(user)
                    else:
                        user.name, user.picture = user_info["name"], user_info.get("picture")
                    await session.flush()
                    request.session["user"] = {
                        "id": str(user.google_id), 
                        "db_id": int(user.id), 
                        "name": str(user.name), 
                        "username": str(user.username) if user.username else None,
                        "email": str(user.email), 
                        "picture": user.picture,
                        "default_time": float(user.default_time),
                        "default_increment": float(user.default_increment),
                        "default_time_control_enabled": bool(user.default_time_control_enabled)
                    }
        except Exception as e:
            print(f"Error saving user to DB: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Database error during authentication")
            
    return RedirectResponse(url=FRONTEND_URL)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url=FRONTEND_URL)
