import pytest

from jsonpath_ng import Child, Descendants, Fields, Index, Slice, Where
from jsonpath_ng.lexer import JsonPathLexer
from jsonpath_ng.parser import JsonPathParser


def check_parse_case(string, parsed):
    parser = JsonPathParser(
        debug=True, lexer_class=lambda: JsonPathLexer(debug=False)
    )  # Note that just manually passing token streams avoids this dep, but that sucks

    assert parser.parse(string) == parsed


@pytest.mark.parametrize('string, parsed', [
    ('foo', Fields('foo')),
    ('*', Fields('*')),
    ('baz,bizzle', Fields('baz', 'bizzle')),
    ('[1]', Index(1)),
    ('[1:]', Slice(start=1)),
    ('[:]', Slice()),
    ('[*]', Slice()),
    ('[:2]', Slice(end=2)),
    ('[1:2]', Slice(start=1, end=2)),
    ('[5:-2]', Slice(start=5, end=-2))
])
def test_atomic(string, parsed):
    check_parse_case(string, parsed)


@pytest.mark.parametrize('string, parsed', [
    ('foo.baz', Child(Fields('foo'), Fields('baz'))),
    ('foo.baz,bizzle', Child(Fields('foo'), Fields('baz', 'bizzle'))),
    ('foo where baz', Where(Fields('foo'), Fields('baz'))),
    ('foo..baz', Descendants(Fields('foo'), Fields('baz'))),
    ('foo..baz.bing', Descendants(Fields('foo'), Child(Fields('baz'), Fields('bing'))))
])
def test_nested(string, parsed):
    check_parse_case(string, parsed)
