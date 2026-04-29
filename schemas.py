from pydantic import BaseModel
from typing import List, Optional

# This matches the blue table headers in your image
class ProjectDetails(BaseModel):
    server_location: str = "N/A"
    platform: str = "N/A"
    version: str = "N/A"
    application_name: str
    database_type: str = "SQL Server"
    database_name: str
    database_account: str
    password_change_complete: str = "no"
    owner: str
    proxy_type: str = "External"
    user_auth: str = "Azure MS Entra ID"
    internal_connection: str
    external_connection: str
    note: Optional[str] = None

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