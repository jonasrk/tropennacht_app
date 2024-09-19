import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from generate_calendar import generate_tropical_nights_plot
from starlette.middleware.sessions import SessionMiddleware
from supabase import Client, create_client
from tropennacht_db import add_user_city, delete_user_city_by_id, get_cities_for_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

SESSION_KEY = os.getenv("SESSION_KEY")

if not SESSION_KEY:
    raise EnvironmentError(
        "The environment variable SESSION_KEY is not set. Please set it before running the application."
    )

app.add_middleware(SessionMiddleware, secret_key=SESSION_KEY)

templates = Jinja2Templates(directory="templates")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request) -> HTMLResponse:
    """
    Render the signup page
    """

    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def post_signup(request: Request) -> RedirectResponse:
    """
    Handle the signup form submission
    """

    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    try:
        _ = supabase.auth.sign_up({"email": email, "password": password})
        return RedirectResponse("/login", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": str(e)}
        )


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request) -> HTMLResponse:
    """
    Render the login page
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def post_login(request: Request) -> RedirectResponse:
    """
    Handle the login form submission
    """

    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        _ = response.session.access_token
        user = response.user
        request.session["user"] = {"email": user.email, "id": user.id}
        return RedirectResponse("/cities", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": str(e)}
        )


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    """
    Log the user out
    """

    request.session.clear()
    return RedirectResponse("/login", status_code=302)


@app.get("/", response_class=HTMLResponse)
async def public_route(request: Request) -> HTMLResponse:
    """
    Render the public page
    """

    return templates.TemplateResponse("public.html", {"request": request})


# --- protected below


class NotAuthenticatedException(Exception):
    pass


def get_current_user(request: Request) -> dict:
    """
    Get the current user from the session
    """

    user = request.session.get("user")
    if not user or not user.get("id"):
        raise NotAuthenticatedException
    return user


@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_exception_handler(
    request: Request, exc: NotAuthenticatedException
):
    return RedirectResponse("/login", status_code=302)


@app.get("/cities", response_class=HTMLResponse)
async def cities_route(
    request: Request, user: dict = Depends(get_current_user)
) -> HTMLResponse:
    """
    Render the cities page
    """

    cities = get_cities_for_user(user["id"])
    # cities = [{"city": "Berlin", "id": "1"}, {"city": "London", "id": "2"}]

    return templates.TemplateResponse(
        "cities.html",
        {
            "request": request,
            "user": user,
            "cities": cities,
            "city_options": [x["name"] for x in city_options],
        },
    )


# get city from path
@app.get("/city/{city_id}", response_class=HTMLResponse)
async def city(
    request: Request, city_id: str, user: dict = Depends(get_current_user)
) -> RedirectResponse:
    """
    Get a city from the user's list of cities
    """

    city_list = get_cities_for_user(user["id"])
    selected_city = next((city for city in city_list if city["id"] == city_id), None)

    # mock_selected_city = {"city": "Berlin", "id": "1"}
    # selected_city = mock_selected_city
    selected_city_option = next(
        (city for city in city_options if city["name"] == selected_city["city"]),
    )

    plot_html = generate_tropical_nights_plot(
        lat=selected_city_option["lat"],
        lon=selected_city_option["lon"],
    )

    return templates.TemplateResponse(
        "city.html",
        {"request": request, "user": user, "city_id": city_id, "plot_html": plot_html},
    )


@app.post("/city", response_class=HTMLResponse)
async def add_city(
    request: Request, user: dict = Depends(get_current_user)
) -> RedirectResponse:
    """
    Add a city to the user's list of cities
    """

    form = await request.form()
    city = form.get("city")
    add_user_city(user_id=user["id"], city=city)
    return RedirectResponse("/cities", status_code=302)


@app.post("/delete_city", response_class=HTMLResponse)
async def delete_city(
    request: Request, user: dict = Depends(get_current_user)
) -> RedirectResponse:
    """
    Delete a city from the user's list of cities
    """

    form = await request.form()
    city_id = form.get("city_id")
    try:
        delete_user_city_by_id(user_id=user["id"], city_id=city_id)
        print(f"Deleted city with ID: {city_id}")
    except ValueError:
        print("Invalid UUID for city_id")
    return RedirectResponse("/cities", status_code=302)


city_options = [
    {"name": "Abu Dhabi", "lat": 24.4539, "lon": 54.3773},
    {"name": "Addis Ababa", "lat": 9.03, "lon": 38.74},
    {"name": "Amman", "lat": 31.9454, "lon": 35.9284},
    {"name": "Amsterdam", "lat": 52.3676, "lon": 4.9041},
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275},
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275},
    {"name": "Bangkok", "lat": 13.7563, "lon": 100.5018},
    {"name": "Barcelona", "lat": 41.3851, "lon": 2.1734},
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
    {"name": "Belgrade", "lat": 44.7866, "lon": 20.4489},
    {"name": "Berlin", "lat": 52.52, "lon": 13.405},
    {"name": "Bogotá", "lat": 4.7110, "lon": -74.0721},
    {"name": "Brisbane", "lat": -27.4698, "lon": 153.0251},
    {"name": "Brussels", "lat": 50.8503, "lon": 4.3517},
    {"name": "Bucharest", "lat": 44.4268, "lon": 26.1025},
    {"name": "Budapest", "lat": 47.4979, "lon": 19.0402},
    {"name": "Buenos Aires", "lat": -34.6037, "lon": -58.3816},
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
    {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241},
    {"name": "Casablanca", "lat": 33.5731, "lon": -7.5898},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"name": "Copenhagen", "lat": 55.6761, "lon": 12.5683},
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Doha", "lat": 25.276987, "lon": 51.521569},
    {"name": "Doha", "lat": 25.276987, "lon": 51.521569},
    {"name": "Dubai", "lat": 25.276987, "lon": 55.296249},
    {"name": "Dublin", "lat": 53.3498, "lon": -6.2603},
    {"name": "Edinburgh", "lat": 55.9533, "lon": -3.1883},
    {"name": "Florence", "lat": 43.7696, "lon": 11.2558},
    {"name": "Hanoi", "lat": 21.0285, "lon": 105.8542},
    {"name": "Havana", "lat": 23.1136, "lon": -82.3666},
    {"name": "Helsinki", "lat": 60.1695, "lon": 24.9354},
    {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
    {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784},
    {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784},
    {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456},
    {"name": "Jerusalem", "lat": 31.7683, "lon": 35.2137},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
    {"name": "Kiev", "lat": 50.4501, "lon": 30.5234},
    {"name": "Kigali", "lat": -1.9579, "lon": 30.1127},
    {"name": "Kraków", "lat": 50.0647, "lon": 19.9450},
    {"name": "Kuala Lumpur", "lat": 3.1390, "lon": 101.6869},
    {"name": "Kyoto", "lat": 35.0116, "lon": 135.7681},
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
    {"name": "Las Vegas", "lat": 36.1699, "lon": -115.1398},
    {"name": "Lima", "lat": -12.0464, "lon": -77.0428},
    {"name": "Lisbon", "lat": 38.7223, "lon": -9.1393},
    {"name": "Ljubljana", "lat": 46.0569, "lon": 14.5058},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
    {"name": "Manila", "lat": 14.5995, "lon": 120.9842},
    {"name": "Marrakesh", "lat": 31.6295, "lon": -7.9811},
    {"name": "Melbourne", "lat": -37.8136, "lon": 144.9631},
    {"name": "Mexico City", "lat": 19.4326, "lon": -99.1332},
    {"name": "Miami", "lat": 25.7617, "lon": -80.1918},
    {"name": "Milan", "lat": 45.4642, "lon": 9.1900},
    {"name": "Monaco", "lat": 43.7384, "lon": 7.4246},
    {"name": "Montreal", "lat": 45.5017, "lon": -73.5673},
    {"name": "Moscow", "lat": 55.7558, "lon": 37.6173},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Muscat", "lat": 23.5880, "lon": 58.3829},
    {"name": "Naples", "lat": 40.8518, "lon": 14.2681},
    {"name": "New York", "lat": 40.7128, "lon": -74.006},
    {"name": "Nice", "lat": 43.7102, "lon": 7.2620},
    {"name": "Osaka", "lat": 34.6937, "lon": 135.5023},
    {"name": "Oslo", "lat": 59.9139, "lon": 10.7522},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Phnom Penh", "lat": 11.5564, "lon": 104.9282},
    {"name": "Prague", "lat": 50.0755, "lon": 14.4378},
    {"name": "Reykjavik", "lat": 64.1466, "lon": -21.9426},
    {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
    {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964},
    {"name": "Saint Petersburg", "lat": 59.9311, "lon": 30.3609},
    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
    {"name": "Santiago", "lat": -33.4489, "lon": -70.6693},
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333},
    {"name": "Sarajevo", "lat": 43.8563, "lon": 18.4131},
    {"name": "Seoul", "lat": 37.5665, "lon": 126.9780},
    {"name": "Shanghai", "lat": 31.2304, "lon": 121.4737},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"name": "Sofia", "lat": 42.6977, "lon": 23.3219},
    {"name": "Stockholm", "lat": 59.3293, "lon": 18.0686},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "Tbilisi", "lat": 41.7151, "lon": 44.8271},
    {"name": "Tehran", "lat": 35.6892, "lon": 51.3890},
    {"name": "Tel Aviv", "lat": 32.0853, "lon": 34.7818},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Toronto", "lat": 43.651070, "lon": -79.347015},
    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207},
    {"name": "Venice", "lat": 45.4408, "lon": 12.3155},
    {"name": "Vienna", "lat": 48.2082, "lon": 16.3738},
    {"name": "Warsaw", "lat": 52.2297, "lon": 21.0122},
    {"name": "Yerevan", "lat": 40.1792, "lon": 44.4991},
    {"name": "Zagreb", "lat": 45.8150, "lon": 15.9819},
    {"name": "Zurich", "lat": 47.3769, "lon": 8.5417},
]
