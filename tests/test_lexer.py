import pytest
from ply.lex import LexToken

from jsonpath_ng.lexer import JsonPathLexer, JsonPathLexerError


def token(value, ty=None):
    token = LexToken()
    token.type = ty if ty is not None else value
    token.value = value
    token.lineno = -1
    token.lexpos = -1
    return token


def assert_lex_equiv(string, stream):
    # NOTE: lexer fails to reset after call?
    lexer = JsonPathLexer(debug=True)
    stream1 = list(lexer.tokenize(string))  # Save the stream for debug output when a test fails
    stream = list(stream)
    assert len(stream1) == len(stream)
    for token1, token2 in zip(stream1, stream):
        print(token1, token2)
        assert token1.type == token2.type
        assert token1.value == token2.value


@pytest.mark.parametrize('string, parsed_token', [
    ('$', [token('$', '$')]),
    ('"hello"', [token('hello', 'ID')]),
    ("'goodbye'", [token('goodbye', 'ID')]),
    ("'doublequote\"'", [token('doublequote"', 'ID')]),
    (r'"doublequote\""', [token('doublequote"', 'ID')]),
    (r"'singlequote\''", [token("singlequote'", 'ID')]),
    ('"singlequote\'"', [token("singlequote'", 'ID')]),
    ('fuzz', [token('fuzz', 'ID')]),
    ('1', [token(1, 'NUMBER')]),
    ('45', [token(45, 'NUMBER')]),
    ('-1', [token(-1, 'NUMBER')]),
    (' -13 ', [token(-13, 'NUMBER')]),
    ('"fuzz.bang"', [token('fuzz.bang', 'ID')]),
    ('fuzz.bang', [token('fuzz', 'ID'), token('.', '.'), token('bang', 'ID')]),
    ('fuzz.*', [token('fuzz', 'ID'), token('.', '.'), token('*', '*')]),
    ('fuzz..bang', [token('fuzz', 'ID'), token('..', 'DOUBLEDOT'), token('bang', 'ID')]),
    ('&', [token('&', '&')]),
    ('@', [token('@', 'ID')]),
    ('`this`', [token('this', 'NAMED_OPERATOR')]),
    ('|', [token('|', '|')]),
    ('where', [token('where', 'WHERE')]),
])
def test_simple_inputs(string, parsed_token):
    assert_lex_equiv(string, parsed_token)


@pytest.mark.parametrize('input_token,error', [
    ("'\"", JsonPathLexerError),
    ('"\'', JsonPathLexerError),
    ('`"', JsonPathLexerError),
    ("`'", JsonPathLexerError),
    ('"`', JsonPathLexerError),
    ("'`", JsonPathLexerError),
    ('?', JsonPathLexerError),
    ('$.foo.bar.#', JsonPathLexerError),
])
def test_basic_errors(input_token, error):
    def tokenize(s):
        lexer = JsonPathLexer(debug=True)
        return list(lexer.tokenize(s))

    with pytest.raises(error):
        tokenize(input_token)
