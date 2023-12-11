import pytest
from enschema import Schema, And, Or, Optional, Regex, Const, Use


@pytest.fixture
def first():
    return Schema({
        'duck': 'yellow',
        'dog': 'white',
        'cat': {
            'male': 'red',
            'female': 'cyan',
        },
    })


@pytest.fixture
def second():
    return Schema({
        'dog': 'black',
        'cat': {
            'helicopter': 'magenta',
        },
    })


@pytest.fixture
def ored():
    return Schema({
        'duck': 'yellow',
        'dog': Or('white', 'black'),
        'cat': Schema({
            'male': 'red',
            'female': 'cyan',
            'helicopter': 'magenta',
        }),
    })


@pytest.fixture
def anded():
    return Schema({
    })


@pytest.fixture
def meow():
    return Schema({
        'cat': 'white',
    })


@pytest.fixture
def meowww():
    return Schema({
        'cat': 'black',
    })


@pytest.fixture
def woof():
    return Schema({
        'dog': 'black',
    })


class TestMerge:
    def test_merge_1(self):
        assert Schema({}) | Schema({}) == Schema({})

    def test_merge_2(self):
        assert Schema('123') | Schema(123) == Schema(Or('123', 123))

    def test_merge_equal(self):
        assert Schema(124) | Schema(124) == Schema(124)

    def test_merge_ored(self):
        assert Schema(124) | Schema(125) == Schema(Or(124, 125))

    def test_merge_tuple(self):
        assert Schema((1, 2)) | Schema((2, 3)) == Schema(Or((1, 2), (2, 3)))

    def test_merge_same_complex(self):
        assert Schema((1, 2, {'a': str})) | Schema((1, 2, {'a': str})) == Schema((1, 2, {'a': str}))

    def test_or(self, first, second, ored):
        assert first | second == ored

    def test_ior(self, first, second, ored):
        first |= second
        assert first == ored

    def test_cats(self, meow, meowww):
        assert meow | meowww == Schema({'cat': Or('black', 'white')})

    def test_animals(self, meow, woof):
        assert meow | woof == Schema({'cat': 'white', 'dog': 'black'})