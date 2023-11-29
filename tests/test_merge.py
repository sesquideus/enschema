import pytest
from enschema import Schema, And, Or


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
    ored = Schema({
        'duck': 'yellow',
        'dog': Or('white', 'black'),
        'cat': Schema({
            'male': 'red',
            'female': 'cyan',
            'helicopter': 'magenta',
        }),
    })

    def test_or(self, first, second):
        print()
        print(first | second)
        print(__class__.ored)
        assert first | second == __class__.ored

    def test_ior(self, first, second):
        first |= second
        assert first == __class__.ored

    def test_cats(self, meow, meowww):
        assert meow | meowww == Schema({'cat': Or('black', 'white')})

    def test_animals(self, meow, woof):
        assert meow | woof == Schema({'cat': 'white', 'dog': 'black'})



class TestSchemaBasic:
    def test_empty(self):
        assert Schema({}) == Schema({})

    def test_basic_1(self):
        assert Schema(int) == Schema(int)

    def test_basic_1(self):
        assert Schema([int, str, '5']) == Schema([int, str, '5'])

    def test_unequal(self):
        assert Schema(int) != Schema(123)

    def test_unequal(self):
        assert Schema(int) != Schema(float)




class TestOr:
    def test_empty(self):
        assert Or() == Or()

    def test_order(self):
        assert Or(1, 'c', int, 2) == Or(2, 1, 'c', int)

    def test_types(self):
        assert Or(str, int) != Or(int, float)

    def test_dicts(self):
        assert Or({}, {'a': float}) == Or({'a': float}, {})


class TestAnd:
    def test_empty(self):
        assert And() == And()

    def test_nonempty(self):
        assert And(int, type) != And(str, lambda x: x > 0)

    def test_types(self):
        assert And(int, lambda x: x < 5) != And(lambda x: x < 3, int)

    def test_order(self):
        assert Or(1, 'c', int, 2) == Or(2, 1, 'c', int)

    def test_and_or(self):
        assert And(str, int) != Or(str, int)
