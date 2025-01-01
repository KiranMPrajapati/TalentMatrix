from pydantic import BaseModel, HttpUrl, EmailStr, Field, validator
from typing import List, Optional,  Union, Dict

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
    name: Optional[str] = ""
    company: Optional[str] = ""
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    startDate: str
    endDate: str
    position: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

class Volunteer(BaseModel):
    organization: str
    position: str
    url: Optional[HttpUrl] = None
    startDate: str
    endDate: str
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None

class Education(BaseModel):
    institution: Optional[str] = None
    url: Optional[HttpUrl] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    startDate: str
    endDate: str
    score: Optional[str] = None
    courses: Optional[List[str]] = None

class Award(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    date: str
    awarder: str
    summary: Optional[str] = None

class Certificate(BaseModel):
    name: Optional[Union[str, None]] = None
    title: Optional[Union[str, None]] = None
    date: str
    issuer: str
    url: HttpUrl

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

class Resume(BaseModel):
    basics: Basics
    work: Optional[List[Work]] = None
    volunteer: Optional[List[Volunteer]] = None
    education: List[Education]
    awards: Optional[List[Award]] = None
    certificates: Optional[List[Certificate]] = None
    publications: Optional[List[Publication]] = None
    skills: List[Union[str, Dict]]
    languages: Optional[List[Language]] = None
    interests: Optional[List[Interest]] = None
    references: Optional[List[Reference]] = None
    projects: List[Project]

    @validator('work', 'education', pre=True, each_item=True)
    def validate_dates(cls, value):
        if 'startDate' in value.keys() and 'endDate' in value.keys():
            if value['startDate'] > value['endDate']:
                raise ValueError(f"startDate {value['startDate']} cannot be after endDate {value['endDate']}.")
        return value

# def validate_project_input(data: Union[dict, List[dict]]):
#     if isinstance(data, list):
#         return [Project(**project_data) for project_data in data]
#     else:
#         return Project(**data)
