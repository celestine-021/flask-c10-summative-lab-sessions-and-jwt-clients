from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Note
from functools import wraps
from sqlalchemy import desc

resources_bp = Blueprint('resources', __name__)


def login_required(f):
    """Decorator to require login for resource routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'errors': ['Unauthorized']}), 401
        
        user = User.query.get(user_id)
        if not user:
            session.pop('user_id', None)
            return jsonify({'errors': ['Unauthorized']}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# NOTES CRUD ENDPOINTS

@resources_bp.route('/notes', methods=['GET'])
@login_required
def get_notes():
    """Get all notes for the current user with pagination"""
    try:
        user_id = session.get('user_id')
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Query notes
        pagination = Note.query.filter_by(user_id=user_id).order_by(
            desc(Note.is_pinned), 
            desc(Note.updated_at)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'notes': [note.to_dict() for note in pagination.items],
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@resources_bp.route('/notes', methods=['POST'])
@login_required
def create_note():
    """Create a new note"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # Validate input
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'errors': ['Title and content are required']}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category = data.get('category', '').strip() or None
        
        if not title or len(title) < 1:
            return jsonify({'errors': ['Title cannot be empty']}), 400
        
        if not content or len(content) < 1:
            return jsonify({'errors': ['Content cannot be empty']}), 400
        
        # Create note
        note = Note(
            title=title,
            content=content,
            category=category,
            user_id=user_id
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@resources_bp.route('/notes/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """Get a single note"""
    try:
        user_id = session.get('user_id')
        note = Note.query.get(note_id)
        
        if not note:
            return jsonify({'errors': ['Note not found']}), 404
        
        if note.user_id != user_id:
            return jsonify({'errors': ['Unauthorized']}), 403
        
        return jsonify(note.to_dict()), 200
    
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@resources_bp.route('/notes/<int:note_id>', methods=['PATCH'])
@login_required
def update_note(note_id):
    """Update a note"""
    try:
        user_id = session.get('user_id')
        note = Note.query.get(note_id)
        
        if not note:
            return jsonify({'errors': ['Note not found']}), 404
        
        if note.user_id != user_id:
            return jsonify({'errors': ['Unauthorized']}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            title = data.get('title', '').strip()
            if not title:
                return jsonify({'errors': ['Title cannot be empty']}), 400
            note.title = title
        
        if 'content' in data:
            content = data.get('content', '').strip()
            if not content:
                return jsonify({'errors': ['Content cannot be empty']}), 400
            note.content = content
        
        if 'category' in data:
            category = data.get('category', '').strip() or None
            note.category = category
        
        if 'is_pinned' in data:
            note.is_pinned = bool(data.get('is_pinned', False))
        
        db.session.commit()
        
        return jsonify(note.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@resources_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete a note"""
    try:
        user_id = session.get('user_id')
        note = Note.query.get(note_id)
        
        if not note:
            return jsonify({'errors': ['Note not found']}), 404
        
        if note.user_id != user_id:
            return jsonify({'errors': ['Unauthorized']}), 403
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500
