import copy
import schema

from enum import Enum
from typing import Self, Hashable, MutableSet, MutableSequence, MutableMapping

__all__ = ['Schema',
           'And',
           'Or',
           'Optional']


class MergeFlags(Enum):
    """
    Conflict resolution algorithm for merging Schemas
    """
    KEEP = 0            # Keep parent values
    EXCEPTION = 1       # Raise an exception
    OVERWRITE = 2       # Keep child values
    ALTERNATIVE = 4     # Replace with Or(self.schema[key], other.schema[key])


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


class Or(schema.Or):
    def __eq__(self, other: Self) -> bool:
        """ Equality comparison: Ors are equal iff their schemas are equal """
        if not isinstance(other, Or):
            return NotImplemented
        else:
            mine = set(make_hashable(self._args))
            their = set(make_hashable(other._args))
            return mine == their


class And(schema.And):
    def __eq__(self, other: Self) -> bool:
        """ Equality comparison: Ands are equal iff their schemas are equal """
        if not isinstance(other, And):
            return NotImplemented
        else:
            mine = set(make_hashable(self._args))
            their = set(make_hashable(other._args))
            return mine == their and self.__class__ == other.__class__


class Optional(schema.Optional):
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Optional):
            return NotImplemented
        return self._schema == other._schema

    def __hash__(self):
        return super().__hash__()


class Schema(schema.Schema):
    def _merge(self, other: Self, *, conflict: MergeFlags = MergeFlags.OVERWRITE):
        """
        Merge a child Schema into a parent Schema, optionally overwriting any existing keys.

        Parameters
        ----------
        other : Schema
        conflict : MergeFlags
            Specifies what to do if a key is found both in parent and child:
                KEEP: keep the value of parent
                EXCEPTION: throw an exception
                OVERWRITE: keep the value of child, discarding the value of parent (default)
                FUSE: allow both values from parent's and child's schema
                ALTERNATIVE: replace with Or(parent's schema, child's schema)
        """
        assert isinstance(other, Schema), "Can only merge a Schema with another Schema"

        if isinstance(self.schema, dict) and isinstance(other.schema, dict):
            for key in other.schema:
                if key in self.schema:
                    match conflict:
                        case MergeFlags.KEEP:
                            pass
                        case MergeFlags.EXCEPTION:
                            raise schema.SchemaError(f"Key collision for {key}")
                        case MergeFlags.OVERWRITE:
                            self.schema[key] = other.schema[key]
                        case MergeFlags.ALTERNATIVE:
                            # two dicts can be merged recursively
                            if isinstance(self.schema[key], dict) and isinstance(other.schema[key], dict):
                                self.schema[key] |= other.schema[key]
                            # two Schemas can be merged recursively
                            elif isinstance(self.schema[key], Schema) and isinstance(other.schema[key], Schema):
                                self.schema[key] |= other.schema[key]
                            # otherwise use Or of the two subschemas
                            else:
                                self.schema[key] = Or(self.schema[key], other.schema[key])
                else:
                    self.schema[key] = other.schema[key]
        else:
            if self.schema == other.schema:
                # two identical schemas are replaced by one
                return self
            else:
                # two different schemas are simply Or-ed
                self._schema = Or(self.schema, other.schema)

        return self


    def __eq__(self, other: Self) -> bool:
        """
            Determine whether two schemas are equal or not.
            Caveat: equality tests are difficult in Python and difficult in general for many objects.
            For instance (lambda x: x < 3) != (lambda x: x < 3) and there is no easy way around it.
        """
        if not isinstance(other, Schema):
            return self._schema == other

        return self._schema == other._schema

    def __or__(self, other: Self) -> Self:
        sch = copy.deepcopy(self)
        return sch._merge(other, conflict=MergeFlags.ALTERNATIVE)

    def __and__(self, other: Self) -> Self:
        sch = copy.deepcopy(self)
        return sch._merge(other, conflict=MergeFlags.OVERWRITE)

    def __add__(self, other) -> Self:
        sch = copy.deepcopy(self)
        return sch._merge(other, conflict=MergeFlags.FUSE)

    def __ior__(self, other: Self):
        return self._merge(other, conflict=MergeFlags.ALTERNATIVE)

    def __iand__(self, other: Self):
        return self._merge(other, conflict=MergeFlags.OVERWRITE)

    def __iadd__(self, other: Self):
        return self._merge(other, conflict=MergeFlags.FUSE)
