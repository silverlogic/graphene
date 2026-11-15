from ..objecttype import ObjectType
from ..schema import Schema
from ..uuid import UUID
from ..structures import NonNull
from .utils import FOUND, GRAPHQL_CORE_3_3


class Query(ObjectType):
    uuid = UUID(input=UUID())
    required_uuid = UUID(input=NonNull(UUID), required=True)

    def resolve_uuid(self, info, input):
        return input

    def resolve_required_uuid(self, info, input):
        return input


schema = Schema(query=Query)


def test_uuidstring_query():
    uuid_value = "dfeb3bcf-70fd-11e7-a61a-6003088f8204"
    result = schema.execute("""{ uuid(input: "%s") }""" % uuid_value)
    assert not result.errors
    assert result.data == {"uuid": uuid_value}


def test_uuidstring_query_variable():
    uuid_value = "dfeb3bcf-70fd-11e7-a61a-6003088f8204"

    result = schema.execute(
        """query Test($uuid: UUID){ uuid(input: $uuid) }""",
        variables={"uuid": uuid_value},
    )
    assert not result.errors
    assert result.data == {"uuid": uuid_value}


def test_uuidstring_invalid_argument():
    uuid_value = {"not": "a string"}

    result = schema.execute(
        """query Test($uuid: UUID){ uuid(input: $uuid) }""",
        variables={"uuid": uuid_value},
    )
    assert result.errors
    assert len(result.errors) == 1
    if GRAPHQL_CORE_3_3:
        expected = "Variable '$uuid' has invalid value: UUID cannot represent value: {'not': 'a string'}"
    else:
        expected = "Variable '$uuid' got invalid value {'not': 'a string'}; UUID cannot represent value: {'not': 'a string'}"
    assert result.errors[0].message == expected


def test_uuidstring_optional_uuid_input():
    """
    Test that we can provide a null value to an optional input
    """
    result = schema.execute("{ uuid(input: null) }")
    assert not result.errors
    assert result.data == {"uuid": None}


def test_uuidstring_invalid_query():
    """
    Test that if an invalid type is provided we get an error
    """
    result = schema.execute("{ uuid(input: 1) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == f"Expected value of type 'UUID', {FOUND} 1."

    result = schema.execute('{ uuid(input: "a") }')
    assert result.errors
    assert len(result.errors) == 1
    if GRAPHQL_CORE_3_3:
        expected = (
            "Expected value of type 'UUID', but encountered error "
            "'badly formed hexadecimal UUID string'; found: \"a\"."
        )
    else:
        expected = (
            "Expected value of type 'UUID', found \"a\"; "
            "badly formed hexadecimal UUID string"
        )
    assert result.errors[0].message == expected

    result = schema.execute("{ requiredUuid(input: null) }")
    assert result.errors
    assert len(result.errors) == 1
    if GRAPHQL_CORE_3_3:
        expected = "Expected value of non-null type 'UUID!' not to be None."
    else:
        expected = "Expected value of type 'UUID!', found null."
    assert result.errors[0].message == expected
