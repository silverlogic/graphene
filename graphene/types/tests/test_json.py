from ..json import JSONString
from ..objecttype import ObjectType
from ..schema import Schema
from .utils import FOUND, GRAPHQL_CORE_3_3


class Query(ObjectType):
    json = JSONString(input=JSONString())

    def resolve_json(self, info, input):
        return input


schema = Schema(query=Query)


def test_jsonstring_query():
    json_value = '{"key": "value"}'

    json_value_quoted = json_value.replace('"', '\\"')
    result = schema.execute("""{ json(input: "%s") }""" % json_value_quoted)
    assert not result.errors
    assert result.data == {"json": json_value}

    result = schema.execute("""{ json(input: "{}") }""")
    assert not result.errors
    assert result.data == {"json": "{}"}


def test_jsonstring_query_variable():
    json_value = '{"key": "value"}'

    result = schema.execute(
        """query Test($json: JSONString){ json(input: $json) }""",
        variables={"json": json_value},
    )
    assert not result.errors
    assert result.data == {"json": json_value}


def test_jsonstring_optional_uuid_input():
    """
    Test that we can provide a null value to an optional input
    """
    result = schema.execute("{ json(input: null) }")
    assert not result.errors
    assert result.data == {"json": None}


def test_jsonstring_invalid_query():
    """
    Test that if an invalid type is provided we get an error
    """
    result = schema.execute("{ json(input: 1) }")
    assert result.errors == [
        {"message": f"Expected value of type 'JSONString', {FOUND} 1."},
    ]

    result = schema.execute("{ json(input: {}) }")
    empty_object = "{  }" if GRAPHQL_CORE_3_3 else "{}"
    assert result.errors == [
        {"message": f"Expected value of type 'JSONString', {FOUND} {empty_object}."},
    ]

    result = schema.execute('{ json(input: "a") }')
    if GRAPHQL_CORE_3_3:
        expected = (
            "Expected value of type 'JSONString', but encountered error "
            "'Badly formed JSONString: Expecting value: line 1 column 1 (char 0)'; "
            'found: "a".'
        )
    else:
        expected = (
            "Expected value of type 'JSONString', found \"a\"; "
            "Badly formed JSONString: Expecting value: line 1 column 1 (char 0)"
        )
    assert result.errors == [{"message": expected}]

    result = schema.execute("""{ json(input: "{\\'key\\': 0}") }""")
    assert result.errors == [
        {"message": "Syntax Error: Invalid character escape sequence: '\\''."},
    ]

    result = schema.execute("""{ json(input: "{\\"key\\": 0,}") }""")
    assert len(result.errors) == 1
    if GRAPHQL_CORE_3_3:
        assert result.errors[0].message.startswith(
            "Expected value of type 'JSONString', but encountered error "
            "'Badly formed JSONString:"
        )
        assert result.errors[0].message.endswith('found: "{\\"key\\": 0,}".')
    else:
        assert result.errors[0].message.startswith(
            'Expected value of type \'JSONString\', found "{\\"key\\": 0,}"; Badly formed JSONString:'
        )
