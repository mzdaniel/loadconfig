"""documentation config"""

from os.path import dirname, abspath
import sphinx_bootstrap_theme
import sys
sys.path.insert(0, '{}'.format(dirname(dirname(abspath(__file__)))))
__version__ = '0.1'

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'documentation'
copyright = '2015, Daniel Mizyrycki'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = __version__
release = __version__

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

extensions = ['sphinx.ext.doctest', 'rst2pdf.pdfbuilder']

pdf_documents = [('index', 'loadconfig', 'loadconfig docs',
    'Daniel Mizyrycki')]

# The theme to use for HTML and HTML Help pages.
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
