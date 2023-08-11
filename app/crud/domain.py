from app.crud.crud_base import CRUDBase

from app import models
from app import schemas
from sqlalchemy.orm import Session


class CRUDDomain(CRUDBase[models.Domain, schemas.DomainCreate]):
    pass


domain = CRUDDomain(models.Domain)
