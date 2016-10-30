from unittest import TestCase
from schema import Optional, Use
from parseable import parseable, Self, SchemaError
from random import randint


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

