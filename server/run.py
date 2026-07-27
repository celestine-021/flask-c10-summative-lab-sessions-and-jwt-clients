#!/usr/bin/env python3
"""Flask application entry point"""

import os
import sys

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make models available in flask shell"""
    from app.models import User, Note
    return {'db': db, 'User': User, 'Note': Note}


if __name__ == '__main__':
    app.run(debug=True, port=5555)
