import copy
import schema

from typing import Self, Hashable, MutableSet, MutableSequence, MutableMapping

__all__ = [
    'Schema',
    'And', 'Or', 'Optional',
    'Regex', 'Use', 'Const',
    'SchemaError', 'SchemaWrongKeyError', 'SchemaMissingKeyError',
    'SchemaUnexpectedTypeError', 'SchemaForbiddenKeyError', 'SchemaOnlyOneAllowedError',
]


def make_hashable(x):
    if isinstance(x, tuple):
        return tuple([make_hashable(y) for y in x])
    elif isinstance(x, MutableSet):
        return frozenset([make_hashable(y) for y in x])
    elif isinstance(x, MutableSequence):
        return tuple([make_hashable(y) for y in x])
    elif isinstance(x, MutableMapping):
        return frozenset({y: make_hashable(z) for y, z in x.items()})
    else:
        return x


SchemaError = schema.SchemaError
SchemaWrongKeyError = schema.SchemaWrongKeyError
SchemaOnlyOneAllowedError = schema.SchemaOnlyOneAllowedError
SchemaMissingKeyError = schema.SchemaMissingKeyError
SchemaForbiddenKeyError = schema.SchemaForbiddenKeyError
SchemaUnexpectedTypeError = schema.SchemaUnexpectedTypeError


class Regex(schema.Regex):
    def __eq__(self, other: Self):
        if not isinstance(other, Regex):
            return NotImplemented
        else:
            return self._pattern_str == other._pattern_str and self._flags_names == other._flags_names

    def __hash__(self):
        return hash(self._pattern_str + self._flags_names)


class Use(schema.Use):
    def __eq__(self, other: Self):
        if not isinstance(other, Use):
            return NotImplemented
        else:
            return self._callable == other._callable


class Or(schema.Or):
    def __eq__(self, other: Self) -> bool:
        """ Equality comparison: Ors are equal iff their schemas are equal """
        if not isinstance(other, Or):
            return NotImplemented
        else:
            mine = set(make_hashable(self._args))
            their = set(make_hashable(other._args))
            return mine == their

    def __hash__(self):
        return hash(self._args)


class And(schema.And):
    def __eq__(self, other: Self) -> bool:
        """ Equality comparison: Ands are equal iff their schemas are equal """
        if not isinstance(other, And):
            return NotImplemented
        else:
            mine = set(make_hashable(self._args))
            their = set(make_hashable(other._args))
            return mine == their and self.__class__ == other.__class__

    def __hash__(self):
        return hash(self._args)


class Optional(schema.Optional):
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Optional):
            return NotImplemented
        return self._schema == other._schema

    def __hash__(self):
        return super().__hash__()


class Const(schema.Const):
    def __eq__(self, other) -> bool:
        return self.schema == other.schema

    def __hash__(self):
        return hash(make_hashable(self.schema))


class Schema(schema.Schema):
    def __eq__(self, other: Self) -> bool:
        """
            Determine whether two schemas are equal or not.
            Caveat: equality tests are difficult in Python and difficult in general for many objects.
            For instance (lambda x: x < 3) != (lambda x: x < 3) and there is no easy way around it.
        """
        if isinstance(other, Schema):
            return self._schema == other._schema
        else:
            # If our schema is equal to the other object, we are good to go.
            return self._schema == other

    def __or__(self, other: Self) -> Self:
        sch = copy.deepcopy(self)
        sch |= other
        return sch

    def __ior__(self, other: Self):
        assert isinstance(other, Schema), "Can only merge a Schema with another Schema"

        if isinstance(self.schema, dict) and isinstance(other.schema, dict):
            for key in other.schema:
                if key in self.schema:
                    if isinstance(self.schema[key], dict) and isinstance(other.schema[key], dict):
                        # two dicts can be merged recursively
                        self.schema[key] |= other.schema[key]
                    elif isinstance(self.schema[key], Schema) and isinstance(other.schema[key], Schema):
                        # two Schemas can be merged recursively
                        self.schema[key] |= other.schema[key]
                    else:
                        # otherwise use Or of the two subschemas
                        self.schema[key] = Or(self.schema[key], other.schema[key])
                else:
                    self.schema[key] = other.schema[key]
        else:
            if self.schema == other.schema:
                # two identical schemas are replaced by one
                return self
            else:
                # two different schemas are simply Or'ed
                self._schema = Or(self.schema, other.schema)

        return self
