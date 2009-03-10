"""
Dict: a Variable wrapper for a dictionary.
"""

#public symbols
__all__ = []
__version__ = "0.1"

from openmdao.main.variable import Variable, UNDEFINED
from openmdao.main.vartypemap import add_var_type_map

class Dict(Variable):
    """A dictionary Variable"""

    def __init__(self, name, parent, iostatus, ref_name=None,
                 default=UNDEFINED, desc=None):
        super(Dict, self).__init__(name, parent, iostatus, val_type=dict,
                                   ref_name=ref_name,
                                   default=default, desc=desc)
        self.set_default(default)

add_var_type_map(Dict, dict)
