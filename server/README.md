# Flask Backend API - Notes App

A secure Flask API backend with session-based authentication and note management for a productivity application.

## Features

- ✅ User registration and authentication (session-based)
- ✅ Password encryption using bcrypt
- ✅ User-owned note resources (CRUD operations)
- ✅ Pagination support for notes list
- ✅ Protected routes (authentication required)
- ✅ Cross-origin resource sharing (CORS) enabled
- ✅ Database seeding with sample data
- ✅ Comprehensive error handling

## Tech Stack

- **Framework**: Flask 2.2.2
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask Sessions + Bcrypt
- **Validation**: Marshmallow
- **Testing**: Pytest
- **Migration**: Flask-Migrate

## Installation

### Prerequisites
- Python 3.8.13 or higher
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask-c10-summative-lab-sessions-and-jwt-clients/server
   ```

2. **Create a Python virtual environment**
   ```bash
   pipenv install --python 3.8
   ```
   
   Or using venv:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Activate the virtual environment**
   ```bash
   pipenv shell  # If using pipenv
   ```

4. **Initialize the database**
   ```bash
   python run.py  # This will create the database
   ```

5. **Seed the database with sample data**
   ```bash
   python seed.py
   ```

## Running the Application

```bash
python run.py
```

The API will be available at `http://localhost:5555`

## API Endpoints

### Authentication Routes

#### POST `/signup`
Register a new user and start a session.

**Request Body:**
```json
{
  "username": "string (min 3 chars)",
  "password": "string (min 6 chars)",
  "password_confirmation": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "alice",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Error Responses:**
- `400`: Missing required fields or validation failed
- `422`: Username already exists

---

#### POST `/login`
Authenticate an existing user and start a session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "alice",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Error Responses:**
- `400`: Missing username or password
- `401`: Invalid credentials

---

#### GET `/check_session`
Check if a user is currently logged in.

**Headers:** None required

**Response (200) - If logged in:**
```json
{
  "id": 1,
  "username": "alice",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Response (200) - If not logged in:**
```json
{}
```

---

#### DELETE `/logout`
End the user's session.

**Headers:** None required

**Response (200):**
```json
{}
```

---

### Note Resource Routes

All note routes require authentication (user must be logged in).

#### GET `/notes`
Retrieve all notes for the current user with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "My First Note",
      "content": "This is the content...",
      "category": "Personal",
      "is_pinned": false,
      "user_id": 1,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 25,
  "pages": 3
}
```

**Error Responses:**
- `401`: Unauthorized (not logged in)

---

#### POST `/notes`
Create a new note.

**Request Body:**
```json
{
  "title": "string (required)",
  "content": "string (required)",
  "category": "string (optional)"
}
```

**Response (201):**
```json
{
  "id": 2,
  "title": "New Note",
  "content": "Note content...",
  "category": "Work",
  "is_pinned": false,
  "user_id": 1,
  "created_at": "2024-01-01T13:00:00",
  "updated_at": "2024-01-01T13:00:00"
}
```

**Error Responses:**
- `400`: Missing or invalid fields
- `401`: Unauthorized

---

#### GET `/notes/<note_id>`
Retrieve a specific note by ID.

**Response (200):**
```json
{
  "id": 1,
  "title": "My Note",
  "content": "...",
  "category": "Personal",
  "is_pinned": false,
  "user_id": 1,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Error Responses:**
- `401`: Unauthorized
- `403`: Forbidden (note belongs to another user)
- `404`: Note not found

---

#### PATCH `/notes/<note_id>`
Update a note.

**Request Body (all fields optional):**
```json
{
  "title": "string",
  "content": "string",
  "category": "string",
  "is_pinned": "boolean"
}
```

**Response (200):** Updated note object

**Error Responses:**
- `400`: Invalid input
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Note not found

---

#### DELETE `/notes/<note_id>`
Delete a note.

**Response (200):**
```json
{}
```

**Error Responses:**
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Note not found

---

## Database Schema

### Users Table
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `password_hash` (String, Not Null)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Notes Table
- `id` (Integer, Primary Key)
- `title` (String, Not Null)
- `content` (Text, Not Null)
- `category` (String, Optional)
- `is_pinned` (Boolean, Default: False)
- `user_id` (Integer, Foreign Key → Users.id)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Testing the API

### Using cURL

```bash
# Sign up
curl -X POST http://localhost:5555/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice123","password_confirmation":"alice123"}'

# Login
curl -X POST http://localhost:5555/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice123"}'

# Check session
curl -X GET http://localhost:5555/check_session

# Create a note
curl -X POST http://localhost:5555/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"My Note","content":"Note content","category":"Personal"}'

# Get all notes (with pagination)
curl -X GET http://localhost:5555/notes?page=1&per_page=5

# Get a specific note
curl -X GET http://localhost:5555/notes/1

# Update a note
curl -X PATCH http://localhost:5555/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'

# Delete a note
curl -X DELETE http://localhost:5555/notes/1

# Logout
curl -X DELETE http://localhost:5555/logout
```

### Using the Provided Frontend

1. Navigate to the client directory:
   ```bash
   cd ../client-with-sessions
   npm install
   npm start
   ```

2. The frontend will connect to `http://localhost:5555` and you can test the full auth flow.

## Test Credentials

After running `seed.py`, use these credentials to test:

| Username | Password |
|----------|----------|
| alice    | alice123 |
| bob      | bob123   |
| charlie  | charlie123 |

## Project Structure

```
server/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # User and Note models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       └── resources.py     # Note CRUD endpoints
├── run.py                   # Application entry point
├── seed.py                  # Database seeding script
├── Pipfile                  # Python dependencies
├── app.db                   # SQLite database (created on first run)
└── README.md                # This file
```

## Error Handling

The API returns consistent error responses:

```json
{
  "errors": ["Error message here"]
}
```

**Common Status Codes:**
- `200`: Success (GET, PATCH, DELETE)
- `201`: Created (POST)
- `400`: Bad Request (validation error)
- `401`: Unauthorized (not logged in)
- `403`: Forbidden (accessing another user's data)
- `404`: Not Found
- `422`: Unprocessable Entity (duplicate username)
- `500`: Server Error

## Security Features

- ✅ Passwords hashed with bcrypt
- ✅ Session-based authentication
- ✅ CORS protection
- ✅ HTTPOnly session cookies
- ✅ User data isolation (users can only access their own notes)
- ✅ Input validation and sanitization

## Development Notes

- The app uses SQLite by default, but can be configured to use other databases via `DATABASE_URL` environment variable
- Sessions are stored server-side and cookies are used for client identification
- All timestamps are in UTC ISO format
- Pagination is limited to a maximum of 100 items per page for performance

## Troubleshooting

### Port Already in Use
If port 5555 is already in use, modify the port in `run.py`:
```python
app.run(debug=True, port=5556)  # Change 5555 to 5556
```

### Database Issues
To reset the database, delete `app.db` and run:
```bash
python run.py
python seed.py
```

### CORS Errors
Make sure the frontend is running on `http://localhost:3000` (JWT client) or `http://localhost:5555` is configured correctly in the frontend's proxy settings.

## Git Workflow

```bash
# Check branch
git branch

# Add changes
git add .

# Commit
git commit -m "Add Flask backend implementation"

# Push to main
git push origin main  # or master
```

## Author

Student - Moringa School

## License

This project is part of the Moringa School curriculum.
