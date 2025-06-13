from typing import TypeVar

from pydantic import BaseModel

from app.infrastructure.db.models import Base

TDomain = TypeVar("TDomain", bound=BaseModel)
TOrm = TypeVar("TOrm", bound=Base)


def orm_to_domain(db_model: TOrm, domain_class: type[TDomain]) -> TDomain:
    return domain_class.model_validate(db_model)


def domain_to_orm(domain_model: TDomain, orm_class: type[TOrm]) -> TOrm:
    return orm_class(**domain_model.model_dump())
