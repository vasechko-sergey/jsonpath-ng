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
