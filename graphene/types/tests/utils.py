from graphql import version_info as graphql_version_info

MyLazyType = object()

# graphql-core 3.3 changed the wording of some validation error messages.
GRAPHQL_CORE_3_3 = graphql_version_info >= (3, 3)
# "Expected value of type 'X', found Y." became "... found: Y."
FOUND = "found:" if GRAPHQL_CORE_3_3 else "found"
