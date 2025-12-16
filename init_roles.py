"""
Initialize default roles in the database.
Run this script once to create default roles.
"""
from core.db_connect import SessionLocal
from models.user import Role

def init_roles():
    """Create default roles if they don't exist."""
    db = SessionLocal()
    
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        
        if existing_roles > 0:
            print(f"✓ Roles already exist ({existing_roles} roles found)")
            return
        
        # Create default roles
        default_roles = [
            Role(id=1, name="STAFF"),
            Role(id=2, name="ADMIN"),
            Role(id=3, name="USER"),
        ]
        
        db.add_all(default_roles)
        db.commit()
        
        print("✓ Successfully created default roles:")
        for role in default_roles:
            print(f"  - {role.name} (ID: {role.id})")
            
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating roles: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing default roles...")
    init_roles()
