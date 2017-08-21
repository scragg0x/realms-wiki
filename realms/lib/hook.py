from __future__ import absolute_import
from six import with_metaclass

from functools import wraps

from flask_sqlalchemy import DeclarativeMeta


def hook_func(name, fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        for hook, a, kw in self.__class__._pre_hooks.get(name) or []:
            hook(self, *args, **kwargs)

        rv = fn(self, *args, **kwargs)

        # Attach return value for post hooks
        kwargs.update(dict(rv=rv))

        for hook, a, kw in self.__class__._post_hooks.get(name) or []:
            hook(self, *args, **kwargs)

        return rv
    return wrapper


class HookMixinMeta(type):
    def __new__(cls, name, bases, attrs):
        hookable = []
        for key, value in attrs.items():
            # Disallow hooking methods which start with an underscore (allow __init__ etc. still)
            if key.startswith('_') and not key.startswith('__'):
                continue
            if callable(value):
                attrs[key] = hook_func(key, value)
                hookable.append(key)
        attrs['_hookable'] = hookable

        return super(HookMixinMeta, cls).__new__(cls, name, bases, attrs)


class HookMixin(with_metaclass(HookMixinMeta, object)):
    _pre_hooks = {}
    _post_hooks = {}
    _hookable = []

    @classmethod
    def after(cls, method_name):
        assert method_name in cls._hookable, "'%s' not a hookable method of '%s'" % (method_name, cls.__name__)

        def outer(f, *args, **kwargs):
            cls._post_hooks.setdefault(method_name, []).append((f, args, kwargs))
            return f
        return outer

    @classmethod
    def before(cls, method_name):
        assert method_name in cls._hookable, "'%s' not a hookable method of '%s'" % (method_name, cls.__name__)

        def outer(f, *args, **kwargs):
            cls._pre_hooks.setdefault(method_name, []).append((f, args, kwargs))
            return f
        return outer


class HookModelMeta(DeclarativeMeta, HookMixinMeta):
    pass


