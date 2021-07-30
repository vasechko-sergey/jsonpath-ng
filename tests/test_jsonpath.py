import pytest

from jsonpath_ng import (
    DatumInContext, Fields, Root, This, jsonpath,
    parser,
)
from jsonpath_ng.parser import parse


def check_case(string, data, target):
    # Note that just manually building an AST would avoid this dep and
    # isolate the tests, but that would suck a bit
    # Also, we coerce iterables, etc, into the desired target type

    print('parse("%s").find(%s) =?= %s' % (string, data, target))
    result = parser.parse(string).find(data)
    if isinstance(target, list):
        assert [r.value for r in result] == target
    elif isinstance(target, set):
        assert set([r.value for r in result]) == target
    else:
        assert result.value == target


@pytest.mark.parametrize('context, path, full_path', [
    (DatumInContext(3), This(), This()),
    (DatumInContext(3, path=Root()), Root(), Root()),
    (DatumInContext(3, path=Fields('foo'), context='does not matter'), Fields('foo'), Fields('foo')),
    (DatumInContext(
        3,
        path=Fields('foo'),
        context=DatumInContext('does not matter', path=Fields('baz'), context='does not matter')
    ), Fields('foo'), Fields('baz').child(Fields('foo'))),
])
def test_datum_in_context_init(context, path, full_path):
    assert context.path == path
    assert context.full_path == full_path


@pytest.mark.parametrize('left,right', [
    (
        DatumInContext(3).in_context(path=Fields('foo'), context=DatumInContext('whatever')),
        DatumInContext(3, path=Fields('foo'), context=DatumInContext('whatever'))
    ),
    (
        DatumInContext(3)
            .in_context(path=Fields('foo'), context='whatever').in_context(path=Fields('baz'), context='whatever'),
        DatumInContext(3)
            .in_context(path=Fields('foo'), context=DatumInContext('whatever')
                        .in_context(path=Fields('baz'), context='whatever'))
    )
])
def test_datum_in_context_in_context(left, right):
    assert left == right


@pytest.mark.parametrize('string,data,target', [
    ('foo', {'foo': 'baz'}, ['baz']),
    ('foo,baz', {'foo': 1, 'baz': 2}, [1, 2]),
    ('@foo', {'@foo': 1}, [1]),
    ('*', {'foo': 1, 'baz': 2}, set([1, 2])),
])
def test_fields_cases(string, data, target):
    jsonpath.auto_id_field = None
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo.id', {'foo': 'baz'}, ['foo']),
    ('foo.id', {'foo': {'id': 'baz'}}, ['baz']),
    ('foo,baz.id', {'foo': 1, 'baz': 2}, ['foo', 'baz']),
    ('*.id', {'foo': {'id': 1}, 'baz': 2}, set(['1', 'baz'])),
    ('*', {'foo': 1, 'baz': 2}, set([1, 2, '`this`']))
])
def test_fields_cases_id(string, data, target):
    jsonpath.auto_id_field = "id"
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('$', {'foo': 'baz'}, [{'foo': 'baz'}]),
    ('foo.$', {'foo': 'baz'}, [{'foo': 'baz'}]),
    ('foo.$.foo', {'foo': 'baz'}, ['baz']),
])
def test_root_value(string, data, target):
    jsonpath.auto_id_field = None
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('$.id', {'foo': 'baz'}, ['$']),  # This is a wonky case that is
    # not that interesting
    ('foo.$.id', {'foo': 'baz', 'id': 'bizzle'}, ['bizzle']),
    ('foo.$.baz.id', {'foo': 4, 'baz': 3}, ['baz']),
])
def test_root_value_id(string, data, target):
    jsonpath.auto_id_field = 'id'
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('`this`', {'foo': 'baz'}, [{'foo': 'baz'}]),
    ('foo.`this`', {'foo': 'baz'}, ['baz']),
    ('foo.`this`.baz', {'foo': {'baz': 3}}, [3]),
])
def test_this_value(string, data, target):
    jsonpath.auto_id_field = None
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('id', {'foo': 'baz'}, ['`this`']),  # This is, again, a wonky case
    # that is not that interesting
    ('foo.`this`.id', {'foo': 'baz'}, ['foo']),
    ('foo.`this`.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
])
def test_this_auto_id(string, data, target):
    jsonpath.auto_id_field = 'id'
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('[0]', [42], [42]),
    ('[5]', [42], []),
    ('[2]', [34, 65, 29, 59], [29])
])
def test_index_value(string, data, target):
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('[0].id', [42], ['[0]']),
    ('[2].id', [34, 65, 29, 59], ['[2]'])
])
def test_index_value_id(string, data, target):
    jsonpath.auto_id_field = "id"
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('[*]', [1, 2, 3], [1, 2, 3]),
    ('[*]', range(1, 4), [1, 2, 3]),
    ('[1:]', [1, 2, 3, 4], [2, 3, 4]),
    ('[:2]', [1, 2, 3, 4], [1, 2]),
    ('[*]', 1, [1]),  # This is a funky hack
    ('[0:]', 1, [1]),  # This is a funky hack
    ('[*]', {'foo': 1}, [{'foo': 1}]),  # This is a funky hack
    ('[*].foo', {'foo': 1}, [1]),  # This is a funky hack
])
def test_slice_value(string, data, target):
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('[*].id', [1, 2, 3], ['[0]', '[1]', '[2]']),
    ('[1:].id', [1, 2, 3, 4], ['[1]', '[2]', '[3]'])
])
def test_slice_value_id(string, data, target):
    jsonpath.auto_id_field = "id"
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo.baz', {'foo': {'baz': 3}}, [3]),
    ('foo.baz', {'foo': {'baz': [3]}}, [[3]]),
    ('foo.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}}, [5])
])
def test_child_value(string, data, target):
    jsonpath.auto_id_field = None
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
    ('foo.baz.id', {'foo': {'baz': [3]}}, ['foo.baz']),
    ('foo.baz.id', {'foo': {'id': 'bizzle', 'baz': 3}}, ['bizzle.baz']),
    ('foo.baz.id', {'foo': {'baz': {'id': 'hi'}}}, ['foo.hi']),
    ('foo.baz.bizzle.id', {'foo': {'baz': {'bizzle': 5}}}, ['foo.baz.bizzle'])
])
def test_child_value_id(string, data, target):
    jsonpath.auto_id_field = "id"
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo..baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, [1, 2]),
    ('foo..baz', {'foo': [{'baz': 1}, {'baz': 2}]}, [1, 2]),
])
def test_descendants_value(string, data, target):
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo..baz.id', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, ['foo.baz', 'foo.bing.baz'])
])
def test_descendants_value_id(string, data, target):
    jsonpath.auto_id_field = "id"
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo.baz.`parent`', {'foo': {'baz': 3}}, [{'baz': 3}]),
    ('foo.`parent`.foo.baz.`parent`.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}}, [5])
])
def test_parent_value(string, data, target):
    check_case(string, data, target)


@pytest.mark.parametrize('string,data,target', [
    ('foo."bar-baz"', {'foo': {'bar-baz': 3}}, [3]),
    ('foo.["bar-baz","blah-blah"]', {'foo': {'bar-baz': 3, 'blah-blah': 5}}, [3, 5])
])
def test_hyphen_key(string, data, target):
    # NOTE(sileht): hyphen is now a operator
    # so to use it has key we must escape it with quote
    # self.check_cases([('foo.bar-baz', {'foo': {'bar-baz': 3}}, [3]),
    #                  ('foo.[bar-baz,blah-blah]',
    #                   {'foo': {'bar-baz': 3, 'blah-blah': 5}},
    #                   [3, 5])])
    check_case(string, data, target)


def check_update_cases(original, expr_str, value, expected):
    print('parse(%r).update(%r, %r) =?= %r' % (expr_str, original, value, expected))
    expr = parse(expr_str)
    actual = expr.update(original, value)
    assert actual == expected


def test_update_root():
    check_update_cases('foo', '$', 'bar', 'bar')


def test_update_this():
    check_update_cases('foo', '`this`', 'bar', 'bar')


@pytest.mark.parametrize('original, expr_str, value, expected', [
    ({'foo': 1}, 'foo', 5, {'foo': 5}),
    ({'foo': 1, 'bar': 2}, '$.*', 3, {'foo': 3, 'bar': 3})
])
def test_update_fields(original, expr_str, value, expected):
    check_update_cases(original, expr_str, value, expected)


@pytest.mark.parametrize('original, expr_str, value, expected', [
    ({'foo': 'bar'}, '$.foo', 'baz', {'foo': 'baz'}),
    ({'foo': {'bar': 1}}, 'foo.bar', 'baz', {'foo': {'bar': 'baz'}})
])
def test_update_child(original, expr_str, value, expected):
    check_update_cases(original, expr_str, value, expected)


@pytest.mark.parametrize('original, expr_str, value, expected', [
    ({'foo': {'bar': {'baz': 1}}, 'bar': {'baz': 2}},
     '*.bar where baz', 5, {'foo': {'bar': 5}, 'bar': {'baz': 2}})
])
def test_update_where(original, expr_str, value, expected):
    check_update_cases(original, expr_str, value, expected)


@pytest.mark.parametrize('original, expr_str, value, expected', [
    (
        {'foo': {'bar': 1, 'flag': 1}, 'baz': {'bar': 2}},
        '(* where flag) .. bar',
        3,
        {'foo': {'bar': 3, 'flag': 1}, 'baz': {'bar': 2}}
    )
])
def test_update_descendants_where(original, expr_str, value, expected):
    check_update_cases(original, expr_str, value, expected)


@pytest.mark.parametrize('original, expr_str, value, expected', [
    ({'somefield': 1}, '$..somefield', 42, {'somefield': 42}),
    ({'outer': {'nestedfield': 1}}, '$..nestedfield', 42, {'outer': {'nestedfield': 42}}),
    ({'outs': {'bar': 1, 'ins': {'bar': 9}}, 'outs2': {'bar': 2}},
     '$..bar', 42,
     {'outs': {'bar': 42, 'ins': {'bar': 42}}, 'outs2': {'bar': 42}})
])
def test_update_descendants(original, expr_str, value, expected):
    check_update_cases(original, expr_str, value, expected)


def test_update_index():
    check_update_cases(['foo', 'bar', 'baz'], '[0]', 'test', ['test', 'bar', 'baz'])


def test_update_slice():
    check_update_cases(['foo', 'bar', 'baz'], '[0:2]', 'test', ['test', 'test', 'baz'])
