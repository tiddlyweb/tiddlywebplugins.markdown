"""
Markdown rendering subsystem.
"""

# for sake of making config calls clean, we import render
# into this space
from .render import render as markdown_render

# keep linters happy
render = markdown_render
