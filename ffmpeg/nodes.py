from __future__ import unicode_literals

from builtins import object
import hashlib
import json


class Node(object):
    """Node base"""
    def __init__(self, parents, name, *args, **kwargs):
        parent_hashes = [hash(parent) for parent in parents]
        assert len(parent_hashes) == len(set(parent_hashes)), 'Same node cannot be included as parent multiple times'
        self._parents = parents
        self._hash = None
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        formatted_props = ['{}'.format(arg) for arg in self._args]
        formatted_props += ['{}={!r}'.format(key, self._kwargs[key]) for key in sorted(self._kwargs)]
        return '{}({})'.format(self._name, ','.join(formatted_props))

    def __hash__(self):
        if self._hash is None:
            self._update_hash()
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def _update_hash(self):
        props = {'args': self._args, 'kwargs': self._kwargs}
        props_str = json.dumps(props, sort_keys=True).encode('utf-8')
        my_hash = hashlib.md5(props_str).hexdigest()
        parent_hashes = [str(hash(parent)) for parent in self._parents]
        hashes = parent_hashes + [my_hash]
        hashes_str = ','.join(hashes).encode('utf-8')
        hash_str = hashlib.md5(hashes_str).hexdigest()
        self._hash = int(hash_str, base=16)


class InputNode(Node):
    """InputNode type"""
    def __init__(self, name, *args, **kwargs):
        super(InputNode, self).__init__(parents=[], name=name, *args, **kwargs)


class FilterNode(Node):
    """FilterNode"""
    def _get_filter(self):
        params_text = self._name
        arg_params = ['{}'.format(arg) for arg in self._args]
        kwarg_params = ['{}={}'.format(k, self._kwargs[k]) for k in sorted(self._kwargs)]
        params = arg_params + kwarg_params
        if params:
            params_text += '={}'.format(':'.join(params))
        return params_text


class OutputNode(Node):
    """OutputNode"""
    pass


class GlobalNode(Node):
    def __init__(self, parent, name, *args, **kwargs):
        assert isinstance(parent, OutputNode), 'Global nodes can only be attached after output nodes'
        super(GlobalNode, self).__init__([parent], name, *args, **kwargs)


def operator(node_classes={Node}, name=None):
    def decorator(func):
        func_name = name or func.__name__
        [setattr(node_class, func_name, func) for node_class in node_classes]
        return func
    return decorator
