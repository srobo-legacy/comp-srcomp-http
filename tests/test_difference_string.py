from nose.tools import eq_, raises

from sr.comp.http.query_utils import parse_difference_string

def test_exact_equal():
    assert parse_difference_string('4')(4)

def test_exact_gt():
    assert not parse_difference_string('4')(6)

def test_exact_lt():
    assert not parse_difference_string('4')(2)

@raises(ValueError)
def test_parse_failure():
    parse_difference_string('cheese', int)

def test_upper_equal():
    assert parse_difference_string('..4')(4)

def test_upper_gt():
    assert not parse_difference_string('..4')(6)

def test_upper_lt():
    assert parse_difference_string('..4')(2)

def test_lower_equal():
    assert parse_difference_string('4..')(4)

def test_lower_gt():
    assert parse_difference_string('4..')(6)

def test_lower_lt():
    assert not parse_difference_string('4..')(2)

def test_bounds_lt():
    assert not parse_difference_string('4..6')(2)

def test_bounds_lower():
    assert parse_difference_string('4..6')(4)

def test_bounds_mid():
    assert parse_difference_string('4..6')(5)

def test_bounds_upper():
    assert parse_difference_string('4..6')(6)

def test_bounds_gt():
    assert not parse_difference_string('4..6')(8)

def test_other_types():
    assert parse_difference_string('cheese..', str)('cheese')

def test_other_types_negative():
    assert not parse_difference_string('cheese..', str)('')

@raises(ValueError)
def test_invalid_ds():
    parse_difference_string('1..2..3')

@raises(ValueError)
def test_inverted_bounds():
    parse_difference_string('3..2')

@raises(ValueError)
def test_double_open():
    parse_difference_string('..')
