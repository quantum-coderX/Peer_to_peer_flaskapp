from app import app, User, Skill, UserSkill, Connection, Resource, db

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
    
    # Display skills information
    skills = Skill.query.all()
    print("\n=== SKILLS DATABASE CONTENTS ===")
    if skills:
        print(f"Total skills: {len(skills)}")
        print("\nSKILL DETAILS:")
        print("-" * 80)
        print(f"{'ID':<5} {'NAME':<30} {'DESCRIPTION':<45}")
        print("-" * 80)
        
        for skill in skills:
            desc = skill.description[:42] + "..." if skill.description and len(skill.description) > 45 else (skill.description or "")
            print(f"{skill.id:<5} {skill.name:<30} {desc:<45}")
        print("-" * 80)
    else:
        print("No skills found in the database.")
    
    # Display user-skill assignments
    user_skills = UserSkill.query.all()
    print("\n=== USER-SKILL ASSIGNMENTS ===")
    if user_skills:
        print(f"Total assignments: {len(user_skills)}")
        print("\nUSER-SKILL DETAILS:")
        print("-" * 100)
        print(f"{'ID':<5} {'USER':<20} {'SKILL':<25} {'LEVEL':<10} {'ROLE':<10}")
        print("-" * 100)
        
        for us in user_skills:
            role = "Teacher" if us.is_teacher else "Learner"
            print(f"{us.id:<5} {us.user.username:<20} {us.skill.name:<25} {us.skill_level:<10} {role:<10}")
        print("-" * 100)
    else:
        print("No user-skill assignments found in the database.")
    
    # Display connections
    connections = Connection.query.all()
    print("\n=== CONNECTIONS ===")
    if connections:
        print(f"Total connections: {len(connections)}")
        print("\nCONNECTION DETAILS:")
        print("-" * 100)
        print(f"{'ID':<5} {'TEACHER':<20} {'LEARNER':<20} {'SKILL':<25} {'STATUS':<15} {'CREATED':<20}")
        print("-" * 100)
        
        for conn in connections:
            print(f"{conn.id:<5} {conn.teacher.username:<20} {conn.learner.username:<20} {conn.skill.name:<25} {conn.status:<15} {conn.created_at}")
        print("-" * 100)
    else:
        print("No connections found in the database.")
    
    # Display resources
    resources = Resource.query.all()
    print("\n=== RESOURCES ===")
    if resources:
        print(f"Total resources: {len(resources)}")
        print("\nRESOURCE DETAILS:")
        print("-" * 100)
        print(f"{'ID':<5} {'TITLE':<30} {'SKILL':<25} {'SHARED BY':<20} {'CREATED':<20}")
        print("-" * 100)
        
        for res in resources:
            print(f"{res.id:<5} {res.title[:27] + '...' if len(res.title) > 30 else res.title:<30} {res.skill.name:<25} {res.user.username:<20} {res.created_at}")
        print("-" * 100)
    else:
        print("No resources found in the database.")
    
    # Additional database info
    print("\nDATABASE TABLES:")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  • {column['name']}: {column['type']}")
