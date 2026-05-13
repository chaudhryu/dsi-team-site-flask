import json
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database, auth

app = FastAPI(title="DSI Project Service")

@app.post("/api/projects", response_model=schemas.ProjectResponse)
def create_project(
    project_in: schemas.ProjectCreate, 
    db: Session = Depends(database.get_db),
    user: dict = Depends(auth.verify_microsoft_token) # Security Check
):
    # Convert the detailed object into a JSON string for the DB
    description_str = project_in.details.json()
    
    db_project = models.Project(
        name=project_in.name,
        status=project_in.status,
        client=project_in.client,
        description=description_str
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Parse description back to dict for the response
    return {
        **db_project.__dict__,
        "details": json.loads(db_project.description)
    }

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(database.get_db)):
    projects = db.query(models.Project).all()
    results = []
    
    for p in projects:
        # 1. Establish the default dictionary required by your Pydantic schema
        details_dict = {
            "server_location": "N/A",
            "platform": "N/A",
            "version": "N/A",
            "application_name": "Legacy Project",
            "database_type": "SQL Server",
            "database_name": "Unknown",
            "database_account": "Unknown",
            "password_change_complete": "no",
            "owner": "Unknown",
            "proxy_type": "External",
            "user_auth": "Azure MS Entra ID",
            "service_account": "Unknown", # 👈 ADD THIS LINE HERE
            "internal_connection": "Unknown",
            "external_connection": "Unknown",
            "note": None
        }
        
        # 2. Check if there is data in the description column
        if p.description and str(p.description).strip() != "":
            try:
                # Attempt to parse it as a strictly formatted JSON object
                parsed_json = json.loads(p.description)
                
                # If it succeeds and is a dictionary, overwrite our defaults with real data
                if isinstance(parsed_json, dict):
                    details_dict.update(parsed_json)
                    
            except json.JSONDecodeError:
                # 3. THE FALLBACK: If it fails because it's legacy text, save it as a note
                details_dict["note"] = str(p.description)

        # 4. Append the fully validated object to the results array
        results.append({
            "id": p.id,
            "name": p.name or "Unnamed Project",
            "status": p.status or "Unknown",
            "client": p.client or "Unknown",
            "details": details_dict
        })
        
    return results