from computerwords.library import Library
from .basics import add_basics
from .html import add_html
from .links import add_links


stdlib = Library()
add_basics(stdlib)
add_html(stdlib)
