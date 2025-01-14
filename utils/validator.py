from pydantic import BaseModel, HttpUrl, EmailStr, Field, validator, field_validator
from typing import List, Optional, Union, Dict
from datetime import datetime


# Define the reusable date validator function
def validate_date_format(value: str) -> datetime.date:
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"Invalid date format for {value}. Expected format is 'dd/mm/yyyy'.")


class Profile(BaseModel):
    network: str
    username: str
    url: HttpUrl


class Location(BaseModel):
    address: str
    postalCode: str
    city: str
    countryCode: str
    region: str


class Basics(BaseModel):
    name: str
    label: Optional[str] = ""
    image: Optional[str] = ""
    email: EmailStr
    phone: Optional[str] = ""
    url: Optional[HttpUrl] = None
    summary: str
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = None


class Work(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    startDate: str
    endDate: str
    position: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

    @field_validator("startDate", "endDate", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Volunteer(BaseModel):
    organization: str
    position: str
    url: Optional[HttpUrl] = None
    startDate: str
    endDate: str
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

    @field_validator("startDate", "endDate", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Education(BaseModel):
    institution: Optional[str] = None
    url: Optional[HttpUrl] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    startDate: str
    endDate: str
    score: Optional[str] = None
    courses: Optional[List[str]] = None

    @field_validator("startDate", "endDate", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Award(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    date: str
    awarder: str
    summary: Optional[str] = None

    @field_validator("date", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Certificate(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    date: str
    issuer: str
    url: HttpUrl

    @field_validator("date", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Publication(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    publisher: str
    releaseDate: str
    url: HttpUrl
    summary: str


class Language(BaseModel):
    language: str
    fluency: Optional[str] = None


class Interest(BaseModel):
    name: str
    keywords: List[str]


class Reference(BaseModel):
    name: str
    reference: str


class Project(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    description: Optional[str] = None
    highlights: Optional[List[str]] = None
    url: Optional[HttpUrl] = None
    keywords: Optional[List[str]] = None
    roles: Optional[List[str]] = None

    @field_validator("startDate", "endDate", mode="before")
    def validate_dates(cls, value):
        return validate_date_format(value)


class Resume(BaseModel):
    basics: Basics
    work: Optional[List[Work]] = None
    volunteer: Optional[List[Volunteer]] = None
    education: List[Union[Education, str]]
    awards: Optional[List[Union[Award, str]]] = None
    certificates: Optional[List[Union[Certificate, str]]] = None
    publications: Optional[List[Union[Publication, str]]] = None
    skills: List[Union[str, Dict]]
    languages: Optional[List[Language]] = None
    interests: Optional[List[Union[Interest, str]]] = None
    references: Optional[List[Union[Reference, str]]] = None
    projects: List[Union[Project, str]]

    @field_validator("work", "education", mode="before")
    def validate_nested_dates(cls, value):
        if "startDate" in value and "endDate" in value:
            if value["startDate"] > value["endDate"]:
                raise ValueError(
                    f"startDate {value['startDate']} cannot be after endDate {value['endDate']}."
                )
        return value


# def validate_project_input(data: Union[dict, List[dict]]):
#     if isinstance(data, list):
#         return [Project(**project_data) for project_data in data]
#     else:
#         return Project(**data)
