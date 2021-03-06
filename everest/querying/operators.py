"""
Custom querying operators.

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Dec 5, 2011.
"""
from everest.querying.base import BinaryOperator
from everest.querying.base import UnaryOperator

__docformat__ = 'reStructuredText en'
__all__ = ['ASCENDING',
           'CONJUNCTION',
           'CONTAINED',
           'CONTAINS',
           'CQL_FILTER_OPERATORS',
           'CQL_ORDER_OPERATORS',
           'DESCENDING',
           'DISJUNCTION',
           'ENDS_WITH',
           'EQUAL_TO',
           'GREATER_OR_EQUALS',
           'GREATER_THAN',
           'IN_RANGE',
           'LESS_OR_EQUALS',
           'LESS_THAN',
           'NEGATION',
           'STARTS_WITH',
           ]


class STARTS_WITH(BinaryOperator):
    name = 'starts_with'

    @staticmethod
    def apply(value, ref_value):
        if isinstance(value, basestring):
            res = value.startswith(ref_value)
        else:
            res = value[0] == ref_value
        return res


class ENDS_WITH(BinaryOperator):
    name = 'ends_with'

    @staticmethod
    def apply(value, ref_value):
        if isinstance(value, basestring):
            res = value.endswith(ref_value)
        else:
            res = value[-1] == ref_value
        return res


class CONTAINED(BinaryOperator):
    name = 'contained'

    @staticmethod
    def apply(value, ref_value):
        return value in ref_value


class CONTAINS(BinaryOperator):
    name = 'contains'

    @staticmethod
    def apply(value, ref_value):
        return ref_value in value


class EQUAL_TO(BinaryOperator):
    name = 'equal_to'

    @staticmethod
    def apply(value, ref_value):
        return value == ref_value


class LESS_THAN(BinaryOperator):
    name = 'less_than'

    @staticmethod
    def apply(value, ref_value):
        return value < ref_value


class LESS_OR_EQUALS(BinaryOperator):
    name = 'less_than_or_equal_to'

    @staticmethod
    def apply(value, ref_value):
        return value <= ref_value


class GREATER_THAN(BinaryOperator):
    name = 'greater_than'

    @staticmethod
    def apply(value, ref_value):
        return value > ref_value


class GREATER_OR_EQUALS(BinaryOperator):
    name = 'greater_than_or_equal_to'

    @staticmethod
    def apply(value, ref_value):
        return value >= ref_value


class IN_RANGE(BinaryOperator):
    name = 'in_range'

    @staticmethod
    def apply(value, ref_value):
        return value >= ref_value[0] and value <= ref_value[1]


class ASCENDING(BinaryOperator):
    name = 'asc'

    @staticmethod
    def apply(x, y):
        return cmp(x, y)


class DESCENDING(BinaryOperator):
    name = 'desc'

    @staticmethod
    def apply(x, y):
        return cmp(y, x)


class NEGATION(UnaryOperator):
    name = 'negation'

    @staticmethod
    def apply(x):
        return not x


class CONJUNCTION(BinaryOperator):
    name = 'conjunction'

    @staticmethod
    def apply(x, y):
        return x and y


class DISJUNCTION(BinaryOperator):
    name = 'disjunction'

    @staticmethod
    def apply(x, y):
        return x or y


class CQL_FILTER_OPERATORS(object):
    """
    Static container for all CQL filtering operators.
    """

    STARTS_WITH = STARTS_WITH
    ENDS_WITH = ENDS_WITH
    CONTAINED = CONTAINED
    CONTAINS = CONTAINS
    EQUAL_TO = EQUAL_TO
    LESS_THAN = LESS_THAN
    LESS_OR_EQUALS = LESS_OR_EQUALS
    GREATER_THAN = GREATER_THAN
    GREATER_OR_EQUALS = GREATER_OR_EQUALS
    IN_RANGE = IN_RANGE


class CQL_ORDER_OPERATORS(object):
    """
    Static container for all CQL ordering operators.
    """

    ASCENDING = ASCENDING
    DESCENDING = DESCENDING
