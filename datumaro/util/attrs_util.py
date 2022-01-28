# Copyright (C) 2020-2021 Intel Corporation
#
# SPDX-License-Identifier: MIT

from inspect import isclass

import attrs
import attrs.converters

def ensure_type(t, c=None):
    c = c or t
    def _converter(v):
        if not isinstance(v, t):
            v = c(v)
        return v
    return _converter

def ensure_type_kw(c):
    def converter(arg):
        if isinstance(arg, c):
            return arg
        else:
            return c(**arg)
    return converter

def optional_cast_with_default(cls, *, conv=None, factory=None):
    # Equivalent to:
    # attrs.converters.pipe(
    #     attrs.converters.optional(ensure_type(t, c)),
    #     attrs.converters.default_if_none(factory=f),
    # )
    #
    # But provides better performance (mostly, due to less function calls)

    factory = factory or cls
    conv = conv or cls

    def _conv(v):
        if v is None:
            v = factory()
        elif not isinstance(v, cls):
            v = conv(v)
        return v
    return _conv

def not_empty(inst, attribute, x):
    assert len(x) != 0, x


def default_if_none(conv):
    def validator(inst, attribute, value):
        default = attribute.default
        if value is None:
            if callable(default):
                value = default()
            elif isinstance(default, attrs.Factory):
                value = default.factory()
            else:
                value = default
        else:
            dst_type = None
            if attribute.type and isclass(attribute.type):
                dst_type = attribute.type
            elif conv and isclass(conv):
                dst_type = conv

            # Using isinstance with Generics leads to bad performance
            # https://stackoverflow.com/questions/42378726/why-is-checking-isinstancesomething-mapping-so-slow

            if not dst_type or not isinstance(value, dst_type):
                value = conv(value)
        setattr(inst, attribute.name, value)
    return validator
