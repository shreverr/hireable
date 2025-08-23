from mongoengine import (
    Document,
    StringField,
    IntField,
    ListField,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)

from pydantic import BaseModel


class Job(Document):
    jd_url = StringField()
    hr_id = StringField()


class JobRequest(BaseModel):
    jd_url: str
    hr_id: str
