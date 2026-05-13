import pandas as pd
import json
from database import SessionLocal
from models import Project

def clean_value(val):
    """Helper to convert NaN/empty Excel cells into empty strings or proper text"""
    if pd.isna(val) or val is None:
        return ""
    return str(val).strip()

def run_import(filename, environment_name):
    print(f"Loading {filename} as {environment_name} environment...")
    
    try:
        # 1. Read the Excel file
        df = pd.read_excel(filename)
    except FileNotFoundError:
        print(f"⚠️ Could not find {filename}. Skipping {environment_name} import.")
        return

    # 2. Open a connection to your SQL Server
    db = SessionLocal()
    
    try:
        success_count = 0
        for index, row in df.iterrows():
            
            # Extract standard columns
            app_name = clean_value(row.get("Application Name", ""))
            
            # 🛡️ FIX 1: Ignore "Ghost Rows" where the Application Name is completely blank
            if not app_name:
                continue
                
            raw_status = clean_value(row.get("Status", "active"))
            
            # 🛡️ FIX 2: Protect the SQL column from Truncation Errors
            # Limit the physical status to 45 characters. 
            status_safe = raw_status[:45].lower()
            
            # If the status was super long, grab the existing note and append the overflow data to it
            current_note = clean_value(row.get("Note", ""))
            if len(raw_status) > 45:
                current_note = f"[Status Overflow: {raw_status}] {current_note}"

            # 3. Build the JSON dictionary for the blue-table details
            details_dict = {
                "server_location": clean_value(row.get("Server Location", "N/A")),
                "platform": clean_value(row.get("Platform", "N/A")),
                "version": clean_value(row.get("Version", "N/A")),
                "application_name": app_name,
                "database_type": clean_value(row.get("Database", "SQL Server")),
                "database_name": clean_value(row.get("Database Name", "Unknown")),
                "database_account": clean_value(row.get("Database Account", "Unknown")),
                "password_change_complete": clean_value(row.get("Database Password Change Complete (yes/no)", "no")),
                "owner": clean_value(row.get("Owner", "Unknown")),
                "proxy_type": clean_value(row.get("Internal/External n (proxy)", "External")),
                "user_auth": clean_value(row.get("User Auth", "Azure MS Entra ID")),
                "service_account": clean_value(row.get("Service Account", "Unknown")),
                "internal_connection": clean_value(row.get("Internal connedtion", "") or row.get("Internal connection", "")),
                "external_connection": clean_value(row.get("External Connection", "")),
                "note": current_note, # Uses the potentially updated note containing the overflow data
                "environment": environment_name  
            }
            
            # 4. Compress the dictionary into a JSON text string
            description_json = json.dumps(details_dict)
            
            # 5. Create the physical database row
            new_project = Project(
                name=app_name,             
                status=status_safe,     
                client="",                 
                description=description_json
            )
            
            db.add(new_project)
            success_count += 1
            
        # 6. Commit all rows to SQL Server simultaneously
        db.commit()
        print(f"✅ Successfully migrated {success_count} {environment_name} projects into SQL Server!\n")
        
    except Exception as e:
        print(f"❌ Error during {environment_name} import: {e}\n")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Make sure both .xlsx files are in the same folder as this Python script
    
    # 1. Run the Production import
    run_import("Application_Server_Information_PROD.xlsx", "Production")
    
    # 2. Run the Development import (You can safely run this again, it will just add duplicates if you don't clear the DB first)
    run_import("Application_Server_Information_DEV.xlsx", "Development")