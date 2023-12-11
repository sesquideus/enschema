import pytest
from enschema import Schema, And, Or, Optional, Regex, Const


@pytest.fixture
def int_lambda():
    return lambda x: x < 6


class TestSchemaBasic:
    def test_empty(self):
        assert Schema({}) == Schema({})

    def test_basic_int(self):
        assert Schema(int) == Schema(int)

    def test_basic_list_equal(self):
        assert Schema([int, str, '5']) == Schema([int, str, '5'])

    def test_basic_list_swapped(self):
        assert Schema([int, str, '5']) != Schema([str, int, '5'])

    def test_basic_tuple_equal(self):
        assert Schema((int, str, '6', {})) == Schema((int, str, '6', {}))

    def test_basic_tuple_swapped(self):
        assert Schema((int, str, '5')) != Schema((str, int, '5'))

    def test_tuple_is_not_list(self):
        assert Schema((int, str, '5')) != Schema([int, str, '5'])

    def test_unequal_type_value(self):
        assert Schema(int) != Schema(123)

    def test_unequal_type(self):
        assert Schema(int) != Schema(float)

    def test_unequal_value(self):
        assert Schema(466) != Schema(-466)

    def test_lambda_equal(self):
        """
        Caveat: this is not desired but expected. However, in general there is no way around this.
        Lambdas are only equal if they are the same function.
        """
        assert Schema(lambda x: x < 5) != Schema(lambda x: x < 5)

    def test_lambda_same(self, int_lambda):
        """ As before, but if the function is actually the same object, they are equal """
        assert Schema(int_lambda) == Schema(int_lambda)

    def test_lambda_fixture(self, int_lambda):
        assert Schema(lambda x: x < 6) != Schema(int_lambda)

    def test_hashable(self):
        assert hash(lambda x: x < 5)


class TestOr:
    def test_empty(self):
        assert Or() == Or()

    def test_order(self):
        assert Or(1, 'c', int, 2) == Or(2, 1, 'c', int)

    def test_order_dict(self):
        assert Or({'a': int}, {int: str}) == Or({int: str}, {'a': int})

    def test_different_types(self):
        assert Or(str, int) != Or(int, float)

    def test_dicts(self):
        assert Or({}, {'a': float}) == Or({'a': float}, {})

    def test_hashable_simple(self):
        assert hash(Or(123, 234))

    def test_hashable_multiple(self):
        assert hash(Or(123, int, 'abc'))


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

    def test_hashable_multiple(self):
        assert hash(And(int, lambda x: x > 30))


class TestOptional:
    def test_equal(self):
        assert Optional(123) == Optional(123)

    def test_unequal(self):
        assert Optional(123) != Optional(445)

    def test_against_value(self):
        assert 123 != Optional(123)

    def test_hashable(self):
        assert hash(Optional(str))


class TestConst:
    def test_hashable(self):
        assert hash(Const('a'))

    def test_hashable_dict(self):
        assert hash(Const({'a': 'b'}))


class TestRegex:
    def test_basic_equal(self):
        assert Regex(r'a') == Regex(r'a')

    def test_basic_unequal(self):
        assert Regex(r'^foo$') != Regex(r'foo')

    def test_hashable(self):
        assert hash(self)
