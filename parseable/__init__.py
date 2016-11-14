from abc import ABCMeta
from schema import Schema, Optional, Use, SchemaError
try:
    from collections.abc import Mapping, Sequence
except ImportError:
    from collections import Mapping, Sequence


class Self(object):
    '''
    Object to represent a class in itself before it's instantiated
    '''
    pass


class Parseable(object):
    '''
    Base class for Parseables

    Must not be instantiated or subclassed directly
    '''
    _schema = None
    _schema_processed = False

    def __init__(self, data):
        '''
        initializes the class

        :param data: the data to validate with this object
        '''
        assert self._schema_processed is True
        self._data = Schema(self._schema, ignore_extra_keys=True).validate(data)
        self._data = self._expand_parseables(self._data)

    @property
    def data(self):
        '''
        get the validated data from this object

        :return: the validated data
        '''
        return self._data

    @property
    def schema(self):
        '''
        get the schema from this object

        :return: the schema which this object validates data against
        '''
        return self._schema

    @classmethod
    def _expand_parseables(cls, data):
        if isinstance(data, list):
            return [cls._expand_parseables(elt) for elt in data]
        elif isinstance(data, dict):
            return {key: cls._expand_parseables(val)
                    for key, val in data.items()}
        elif isinstance(data, Parseable):
            return data.data
        else:
            return data

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.data)


class MappingParseable(Parseable, Mapping):
    '''
    Base class for list-like Parseables

    Must not be instantiated or subclassed directly
    '''

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return self._data.__len__()


class SequenceParseable(Parseable, Sequence):
    '''
    Base class for dict-like Parseables

    Must not be instantiated or subclassed directly
    '''

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __len__(self):
        return self._data.__len__()


class DefaultParseable(Parseable):
    '''
    Base class for other types of Parseables

    Must not be instantiated or subclassed directly
    '''
    pass


def _replace_self(cls, data):
    '''
    Replace instances of 'Self' by own class in the current schema
    This makes recursive parsing possible
    '''
    if isinstance(data, Sequence):
        for idx, val in enumerate(data):
            if val is Self:
                data[idx] = cls
            else:
                _replace_self(cls, val)
    elif isinstance(data, Mapping):
        for key, val in data.items():
            if val is Self:
                data[key] = cls
            else:
                _replace_self(cls, val)
    elif isinstance(data, Use):
        if data._callable is Self:
            data._callable = cls
        else:
            _replace_self(cls, data._callable)
    elif isinstance(data, Schema):
        if data._schema is Self:
            data._schema = cls
        else:
            _replace_self(cls, data._schema)

    if issubclass(cls, Parseable):
        cls._schema_processed = True

def parseable(name, schema):
    '''
    creates a new Parseable class

    :param name: the name of the new class to create
    :param schema: the 'schema'-compliant schema
    :type name: str
    :type schema: Schema
    :return: the customized Parseable Class
    '''
    if isinstance(schema, Mapping):
        base_class = MappingParseable
    elif isinstance(schema, Sequence):
        base_class = SequenceParseable
    else:
        base_class = DefaultParseable

    cls = type(name, (base_class,), {'_schema': schema})
    _replace_self(cls, cls._schema)
    return cls
