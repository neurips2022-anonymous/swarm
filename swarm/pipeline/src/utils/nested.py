""" utility functions that help you process nested dicts, tuples, lists and namedtuples """
import torch

from src.utils.tensor_descr import BatchTensorDescriptor, TensorDescriptor


def nested_compare(t, u):
    """
    Return whether nested structure of t1 and t2 matches.
    """
    if isinstance(t, (list, tuple)):
        if not isinstance(u, type(t)):
            return False
        if len(t) != len(u):
            return False
        for a, b in zip(t, u):
            if not nested_compare(a, b):
                return False
        return True

    if isinstance(t, dict):
        if not isinstance(u, dict):
            return False
        if set(t.keys()) != set(u.keys()):
            return False
        for k in t:
            if not nested_compare(t[k], u[k]):
                return False
        return True

    # if isinstance(t, torch.Tensor):
    #     if isinstance(u, torch.Tensor) and t.size() != u.size():
    #         return False
    #     if isinstance(u, TensorDescriptor) and t.size() != u.size:
    #         return False
    #     if isinstance(u, BatchTensorDescriptor) and t.size()[1:] != u.size[1:]:
    #         return False

    # if hasattr(t, '__iter__'):
    #     print(t, u)
    #     if not hasattr(u, '__iter__'):
    #         return False
    #     for a, b in zip(t, u):
    #         if not nested_compare(a, b):
    #             return False

    else:
        return True


def nested_flatten(t):
    """
    Turn nested list/tuple/dict into a flat iterator.
    """
    if isinstance(t, (list, tuple)):
        for x in t:
            yield from nested_flatten(x)
    elif isinstance(t, dict):
        for k, v in sorted(t.items()):
            yield from nested_flatten(v)
    else:
        yield t


def nested_pack(flat, structure):
    """
    Restore nested structure from flattened state
    :param flat: result of nested_flatten
    :param structure: used as example when recovering structure
    :returns: nested structure like :structure: filled with elements of :flat:
    """
    return _nested_pack(iter(flat), structure)


def _nested_pack(flat_iter, structure):
    if is_namedtuple(structure):
        return type(structure)(*[_nested_pack(flat_iter, x) for x in structure])
    elif isinstance(structure, (list, tuple)):
        return type(structure)(_nested_pack(flat_iter, x) for x in structure)
    elif isinstance(structure, dict):
        return {k: _nested_pack(flat_iter, v) for k, v in sorted(structure.items())}
    else:
        return next(flat_iter)


def is_namedtuple(x):
    """Checks if x is a namedtuple instance. Taken from https://stackoverflow.com/a/2166841 ."""
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


def nested_map(fn, *t):
    # Check arguments.
    if not t:
        raise ValueError("Expected 2+ arguments, got 1")
    for i in range(1, len(t)):
        if not nested_compare(t[0], t[i]):
            msg = "Nested structure of %r and %r differs"
            raise ValueError(msg % (t[0], t[i]))

    # Map.
    flat = map(nested_flatten, t)
    return nested_pack(map(fn, *flat), t[0])
