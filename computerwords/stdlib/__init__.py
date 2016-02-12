from computerwords.library import Library
from .basics import add_basics
from .html import add_html


stdlib = Library()
add_basics(stdlib)
add_html(stdlib)
