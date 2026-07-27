#!/usr/bin/env python3
"""Database seeding script"""

import os
import sys
from faker import Faker

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Note

fake = Faker()


def seed_database():
    """Seed the database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create users
        print("Creating users...")
        users = []
        user_credentials = [
            ('alice', 'alice123'),
            ('bob', 'bob123'),
            ('charlie', 'charlie123'),
        ]
        
        for username, password in user_credentials:
            user = User(username=username)
            user.set_password(password)
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✓ Created {len(users)} users")
        
        # Create notes for each user
        print("Creating notes...")
        note_count = 0
        
        categories = ['Personal', 'Work', 'Ideas', 'Todo', 'Learning']
        
        for user in users:
            # Create 5-8 notes per user
            num_notes = fake.random_int(min=5, max=8)
            
            for _ in range(num_notes):
                note = Note(
                    title=fake.sentence(nb_words=6),
                    content=fake.paragraph(nb_sentences=4),
                    category=fake.random_element(categories),
                    is_pinned=fake.boolean(chance_of_getting_true=20),
                    user_id=user.id
                )
                db.session.add(note)
                note_count += 1
        
        db.session.commit()
        print(f"✓ Created {note_count} notes")
        
        print("\n✅ Database seeded successfully!")
        print("\nTest Credentials:")
        for username, password in user_credentials:
            print(f"  Username: {username} | Password: {password}")


if __name__ == '__main__':
    seed_database()
