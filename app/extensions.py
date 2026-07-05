"""Shared Flask extension instances.

Extensions live here (not in __init__.py) so any module can import them
without touching the app package itself — avoids circular imports.
"""

from flask_flatpages import FlatPages

# App-wide blog store; loaded from posts/ via init_app in create_app.
pages = FlatPages()
