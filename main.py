from fastapi import APIRouter, Depends, HTTPException, Request, status, FastAPI



from url_shortener.api import url_api
from url_shortener.db.session import Base, engine

Base.metadata.create_all(bind=engine)


app=FastAPI(title="url shortner")

app.include_router(url_api.router,prefix="")


@app.get("/")
def root():
    return {"welcome"}