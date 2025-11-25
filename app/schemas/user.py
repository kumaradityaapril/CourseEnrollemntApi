from pydantic import BaseModel, EmailStr, ConfigDict, constr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: constr(min_length=6, max_length=72)


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: str


class PasswordChangeRequest(BaseModel):
    old_password: constr(min_length=6, max_length=72)
    new_password: constr(min_length=6, max_length=72)

