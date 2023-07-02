import uvicorn
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from app import schemas, models
from app import deps
from app import crud
import functionality

# Project directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
# TEMPLATES = Jinja2Templates()

app = FastAPI()

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root(request: Request, db: Session = Depends(deps.get_db)) -> dict:
    return {"HWE": "I seem to be working correctly"}


@api_router.get("/converse/", status_code=200, response_model=schemas.Message)
def converse(
    input_msg: schemas.MessageCreate, db: Session = Depends(deps.get_db)
) -> schemas.Message:
    # add message to database
    msg_human = crud.message.create(db=db, obj_in=input_msg)
    # get response
    agent_response_str = functionality.converser(msg_human)
    # add response to database
    msg_agent = schemas.MessageCreate(
        conv_id=msg_human.conv_id,
        content=agent_response_str,
        sender="agent",
        receiver="human",
    )
    agent_response = crud.message.create(db=db, obj_in=msg_agent)
    # return response
    return agent_response


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app")
import uvicorn
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from app import schemas, models
from app import deps
from app import crud
import functionality

# Project directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
# TEMPLATES = Jinja2Templates()

app = FastAPI()

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root(request: Request, db: Session = Depends(deps.get_db)) -> dict:
    return {"HWE": "I seem to be working correctly"}


@api_router.get("/converse/", status_code=200, response_model=schemas.Message)
def converse(
    input_msg: schemas.MessageCreate, db: Session = Depends(deps.get_db)
) -> models.Message:
    # get response
    agent_response_str = functionality.converser(input_msg, db)

    # add both human msg and agent response into the sql table in one go
    # add input message to database
    msg_human = crud.message.create(db=db, obj_in=input_msg)
    # add response to database
    msg_agent = schemas.MessageCreate(
        conv_id=msg_human.conv_id,
        content=agent_response_str,
        sender="agent",
        receiver="human",
    )
    agent_response = crud.message.create(db=db, obj_in=msg_agent)
    # return response
    return agent_response


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app")
