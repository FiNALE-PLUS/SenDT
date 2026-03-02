from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = 'sendt_user'

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    hash: str = Field(nullable=False)


# TODO: Add access levels on startup and add 1-many relation
class UserAccess(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)