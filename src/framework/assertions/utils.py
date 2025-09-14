# Custom assertion helpers for tests
from pymongo.errors import OperationFailure

def assert_docs_not_empty(docs, msg="No documents returned"):
    print("Log: Documents size = "+str(len(docs)))
    assert len(docs) > 0, msg

def assert_field_exists(doc, field):
    assert field in doc, f"Missing field: {field}"

# Parsing-specific assertions

def assert_query_executes_successfully(collection, query, msg="Query should execute successfully"):
    """Assert that a query executes without errors"""
    try:
        print(f"Log: Executing query: {query}")
        result = list(collection.find(query))
        print(f"Log: Query executed successfully, returned {len(result)} documents")
    except Exception as e:
        print(f"Log: Query failed: {query}")
        assert False, f"{msg}. Error: {str(e)}"

def assert_query_fails_with_error(collection, query, expected_error_type=OperationFailure, msg="Query should fail"):
    """Assert that a query fails with expected error"""
    try:
        print(f"Log: Executing query (expecting failure): {query}")
        list(collection.find(query))
        assert False, f"{msg}. Query unexpectedly succeeded"
    except expected_error_type as e:
        print(f"Log: Query failed as expected with error: {str(e)}")
    except Exception as e:
        assert False, f"{msg}. Got unexpected error type {type(e)}: {str(e)}"

def assert_aggregation_executes_successfully(collection, pipeline, msg="Aggregation should execute successfully"):
    """Assert that an aggregation pipeline executes without errors"""
    try:
        print(f"Log: Executing aggregation pipeline: {pipeline}")
        result = list(collection.aggregate(pipeline))
        print(f"Log: Aggregation executed successfully, returned {len(result)} documents")
    except Exception as e:
        print(f"Log: Aggregation failed: {pipeline}")
        assert False, f"{msg}. Error: {str(e)}"

def assert_aggregation_fails_with_error(collection, pipeline, expected_error_type=OperationFailure, msg="Aggregation should fail"):
    """Assert that an aggregation pipeline fails with expected error"""
    try:
        print(f"Log: Executing aggregation pipeline (expecting failure): {pipeline}")
        list(collection.aggregate(pipeline))
        assert False, f"{msg}. Aggregation unexpectedly succeeded"
    except expected_error_type as e:
        print(f"Log: Aggregation failed as expected with error: {str(e)}")
    except Exception as e:
        assert False, f"{msg}. Got unexpected error type {type(e)}: {str(e)}"

def assert_query_result_structure(docs, expected_fields, msg="Query result should have expected structure"):
    """Assert that query results have expected field structure"""
    assert len(docs) > 0, "No documents to validate structure"
    
    for doc in docs:
        for field in expected_fields:
            assert field in doc, f"{msg}. Missing field '{field}' in document: {doc}"
    
    print(f"Log: Validated structure of {len(docs)} documents with fields: {expected_fields}")

def assert_data_types_correct(docs, field_types, msg="Query result should have correct data types"):
    """Assert that query results have correct data types for specified fields"""
    assert len(docs) > 0, "No documents to validate data types"
    
    for doc in docs:
        for field, expected_type in field_types.items():
            if field in doc:
                actual_type = type(doc[field])
                assert isinstance(doc[field], expected_type), \
                    f"{msg}. Field '{field}' should be {expected_type}, got {actual_type}: {doc[field]}"
    
    print(f"Log: Validated data types for {len(docs)} documents")
