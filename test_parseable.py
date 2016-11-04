from unittest import TestCase
from schema import Optional, Use
from parseable import parseable, Self, SchemaError, Parseable
from random import randint
try:
    from collections.abc import Sequence, Mapping
except ImportError:
    from collections import Sequence, Mapping


class SimpleTest(TestCase):

    def setUp(self):
        self.SimpleInt = parseable('SimpleInt', int)
        self.SimpleStr = parseable('SimpleStr', str)

    def test_simple(self):
        '''
        Check if base function works
        '''
        self.SimpleInt(2)
        self.SimpleStr('2')

    def test_data(self):
        data = 2
        self.assertEqual(self.SimpleInt(data).data, data)
        data = '2'
        self.assertEqual(self.SimpleStr(data).data, data)

    def test_typeerror(self):
        self.assertRaises(SchemaError, self.SimpleInt, '2')
        self.assertRaises(SchemaError, self.SimpleInt, [])
        self.assertRaises(SchemaError, self.SimpleInt, 2.2)
        self.assertRaises(SchemaError, self.SimpleStr, 2)
        self.assertRaises(SchemaError, self.SimpleStr, [])
        self.assertRaises(SchemaError, self.SimpleStr, 2.2)


class SubParseableTest(TestCase):

    def setUp(self):
        self.User = parseable('User', {'id': int, 'name': str})
        self.Message = parseable('Message', {'from': Use(self.User),
                                             'id': int, 'text': str})
        self.gooddata = {'from': {'id': 2, 'name': 'Test'},
                         'id': 4, 'text': 'Hi'}
        self.baddata = {'from': {},
                        'id': 4, 'text': 'Hi'}

    def test_gooddata(self):
        message = self.Message(self.gooddata)

    def test_baddata(self):
        self.assertRaises(SchemaError, self.Message, self.baddata)

    def test_matchdata(self):
        self.assertEqual(self.Message(self.gooddata).data, self.gooddata)

    def test_depth(self):
        Depth = parseable('Depth', [[Use(self.User)]])
        depth = Depth([[{'id': 2, 'name': 'Joe'}]])
        self.assertEqual(depth.data, [[{'id': 2, 'name': 'Joe'}]])


class SubParseableSelf(TestCase):

    def setUp(self):
        self.Linked = parseable('Linked', {'val': int, Optional('next'): Use(Self)})
        self.data = {'val': 0, 'next': {'val': 1, 'next': {'val': 2}}}

    def test_parse(self):
        self.assertEqual(self.Linked(self.data).data, self.data)


class SubParseableSelfDepthFunc(TestCase):

    def setUp(self):
        self.Linked = parseable('Linked', {'val': int, Optional('next'): Optional(Optional(Use(Self)))})
        self.data = {'val': 0, 'next': {'val': 1, 'next': {'val': 2}}}

    def test_parse(self):
        self.assertEqual(self.Linked(self.data).data, self.data)


class SubParseableSelfDepthList(TestCase):

    def setUp(self):
        self.Depth = parseable('Depth', [[[[[Self]]]]])
        self.data = []

    def test_parse(self):
        self.Depth(self.data)


class Subscriptable(TestCase):

    def setUp(self):
        self.Flag = parseable('Flag', {'id': int, 'value': bool})
        self.FlagSet = parseable('FlagSet', [Use(self.Flag)])
        self.User = parseable('User', {'id': int, 'name': str})
        self.Message = parseable('Message', {'from': Use(self.User),
                                             'id': int, 'text': str,
                                             'flags': Use(self.FlagSet)})

        self.data = {'from': {'id': 42, 'name': 'Joe User'},
                     'id': 4242,
                     'text': 'Hello, World!',
                     'flags': [{'id': 5, 'value': True},
                               {'id': 12, 'value': False}]}

        self.message = self.Message(self.data)

    def test_subscript_mapping(self):
        self.assertEqual(self.message['id'], 4242)
        self.assertEqual(self.message['text'], 'Hello, World!')

    def test_subscript_submapping(self):
        self.assertEqual(self.message['from']['id'], 42)
        self.assertEqual(self.message['from']['name'], 'Joe User')

    def test_subscript_sequence(self):
        self.assertEqual(self.message['flags'][0]['id'], 5)
        self.assertEqual(self.message['flags'][1]['id'], 12)


class TestStr(TestCase):

    def test_simple(self):
        Simple = parseable('Simple', int)
        simple = Simple(2)
        self.assertEqual(str(simple), 'Simple(2)')

    def test_list(self):
        List = parseable('List', list)
        lst = List([0, 1, 2])
        self.assertEqual(str(lst), 'List([0, 1, 2])')

    def test_dict(self):
        Dict = parseable('Dict', dict)
        dic = Dict({'a': 0})
        self.assertEqual(str(dic), 'Dict({\'a\': 0})')


class NoDirectInstance(TestCase):

    def test_direct_instance(self):
        self.assertRaises(AssertionError, Parseable, None)


class ABCSequence(TestCase):

    def setUp(self):
        self.reflist = list([1, 2, 3])
        self.IntList = parseable('IntList', [int])
        self.intlist = self.IntList(self.reflist)

    def test_inheritance(self):
        self.assertTrue(isinstance(self.intlist, Parseable))
        self.assertTrue(isinstance(self.intlist, Sequence))

    def test_notinheritance(self):
        self.assertFalse(isinstance(self.intlist, Mapping))

    def test_iteration(self):
        self.assertEqual([x for x in self.intlist], [x for x in self.reflist])

    def test_getitem(self):
        self.assertEqual(self.intlist[0], self.reflist[0])

    def test_len(self):
        self.assertEqual(len(self.intlist), len(self.reflist))



class ABCMapping(TestCase):

    def setUp(self):
        self.refdict = dict(enumerate([1, 2, 3]))
        self.IntDict = parseable('IntDict', {int: int})
        self.intdict = self.IntDict(self.refdict)

    def test_inheritance(self):
        self.assertTrue(isinstance(self.intdict, Parseable))
        self.assertTrue(isinstance(self.intdict, Mapping))

    def test_notinheritance(self):
        self.assertFalse(isinstance(self.intdict, Sequence))

    def test_iteration(self):
        self.assertEqual({key: value for key, value in self.intdict.items()},
                         {key: value for key, value in self.refdict.items()})

    def test_getitem(self):
        self.assertEqual(self.intdict[0], self.refdict[0])

    def test_len(self):
        self.assertEqual(len(self.intdict), len(self.refdict))


class ABCScalar(TestCase):

    def setUp(self):
        self.refscal = 42
        self.IntScal = parseable('IntScal', int)
        self.intscal = self.IntScal(self.refscal)

    def test_inheritance(self):
        self.assertTrue(isinstance(self.intscal, Parseable))

    def test_notinheritance(self):
        self.assertFalse(isinstance(self.intscal, Sequence))
        self.assertFalse(isinstance(self.intscal, Mapping))

    def test_iteration(self):
        self.assertRaises(TypeError, lambda seq: [x for x in seq], self.refscal)

    def test_getitem(self):
        self.assertRaises(TypeError, lambda dic: dic[0], self.refscal)

    def test_len(self):
        self.assertRaises(TypeError, len, self.refscal)
