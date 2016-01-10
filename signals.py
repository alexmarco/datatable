# -*- coding: utf-8 -*-


class Signal(list):
    """Implement the classical 'signal/slot' pattern."""
    def __call__(self, *args, **kwargs):
        """"""
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Signal(%s)" % list.__repr__(self)
