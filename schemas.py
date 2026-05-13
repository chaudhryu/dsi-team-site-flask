from pydantic import BaseModel
from typing import List, Optional

# This matches the blue table headers in your image
class ProjectDetails(BaseModel):
    server_location: str | None = "N/A"
    platform: str | None = "N/A"
    version: str | None = "N/A"
    application_name: str
    database_type: str | None = "SQL Server"
    database_name: str
    database_account: str | None = "Unknown"
    password_change_complete: str | None = "no"
    owner: str
    proxy_type: str | None = "External"
    user_auth: str | None = "Azure MS Entra ID"
    service_account: str | None = "Unknown"  # 👈 THE NEW EXCEL COLUMN
    internal_connection: str | None = "Unknown"
    external_connection: str | None = "Unknown"
    note: str | None = None

class ProjectCreate(BaseModel):
    name: str
    status: str
    client: str
    details: ProjectDetails  # This will be serialized into the description column

class ProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    client: str
    details: ProjectDetails
    
    class Config:
        from_attributes = True