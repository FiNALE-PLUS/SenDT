from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = 'sendt_user'

    id: int | None                = Field(default=None, primary_key=True)
    username: str                 = Field(unique=True, nullable=False, index=True)
    hash: str                     = Field(nullable=False)
    disabled: bool                = Field(default=False, nullable=False)
    two_factor_secret: str        = Field(nullable=False)
    last_two_factor: str | None   = Field()
    two_factor_enabled: bool      = Field(default=False, nullable=False)
    # TODO: Revisit
    # failed_attempts: int          = Field(default=0, nullable=False)
    
    access_level_id: int          = Field(default=1, foreign_key="user_access_level.id")
    user_access_level: UserAccess = Relationship(back_populates="users_with_access_level")


# TODO: Add access levels on startup and add 1-many relation
class UserAccess(SQLModel, table=True):
    __tablename__ = 'user_access_level'

    id: int | None                      = Field(default=None, primary_key=True)
    name: str                           = Field(nullable=False)
    users_with_access_level: list[User] = Relationship(back_populates="user_access_level")