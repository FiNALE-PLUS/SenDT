from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Column, DateTime, Relationship, SQLModel, Field, func

from utils.timestamps.default_timestamps import get_utc_now

from api.utils.admin.patterns import ip_regex
from db.models.users import User

class BannedIPAddress(SQLModel, table=True):
    __tablename__ = 'api_ip_naughty_list'
    
    id:         int | None        = Field(default=None, primary_key=True)
    ip:         str               = Field(regex=ip_regex, nullable=False, index=True)
    reason:     str | None        = Field(default=None, nullable=True)
    created_by: int | None        = Field(default=None, foreign_key="sendt_user.id")
    ip_ban_creator: User | None   = Relationship(back_populates="user_ip_bans")
    created_at: datetime | None   = Field(default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    ends_at: datetime | None      = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))