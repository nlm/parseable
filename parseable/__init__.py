from schema import Schema, Optional, Use, SchemaError


class Self(object): pass


class _Parseable(object):
    '''
    '''

    _schema = None

    def __init__(self, data):
        '''
        initializes the class

        :param data: the data to validate with this object
        '''
        self._data = Schema(self._schema, ignore_extra_keys=True).validate(data)

    def __getattr__(self, attr):
        assert attr != '_data'
        return self._data[attr]

    @property
    def data(self):
        '''
        get the validated data from this object

        :return: the validated data
        '''
        return self._expand_parseables(self._data)

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
        elif isinstance(data, _Parseable):
            return data.data
        else:
            return data

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.data)


def _replace_self(cls, data):
    '''
    Replace instances of 'Self' by own class in the current schema
    This makes recursive parsing possible
    '''
    if isinstance(data, list):
        for idx, val in enumerate(data):
            if val is Self:
                data[idx] = cls
            else:
                _replace_self(cls, val)
    elif isinstance(data, dict):
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

def parseable(name, schema):
    '''
    creates a new Parseable class

    :param name: the name of the new class to create
    :param schema: the 'schema'-compliant schema
    :type name: str
    :type schema: Schema
    :return: the customized Parseable Class
    '''
    class Parseable(_Parseable):
        _schema = schema
    _replace_self(Parseable, Parseable._schema)
    Parseable.__name__ = name
    return Parseable
