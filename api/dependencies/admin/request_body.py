from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from api.utils.admin.patterns import ip_regex

class HarmfulIPAddressBanBody(BaseModel):
    ip:         str               = Field(pattern=ip_regex, nullable=False, index=True)
    reason:     str | None        = Field(default=None, nullable=True)
    duration:   timedelta         = Field(default=None, nullable=True)