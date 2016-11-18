Parseable [![Build Status](https://travis-ci.org/nlm/parseable.svg?branch=master "Build Status")]() [![License: MIT](https://img.shields.io/github/license/nlm/parseable.svg)](https://opensource.org/licenses/MIT)
=========

A python library to make easier the parsing of data structures into objects,
with strong validation.

This has been originally developed to parse messages from the Telegram Bot API
(https://core.telegram.org/bots/api/)

Data validation is done using 'schema' (https://pypi.python.org/pypi/schema)

Software in Development
-----------------------

*Warning*: This is software is in beta stage, it is subject to changes

Basic Usage
-----------

Basic usage is simple. You call the `parseable` function, providing
a class name and a validation schema (see the `schema` package documentation
for more informations)

```python
>>> from parseable import parseable
>>> User = parseable('User', {'id': int, 'name': str})
>>> user = User({'id': 2, 'name': 'Joe'})
>>> user == {'id': 2, 'name': 'Joe'}
True
>>> isinstance(user, User)
True

```

If the data doesn't match the schema, a `SchemaError` exception is raised

```python
>>> from parseable import SchemaError
>>> try:
...     baduser = User({'a wrong': 'data structure'})
... except SchemaError as exc:
...     print(exc)
Missing keys: 'id', 'name'

```

Recursive Parsing
-----------------

This library allow you to include parseables into other parseables,
so you can define objects and include them in each other.
This makes nested api objects easier to parse.

```python
>>> from parseable import parseable, Use
>>> User = parseable('User', {'id': int, 'name': str})
>>> Message = parseable('Message', {'from': Use(User), 'text': str})
>>> message = Message({'from': {'id': 2, 'name': 'Joe'}, 'text': 'Hello'})
>>> message == {'text': 'Hello', 'from': {'id': 2, 'name': 'Joe'}}
True

```

You can also recurse on the current object itself,
using the special class `Self`

```python
>>> from parseable import parseable, Use, Optional, Self
>>> User = parseable('User', {'id': int, Optional('parent'): Use(Self)})
>>> user = User({'id': 2, 'parent': {'id': 1}})
>>> user == {'id': 2, 'parent': {'id': 1}}
True

```

Defaults
--------

As with `schema.Schema`, you can use defaults:

```python
>>> from parseable import parseable, Use, Optional, Self
>>> DefDemo = parseable('DefDemo', {Optional('id', default=4): int})
>>> defdemo = DefDemo({'id': 2})
>>> defdemo['id']
2
>>> defdemo = DefDemo({})
>>> defdemo['id']
4

```

Producing Content
-----------------

Parsing text from an API is cool, but you also have to reply sometimes.
You can use the exact same objects to do that.

```python
>>> from parseable import parseable, Use
>>> User = parseable('User', {'id': int, 'name': str})
>>> Message = parseable('Message', {'from': Use(User), 'text': str})
>>> # defining objects
>>> user = User({'id': 2, 'name': 'Joe'})
>>> message = Message({'from': user.data, 'text': 'Hello'})
>>> message == {'text': 'Hello', 'from': {'id': 2, 'name': 'Joe'}}
True

```

You can then encode this and send it to your API endpoint.
This way, you can guarantee the correctness of data structures
on input and output operations.

Value Expansion
---------------

You can use parseable object instances as any other object, but sometimes,
you really need the real underlying data structures types. For example,
when you want to use operators or when you want to dump
data using the json module.

### Using type-specific operators:

```python
>>> from parseable import parseable, expand
>>> Int = parseable('Int', int)
>>> integer = Int(3)
>>> try:
...     print(integer * integer)
... except TypeError as err:
...     print(err)
...
unsupported operand type(s) for *: 'Int' and 'Int'
>>> print(expand(integer) * expand(integer))
9

```

### Encoding objects as JSON

```python
>>> import json
>>> message = Message({'from': user.data, 'text': 'Hello'})
>>> isinstance(message, dict)
False
>>> from parseable import expand
>>> message = expand(message)
>>> isinstance(message, dict)
True
>>> json.dumps(message) # doctest: +SKIP
'{"text": "Hello", "from": {"id": 2, "name": "Joe"}}'

```

Note: expand recurses on lists and dicts, so if you have nested Parseables,
the whole structure will be expanded.

Types and inheritance
---------------------

All the objects as subclasses of parseable.Parseable, you can check
if an object is a parseable like this:

```python
>>> from parseable import parseable, Parseable
>>> User = parseable('User', {'id': int, 'name': str})
>>> issubclass(User, Parseable)
True

```

Some Parseables will verify as Sequence or Mapping, depending on the Schema
that you create them with.

```python
>>> from parseable import parseable
>>> from collections import Sequence, Mapping
>>>
>>> seq_schema = [int]
>>> MySeq = parseable('MySeq', seq_schema)
>>> myseq = MySeq([1, 2, 3])
>>> isinstance(seq_schema, Sequence)
True
>>> isinstance(myseq, Sequence)
True
>>>
>>> map_schema = {str: str}
>>> MyMap = parseable('MyMap', map_schema)
>>> mymap = MyMap({'test': 'ok'})
>>> isinstance(map_schema, Mapping)
True
>>> isinstance(mymap, Mapping)
True

```
