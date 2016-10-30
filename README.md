Parseable
=========

A python library to make easier the parsing of data structures into objects,
with strong validation.

This has been originally developed to parse messages from the Telegram Bot API
(https://core.telegram.org/bots/api/)

Data validation is done using 'schema' (https://pypi.python.org/pypi/schema)

Basic Usage
-----------

Basic usage is simple. You call the 'parseable' function

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
