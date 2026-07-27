import pytest
from app import create_app, db
from app.models import User, Note


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI."""
    return app.test_cli_runner()


class TestAuth:
    """Authentication tests"""
    
    def test_signup_success(self, client):
        """Test successful user signup"""
        response = client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        assert response.status_code == 201
        assert response.json['username'] == 'testuser'
        assert 'password' not in response.json
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing fields"""
        response = client.post('/signup', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
    
    def test_signup_password_mismatch(self, client):
        """Test signup with mismatched passwords"""
        response = client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'different'
        })
        assert response.status_code == 400
    
    def test_signup_short_password(self, client):
        """Test signup with password too short"""
        response = client.post('/signup', json={
            'username': 'testuser',
            'password': '123',
            'password_confirmation': '123'
        })
        assert response.status_code == 400
    
    def test_signup_duplicate_username(self, client):
        """Test signup with existing username"""
        # First signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Second signup with same username
        response = client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        assert response.status_code == 422
    
    def test_login_success(self, client):
        """Test successful login"""
        # Signup first
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Login
        response = client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert response.json['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """Test login with wrong password"""
        # Signup first
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Login with wrong password
        response = client.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    def test_check_session_not_logged_in(self, client):
        """Test check_session when not logged in"""
        response = client.get('/check_session')
        assert response.status_code == 200
        assert response.json == {}
    
    def test_check_session_logged_in(self, client):
        """Test check_session when logged in"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Check session
        response = client.get('/check_session')
        assert response.status_code == 200
        assert response.json['username'] == 'testuser'
    
    def test_logout(self, client):
        """Test logout"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Check session (should be logged in)
        response = client.get('/check_session')
        assert response.status_code == 200
        assert 'username' in response.json
        
        # Logout
        response = client.delete('/logout')
        assert response.status_code == 200
        
        # Check session again (should be logged out)
        response = client.get('/check_session')
        assert response.status_code == 200
        assert response.json == {}


class TestNotes:
    """Note CRUD tests"""
    
    def test_create_note_unauthorized(self, client):
        """Test creating note without login"""
        response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        assert response.status_code == 401
    
    def test_create_note_success(self, client):
        """Test successful note creation"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create note
        response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content',
            'category': 'Personal'
        })
        assert response.status_code == 201
        assert response.json['title'] == 'Test Note'
        assert response.json['content'] == 'Test content'
    
    def test_create_note_missing_fields(self, client):
        """Test creating note with missing fields"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create note without content
        response = client.post('/notes', json={
            'title': 'Test Note'
        })
        assert response.status_code == 400
    
    def test_get_notes(self, client):
        """Test getting all notes"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create notes
        client.post('/notes', json={
            'title': 'Note 1',
            'content': 'Content 1'
        })
        client.post('/notes', json={
            'title': 'Note 2',
            'content': 'Content 2'
        })
        
        # Get notes
        response = client.get('/notes')
        assert response.status_code == 200
        assert len(response.json['notes']) == 2
    
    def test_get_notes_pagination(self, client):
        """Test pagination on get notes"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create notes
        for i in range(15):
            client.post('/notes', json={
                'title': f'Note {i}',
                'content': f'Content {i}'
            })
        
        # Get notes with pagination
        response = client.get('/notes?page=1&per_page=10')
        assert response.status_code == 200
        assert len(response.json['notes']) == 10
        assert response.json['total'] == 15
        assert response.json['pages'] == 2
    
    def test_get_note_success(self, client):
        """Test getting a single note"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create note
        create_response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        note_id = create_response.json['id']
        
        # Get note
        response = client.get(f'/notes/{note_id}')
        assert response.status_code == 200
        assert response.json['title'] == 'Test Note'
    
    def test_get_note_not_found(self, client):
        """Test getting non-existent note"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Get non-existent note
        response = client.get('/notes/999')
        assert response.status_code == 404
    
    def test_update_note_success(self, client):
        """Test updating a note"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create note
        create_response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        note_id = create_response.json['id']
        
        # Update note
        response = client.patch(f'/notes/{note_id}', json={
            'title': 'Updated Note',
            'is_pinned': True
        })
        assert response.status_code == 200
        assert response.json['title'] == 'Updated Note'
        assert response.json['is_pinned'] == True
    
    def test_delete_note_success(self, client):
        """Test deleting a note"""
        # Signup
        client.post('/signup', json={
            'username': 'testuser',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Create note
        create_response = client.post('/notes', json={
            'title': 'Test Note',
            'content': 'Test content'
        })
        note_id = create_response.json['id']
        
        # Delete note
        response = client.delete(f'/notes/{note_id}')
        assert response.status_code == 200
        
        # Verify note is deleted
        response = client.get(f'/notes/{note_id}')
        assert response.status_code == 404
    
    def test_user_isolation(self, client):
        """Test that users cannot access each other's notes"""
        # Create first user and note
        client.post('/signup', json={
            'username': 'user1',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        create_response = client.post('/notes', json={
            'title': 'User1 Note',
            'content': 'User1 content'
        })
        note_id = create_response.json['id']
        
        # Logout
        client.delete('/logout')
        
        # Create second user
        client.post('/signup', json={
            'username': 'user2',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Try to access first user's note
        response = client.get(f'/notes/{note_id}')
        assert response.status_code == 403
