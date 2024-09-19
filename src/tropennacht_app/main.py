from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from supabase import create_client, Client
import os
from tropennacht_db import add_user_city, delete_user_city_by_id

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_KEY"))

templates = Jinja2Templates(directory="templates")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def post_signup(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    try:
        # Sign up the user
        response = supabase.auth.sign_up({"email": email, "password": password})
        # Redirect to login page
        return RedirectResponse("/login", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": str(e)})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def post_login(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    try:
        # Sign in the user
        response = supabase.auth.sign_in_with_password({"email":email, "password":password})
        access_token = response.session.access_token
        user = response.user
        # Store user info in the session
        request.session['user'] = {'email': user.email, 'id': user.id}
        return RedirectResponse("/protected", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)



@app.get("/public", response_class=HTMLResponse)
async def public_route(request: Request):
    return templates.TemplateResponse("public.html", {"request": request})

# --- protected below
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)
    return user

@app.get("/protected", response_class=HTMLResponse)
async def protected_route(request: Request, user: dict = Depends(get_current_user)):

    if type(user) is not dict:
        return RedirectResponse("/login", status_code=302)
    if not user.get("id", None):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("protected.html", {"request": request, "user": user})

@app.post("/city", response_class=HTMLResponse)
async def add_city(request: Request, user: dict = Depends(get_current_user)):
    if type(user) is not dict:
        return RedirectResponse("/login", status_code=302)
    if not user.get("id", None):
        return RedirectResponse("/login", status_code=302)
    user_id = user["id"]
    form = await request.form()
    city = form.get("city")
    add_user_city(user_id=user_id, city=city)
    return RedirectResponse("/protected", status_code=302)