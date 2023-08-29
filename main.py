from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from token_utils import create_access_token, check_jwt_token
import httpx
from datetime import  timedelta

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/callback"
GOOGLE_SECRET_ID = os.environ["GOOGLE_SECRET_ID"]

# Google OAuth2.0認証用のURL
GOOGLE_AUTH_URL = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20profile%20email"

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return f"""
    <form method="post" action="/login">
        <input type="submit" value="Login with Google">
    </form>
    """

@app.post("/login")
async def login():
    return RedirectResponse(url=GOOGLE_AUTH_URL)

# コールバック処理
@app.get("/callback")
async def callback(request: Request, code: str = None):
    if code is None:
        return {"message": "Google login failed"}

    # アクセストークンの取得
    token_url = "https://oauth2.googleapis.com/token"
    params = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_SECRET_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=params)
        token_data = response.json()

    if "access_token" not in token_data:
        return {"message": "Failed to retrieve access token"}

    access_token = token_data["access_token"]

    # ユーザー情報の取得
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        user_info = response.json()

    # JWTトークンを発行 期限1分
    ACCESS_TOKEN_EXPIRE_MINUTES = 1
    jwt_access_token = create_access_token(
        data={"sub": user_info["id"],"email": user_info["email"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # JWTトークンをリダイレクトURLに付加してリダイレクト
    redirect_url = f"/profile?token={jwt_access_token}"
    print(user_info)
    return RedirectResponse(url=redirect_url)

@app.get("/profile", response_class=HTMLResponse)

async def profile_page(request: Request, token: str = None):

    if token is None:
        return "Token is missing."

    # JWTトークンを検証
    user_id, user_email, error_message =check_jwt_token(token)


    # プロフィール情報を表示
    return f"""
        <h1>Profile</h1>
        <p>User ID: {user_id}</p>
        <p>Email: {user_email}</p>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
