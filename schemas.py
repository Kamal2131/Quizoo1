from pydantic import BaseModel, EmailStr

# Schema for user registration input
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Schema for returning user details in API responses (excluding password)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # Allows ORM model to be parsed directly

# Schema for user login input
class UserLogin(BaseModel):
    username: str
    password: str
