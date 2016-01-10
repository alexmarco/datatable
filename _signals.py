# -*- coding: utf-8 -*-

###############################################################################
# SIGNALING
###############################################################################

from weakref import *
import inspect


class _Signal:
    def __init__(self, **env):
        self.slots = []
        # for keeping references to _WeakMethod_FuncHost objects.
        # If we didn't, then the weak references would die for
        # non-method slots that we've created.
        self.funchost = []

    def __call__(self, sender, **kwargs):
        for i, slot in enumerate(self.slots):
            if slot['handler'] is not None:
                if slot['sender'] is None or slot['sender'] == sender:
                    slot(sender, **kwargs)
            else:
                del self.slots[i]

    def connect(self, slot, sender=None):
        self.disconnect(slot)
        if inspect.ismethod(slot):
            sh = SignalHandler()
            self.slots.append({'handler': WeakMethod(slot), 'sender': sender})
        else:
            o = _WeakMethod_FuncHost(slot)
            self.slots.append({'handler': WeakMethod(o.func),
                               'sender': sender})
            # we stick a copy in here just to keep the instance alive
            self.funchost.append(o)

    def disconnect(self, slot):
        try:
            for i, wm in enumerate(self.slots):
                if inspect.ismethod(slot):
                    if wm.f == slot.im_func and wm.c() == slot.im_self:
                        del self.slots[i]
                        return
                else:
                    if wm.c().hostedFunction == slot:
                        del self.slots[i]
                        return
        except:
            pass

    def disconnectAll(self):
        self.slots = []
        self.funchost = []


class _WeakMethod_FuncHost:
    def __init__(self, func):
        self.hostedFunction = func

    def func(self, sender, **kwargs):
        self.hostedFunction(sender, **kwargs)

# this class was generously donated by a poster on ASPN (aspn.activestate.com)


class WeakMethod:
    def __init__(self, f):
        self.f = f.im_func
        self.c = ref(f.im_self)

    def __call__(self, sender, **kwargs):
        if self.c() is not None:
            self.f(self.c(), sender, **kwargs)


# def hashable_identity(obj):
#     if hasattr(obj, '__func__'):
#         return (id(obj.__func__), id(obj.__self__))
#     elif hasattr(obj, 'im_func'):
#         return (id(obj.im_func), id(obj.im_self))
#     elif isinstance(obj, basestring):
#         return obj
#     else:
#         return id(obj)


# class SignalHandler(object):
#     def __init__(self, callable_handler, sender=None):
#         self.callable_handler = callable_handler
#         self.sender = sender
#         self.id = hashable_identity(sender)


class Signal(list):

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Signal(%s)" % list.__repr__(self)
