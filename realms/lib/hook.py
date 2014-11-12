from flask.ext.sqlalchemy import DeclarativeMeta

from functools import wraps


def hook_func(name, fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        for hook, a, kw in self.__class__._pre_hooks.get(name) or []:
            hook(*args, **kwargs)

        rv = fn(self, *args, **kwargs)

        # Attach return value for post hooks
        kwargs.update(dict(rv=rv))

        for hook, a, kw in self.__class__._post_hooks.get(name) or []:
            hook(*args, **kwargs)

        return rv
    return wrapper


class HookMixinMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(HookMixinMeta, cls).__new__

        for key, value in attrs.items():
            if callable(value):
                attrs[key] = hook_func(key, value)

        return super_new(cls, name, bases, attrs)


class HookMixin(object):
    __metaclass__ = HookMixinMeta

    _pre_hooks = {}
    _post_hooks = {}

    @classmethod
    def after(cls, method_name):
        def outer(f, *args, **kwargs):
            cls._post_hooks.setdefault(method_name, []).append((f, args, kwargs))
            return f
        return outer

    @classmethod
    def before(cls, method_name):
        def outer(f, *args, **kwargs):
            cls._pre_hooks.setdefault(method_name, []).append((f, args, kwargs))
            return f
        return outer


class HookModelMeta(DeclarativeMeta, HookMixinMeta):
    pass


