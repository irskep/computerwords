from computerwords.library import Library
from .basics import add_basics
from .html import add_html
from .links import add_links
from .table_of_contents import add_table_of_contents


stdlib = Library()
add_basics(stdlib)
add_html(stdlib)
add_links(stdlib)
add_table_of_contents(stdlib)
