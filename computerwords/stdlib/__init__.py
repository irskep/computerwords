from computerwords.library import Library
from .basics import add_basics
from .html import add_html
from .links import add_links
from .table_of_contents import add_table_of_contents
from .code import add_code
from .src_py import add_src_py


stdlib = Library()
add_basics(stdlib)
add_html(stdlib)
add_links(stdlib)
add_table_of_contents(stdlib)
add_code(stdlib)
add_src_py(stdlib)
