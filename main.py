from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx

app = FastAPI()

GOOGLE_CLIENT_ID = ""
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/callback"
GOOGLE_SECRET_ID = ""

# Google OAuth2.0認証用のURL
GOOGLE_AUTH_URL = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20profile%20email"

# ログインページ
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return f"""
    <form method="post" action="/login">
        <input type="submit" value="Login with Google">
    </form>
    """

# ログイン処理
@app.post("/login")
async def login():
    return RedirectResponse(url=GOOGLE_AUTH_URL)

# Googleからのコールバックを受け取るエンドポイント
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
        
    return user_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
