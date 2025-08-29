from app import app, User, db

# Use app context to query the database
with app.app_context():
    # Get all users
    users = User.query.all()
    
    # Display user information
    print("\n=== USER DATABASE CONTENTS ===")
    if users:
        print(f"Total users: {len(users)}")
        print("\nUSER DETAILS:")
        print("-" * 80)
        print(f"{'ID':<5} {'USERNAME':<20} {'EMAIL':<30} {'REGISTERED ON':<25}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.date_registered}")
        print("-" * 80)
    else:
        print("No users found in the database.")
    
    # Additional database info
    print("\nDATABASE TABLES:")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  • {column['name']}: {column['type']}")
