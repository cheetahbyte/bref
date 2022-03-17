from fastapi import FastAPI, Request, Form, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiosqlite
import random
import string
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

db = None


@app.route("/", methods=("GET", "POST"))
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/shorten", response_class=HTMLResponse)
async def shorten(request: Request, url=Form(...)):
    short: str = "".join(random.choices(
        string.ascii_letters + string.digits, k=6))
    async with aiosqlite.connect("bref.db") as db:
        # check if url already exists
        cursor = await db.execute(
            "select * from urls where url=?", (url,))
        result = await cursor.fetchone()
        if result:
            return templates.TemplateResponse("index.html", {"request": request, "short": result[1], "url": result[0], "base_url": request.url.scheme + "://" + request.url.hostname + ":" + str(request.url.port)})
        # insert
        await db.execute("INSERT INTO urls (url, short) VALUES (?, ?)", (url, short))
        await db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "short": short, "url": url, "base_url": request.url.scheme + "://" + request.url.hostname + ":" + str(request.url.port)})


@app.get("/shorten", status_code=308, response_class=RedirectResponse)
async def redirect():
    return RedirectResponse("/")


@app.get("/{short}", response_class=RedirectResponse, status_code=307)
async def redirect_short(short: str):
    async with aiosqlite.connect("bref.db") as db:
        # check if url already exists
        cursor = await db.execute(
            "select * from urls where short=?", (short,))
        result = await cursor.fetchone()
        if result:
            return RedirectResponse(result[0])


@app.on_event("startup")
async def startup():
    async with aiosqlite.connect("bref.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT, short TEXT)")
        await db.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", reload=True)
