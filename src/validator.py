from pydantic import BaseModel, HttpUrl, EmailStr, Field, validator
from typing import List, Optional

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
    label: str
    image: Optional[str] = ""
    email: EmailStr
    phone: str
    url: HttpUrl
    summary: str
    location: Location
    profiles: List[Profile]

class Work(BaseModel):
    name: str
    position: str
    url: HttpUrl
    startDate: str
    endDate: str
    summary: str
    highlights: List[str]

class Volunteer(BaseModel):
    organization: str
    position: str
    url: HttpUrl
    startDate: str
    endDate: str
    summary: str
    highlights: List[str]

class Education(BaseModel):
    institution: str
    url: HttpUrl
    area: str
    studyType: str
    startDate: str
    endDate: str
    score: str
    courses: List[str]

class Award(BaseModel):
    title: str
    date: str
    awarder: str
    summary: str

class Certificate(BaseModel):
    name: str
    date: str
    issuer: str
    url: HttpUrl

class Publication(BaseModel):
    name: str
    publisher: str
    releaseDate: str
    url: HttpUrl
    summary: str

class Skill(BaseModel):
    name: str
    level: str
    keywords: List[str]

class Language(BaseModel):
    language: str
    fluency: str

class Interest(BaseModel):
    name: str
    keywords: List[str]

class Reference(BaseModel):
    name: str
    reference: str

class Project(BaseModel):
    name: str
    startDate: str
    endDate: str
    description: str
    highlights: List[str]
    url: HttpUrl

class Resume(BaseModel):
    basics: Basics
    work: List[Work]
    volunteer: List[Volunteer]
    education: List[Education]
    awards: List[Award]
    certificates: List[Certificate]
    publications: List[Publication]
    skills: List[Skill]
    languages: List[Language]
    interests: List[Interest]
    references: List[Reference]
    projects: List[Project]

    @validator('work', 'volunteer', 'education', 'projects', pre=True, each_item=True)
    def validate_dates(cls, value):
        if value['startDate'] > value['endDate']:
            raise ValueError(f"startDate {value['startDate']} cannot be after endDate {value['endDate']}.")
        return value

resume = Resume(**data)
print(resume)
