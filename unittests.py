from pprint import pprint
import unittest
from typing import Callable

from KeyPathDict import KeyPath
from KeyPathDict import KeyPathDict

class KeyPathUnittests(unittest.TestCase):

    display_test = False

    simple_content = [ 'a', 'b', 'c' ]
    composite_content = [ 'a 1 @', ('b', 'c'), 1, { 'e' } ]

    test_keypaths = {
        'simple': KeyPath(simple_content),
        'composite': KeyPath(composite_content),
        'sum': KeyPath(simple_content) + KeyPath(composite_content)
    }
    
    expected_strings = {
        'simple': '.'.join(simple_content),
        'composite': '.'.join(map(lambda x: str(x), composite_content)),
        'sum': '.'.join(map(lambda x: str(x), simple_content + composite_content))
    }

    expected_adds = {
        'sum': KeyPath(simple_content + composite_content)
    }

    expected_tops = {
        'simple': simple_content[0],
        'composite': composite_content[0],
        'sum': simple_content[0]
    }

    expected_descendants = {
        'simple': KeyPath(simple_content[1:]),
        'composite': KeyPath(composite_content[1:]),
        'sum': KeyPath(simple_content[1:] + composite_content)
    }

    def run_test(self, function: callable, results: dict) -> None:
        for nick, kp in self.test_keypaths.items():
            if nick in results:
                if self.display_test:
                    print(f'Testing: {function.__name__}({repr(kp)}) -> {results[nick]}')
                self.assertEqual(function(kp), results[nick])

    def test_string(self):
        self.run_test(str, self.expected_strings)

    def test_add(self):
        self.run_test(lambda x: x, self.expected_adds)
    
    def test_top(self):
        self.run_test(lambda x: x.top, self.expected_tops)
    
    def test_descendant(self):
        self.run_test(lambda x: x.descendants, self.expected_descendants)

class KeyPathDictUnittests(unittest.TestCase):

    # Les éléments de tests
    base_dict = {
        'a': 0,
        'b': {
            'ba': 1,
            'bb': {
                'bba': 2,
                'bbb': {
                    'bbba': 3,
                    'bbbb': {
                        'bbbba': 4
                    }
                }
            }
        }
    }

    # De quoi merge
    merge_dict = {
        'b': {
            'bb': {
                'bba': 'Replaced',
                'bbb': {
                    'bbbb': {
                        'bbbbb': {
                            'bbbbba': 'Added'
                        }
                    }
                }
            },
            'bc': 'Added'
        }
    }

    expected__gets__ = {
        'a' : 0,
        KeyPath(('b', 'ba')): 1,
        KeyPath(('b', 'bb', 'bba')): 2,
        KeyPath(('b', 'bb', 'bbb', 'bbba')): 3,
        KeyPath(('b', 'bb', 'bbb', 'bbbb', 'bbbba')): 4,
        KeyPath(('b', 'bb')) + KeyPath(('bbb', 'bbbb')  + KeyPath([ 'bbbba' ])): 4,
        KeyPath(('b', 'bb')): base_dict['b']['bb'],
        KeyPath(('b', 'bb', 'bbb')): base_dict['b']['bb']['bbb'],
    }

    expected_kpitems = [
        (KeyPath(('a', )), 0),
        (KeyPath(('b', 'ba')), 1),
        (KeyPath(('b', 'bb', 'bba')), 2),
        (KeyPath(('b', 'bb', 'bbb', 'bbba')), 3),
        (KeyPath(('b', 'bb', 'bbb', 'bbbb', 'bbbba')), 4),
    ]

    expected_merge = {
        'a': 0,
        'b': {
            'ba': 1,
            'bb': {
                'bba': 'Replaced',
                'bbb': {
                    'bbba': 3,
                    'bbbb': {
                        'bbbba': 4,
                        'bbbbb': {
                            'bbbbba': 'Added'
                        }
                    }
                }
            },
            'bc': 'Added'
        }
    }
    
    def test__get__(self):
        K = KeyPathDict(self.base_dict)
        for keypath, value in self.expected__gets__.items():
            self.assertEqual(K[keypath], value)
        self.assertRaises(TypeError, lambda x: K[x], KeyPath(('a', 'b', 'c')))
        self.assertRaises(KeyError, lambda x: K[x], KeyPath(('d', )))
        
    def test_deepcopy(self):
        K = KeyPathDict(self.base_dict)
        K2 = K.deepcopy()
        self.assertEqual(K, K2)

    def test_gets(self):
        K = KeyPathDict(self.base_dict)
        self.assertEqual(K.get('a'), 0)
        self.assertEqual(K.get('c', 'Nope'), 'Nope')
        self.assertEqual(K.get(KeyPath(('b', 'bb', 'bbb', 'bbba')), 'Nope'), 3)

    def test_merge(self):
        K = KeyPathDict(self.base_dict)
        K.merge(self.merge_dict)
        self.assertEqual(K, self.expected_merge)

    def test_kpitems(self):
        K = KeyPathDict(self.base_dict)
        expected = list(self.expected_kpitems).sort()
        result = [ (keypath, value) for keypath, value in K.kpitems() ].sort()
        self.assertEqual(result, expected)

    def test__set__(self):
        K = KeyPathDict(self.base_dict)
        K2 = KeyPathDict()
        for keypath, value in K.kpitems():
            K2[keypath] = value
        self.assertEqual(K, K2)

if __name__ == '__main__':
    # def test_exception(kpdict, keypath):
    #     print(f'Testing keypath {repr(keypath)}')
    #     try:
    #         result = kpdict[keypath]
    #     except Exception as E:
    #         print(f'{type(E).__name__} exception caught : {E}')
    
    # K = KeyPathDict(KeyPathDictUnittests.base_dict)
    # test_exception(K, KeyPath(('coincoin', 'cuicui', 'proutprout')))
    # test_exception(K, KeyPath(('a', 'b')))
    # test_exception(K, KeyPath(('b', 'bb', 'bbb', 'bbba', 'bbbbb')))

    unittest.main()
