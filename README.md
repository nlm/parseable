Parseable ![Build Status](https://travis-ci.org/nlm/parseable.svg?branch=master "Build Status") [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
=========

A python library to make easier the parsing of data structures into objects,
with strong validation.

This has been originally developed to parse messages from the Telegram Bot API
(https://core.telegram.org/bots/api/)

Data validation is done using 'schema' (https://pypi.python.org/pypi/schema)

Software in Development
-----------------------

Warning: This is software is in beta stage, it is subject to changes

Basic Usage
-----------

Basic usage is simple. You call the 'parseable' function, providing
a class name and a validation schema (see the 'schema' package documentation
for more informations)

```
>>> from parseable import parseable
>>> User = parseable('User', {'id': int, 'name': str})
>>> user = User({'id': 2, 'name': 'Joe'})
>>> user.data == {'id': 2, 'name': 'Joe'}
True

```

If the data doesn't match the schema, a SchemaError exception is raised

Recursive Parsing
-----------------

This library allow you to include parseables into other parseables,
so you can define objects and include them in each other.
This makes json objects easier to parse.

```
>>> from parseable import parseable, Use
>>> User = parseable('User', {'id': int, 'name': str})
>>> Message = parseable('Message', {'from': Use(User), 'text': str})
>>> message = Message({'from': {'id': 2, 'name': 'Joe'}, 'text': 'Hello'})
>>> message.data == {'text': 'Hello', 'from': {'id': 2, 'name': 'Joe'}}
True

```

You can also recurse on your own object, using the special class 'Self'

```
>>> from parseable import parseable, Use, Optional, Self
>>> User = parseable('User', {'id': int, Optional('parent'): Use(Self)})
>>> user = User({'id': 2, 'parent': {'id': 1}})
>>> user.data == {'id': 2, 'parent': {'id': 1}}
True

```

Defaults
--------

As with Schema, you can use defaults:

```
>>> from parseable import parseable, Use, Optional, Self
>>> DefDemo = parseable('DefDemo', {Optional('id', default=4): int})
>>> defdemo = DefDemo({'id': 2})
>>> defdemo['id'] == 2
True
>>> defdemo = DefDemo({})
>>> defdemo['id'] == 4
True

```

Producing Content
-----------------

Parsing text from an API is cool, but you also have to reply sometimes.
You can use the exact same objects to do that.

```
>>> from parseable import parseable, Use
>>> User = parseable('User', {'id': int, 'name': str})
>>> Message = parseable('Message', {'from': Use(User), 'text': str})
>>> # defining objects
>>> user = User({'id': 2, 'name': 'Joe'})
>>> message = Message({'from': user.data, 'text': 'Hello'})
>>> message.data == {'text': 'Hello', 'from': {'id': 2, 'name': 'Joe'}}
True

```

You can then encode this a json and send this to your API endpoint.
This way, you can guarantee the correctness of data structures
on input and output operations.

Types and inheritance
---------------------

All the objects as subclasses of parseable.Parseable, you can check
if an object is a parseable like this:

```
>>> from parseable import parseable, Parseable
>>> User = parseable('User', {'id': int, 'name': str})
>>> issubclass(User, Parseable)
True

```

Some Parseables will verify as Sequence or Mapping, depending on the Schema
that you create them with.

```
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

Value Expansion
---------------

You can use parseable object instances as any other object, but sometimes,
you really need the real underlying data structures types. For example,
when you want to use special types properties or when you want to dump
data using the json module.

```
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

Note: expand recurses on lists and dicts, so if you have nested Parseables,
the whole structure will be expanded.
