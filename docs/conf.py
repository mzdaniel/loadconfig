"""documentation config"""
import sys
sys.path.append('..')
try:
    from loadconfig import __version__
except Exception:
    __version__ = ''

try:
    import sphinx_bootstrap_theme
except ImportError as e:
    pass

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'documentation'
author = 'Daniel Mizyrycki'
copyright = '2015, %s' % (author)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = __version__
release = __version__

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

extensions = ['sphinx.ext.doctest']

# --  Options for pdflatex output -----------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
latex_documents = [
    (master_doc, 'loadconfig.tex', 'Loadconfig Documentation',
     author, 'manual')]


# Use bootstrap theme if available. Assumed readthedocs otherwise
if 'sphinx_bootstrap_theme' in locals():
    html_theme = 'bootstrap'
    html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
    html_theme_options = {
        'globaltoc_depth': 3,
        'bootswatch_theme': "flatly"}

# Output file base name for HTML help builder.
htmlhelp_basename = 'documentation'

templates_path = ['_templates']

html_sidebars = {
    '*': ['sidebartoc.html', 'searchbox.html']}

# Include badges without warnings.
# https://github.com/sphinx-doc/sphinx/issues/1895

from docutils.utils import get_source_line
import sphinx.environment


def _warn_node(self, msg, node):
    if not msg.startswith('nonlocal image URI found:'):
        self._warnfunc(msg, '%s:%s' % get_source_line(node))

sphinx.environment.BuildEnvironment.warn_node = _warn_node
