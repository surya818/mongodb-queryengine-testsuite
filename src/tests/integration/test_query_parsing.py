from src.framework.database.client import db
from src.framework.queries.utils import (
    drama_movies_query, basic_find_queries, invalid_find_queries, 
    complex_nested_query, valid_aggregation_pipelines, invalid_aggregation_pipelines
)
from src.framework.assertions.utils import (
    assert_docs_not_empty, assert_query_executes_successfully, assert_query_fails_with_error,
    assert_aggregation_executes_successfully, assert_aggregation_fails_with_error,
    assert_query_result_structure, assert_data_types_correct
)
import pytest
from pymongo.errors import OperationFailure
from datetime import datetime
from bson import ObjectId

def test_drama_movies_basic():
    query = drama_movies_query()
    projection = {"title":1,"imdb.rating":1,"_id":0}
    print(f"Log: Executing basic drama movies query: {query} with projection: {projection}")
    docs = list(db.movies.find(query, projection))
    assert_docs_not_empty(docs)

# =============================================================================
# Basic MQL Syntax Validation 
# =============================================================================

def test_basic_valid_find_queries():
    """Test basic valid find query syntax parsing"""
    queries = basic_find_queries()
    
    for i, query in enumerate(queries):
        print(f"Testing valid query {i+1}: {query}")
        assert_query_executes_successfully(db.movies, query, f"Valid query {i+1} should parse and execute")

def test_comparison_operators():
    """Test all comparison operators parse correctly"""
    comparison_queries = [
        {"imdb.rating": {"$eq": 8.0}},
        {"imdb.rating": {"$ne": 5.0}}, 
        {"imdb.rating": {"$gt": 7.0}},
        {"imdb.rating": {"$gte": 7.5}},
        {"imdb.rating": {"$lt": 9.0}},
        {"imdb.rating": {"$lte": 8.5}}
    ]
    
    for query in comparison_queries:
        operator = list(query["imdb.rating"].keys())[0]
        print(f"Testing comparison operator: {operator}")
        assert_query_executes_successfully(db.movies, query, f"Comparison operator {operator} should parse correctly")

def test_logical_operators():
    """Test logical operators parse correctly"""
    logical_queries = [
        {"$and": [{"genres": "Drama"}, {"imdb.rating": {"$gte": 8.0}}]},
        {"$or": [{"genres": "Action"}, {"genres": "Adventure"}]},
        {"genres": {"$not": {"$eq": "Horror"}}}
    ]
    
    for query in logical_queries:
        operator = list(query.keys())[0] if not query.get("genres") else "$not (nested)"
        print(f"Testing logical operator: {operator}")
        assert_query_executes_successfully(db.movies, query, f"Logical operator {operator} should parse correctly")

def test_array_operators():
    """Test array operators parse correctly"""
    array_queries = [
        {"genres": {"$in": ["Drama", "Action", "Comedy"]}},
        {"genres": {"$nin": ["Horror", "Thriller"]}},
        {"cast": {"$all": ["Tom Hanks"]}},
        {"genres": {"$size": 3}},
        {"awards": {"$exists": True}}
    ]
    
    for query in array_queries:
        field = list(query.keys())[0]
        operator = list(query[field].keys())[0] if isinstance(query[field], dict) else "direct"
        print(f"Testing array operator {operator} on field {field}")
        assert_query_executes_successfully(db.movies, query, f"Array operator {operator} should parse correctly")

def test_data_type_handling():
    """Test various BSON data types parse correctly"""
    # Test different data types in queries
    type_queries = [
        {"title": "The Godfather"},  # String
        {"year": 1972},  # Number (int)
        {"imdb.rating": 9.2},  # Number (float)
        {"_id": ObjectId("507f1f77bcf86cd799439011") if ObjectId.is_valid("507f1f77bcf86cd799439011") else ObjectId()},  # ObjectId
    ]
    
    for query in type_queries:
        field = list(query.keys())[0]
        value_type = type(query[field]).__name__
        print(f"Testing data type {value_type} for field {field}")
        print(f"Log: Executing query: {query}")
        # These should parse correctly even if no documents match
        try:
            result = list(db.movies.find(query).limit(1))
            print(f"Log: Data type {value_type} parsed successfully, returned {len(result)} documents")
        except Exception as e:
            pytest.fail(f"Data type {value_type} should parse correctly, got error: {str(e)}")

def test_invalid_syntax_rejection():
    # Test invalid operator (should cause OperationFailure)
    invalid_queries = [
        {"field": {"$invalidOperator": "value"}},
        {"field": {"$invalidOp": "value"}}
    ]
    
    for i, query in enumerate(invalid_queries):
        print(f"Testing invalid query {i+1}: {query}")
        assert_query_fails_with_error(db.movies, query, OperationFailure, f"Invalid query {i+1} should be rejected")

def test_complex_nested_query():
    """Test complex nested query structure parsing"""
    query = complex_nested_query()
    print(f"Testing complex nested query: {query}")
    assert_query_executes_successfully(db.movies, query, "Complex nested query should parse correctly")

def test_deep_field_path_queries():
    """Test deep field path (dot notation) parsing"""
    deep_field_queries = [
        {"imdb.rating": {"$gte": 8.0}},
        {"imdb.votes": {"$exists": True}},
        {"tomatoes.viewer.rating": {"$gte": 4.0}},
        {"cast.0": {"$exists": True}},  # Array index access
        {"awards.wins": {"$gt": 0}}
    ]
    
    for query in deep_field_queries:
        field = list(query.keys())[0]
        print(f"Testing deep field path: {field}")
        assert_query_executes_successfully(db.movies, query, f"Deep field path {field} should parse correctly")

def test_elemMatch_complex_parsing():
    """Test $elemMatch with complex expressions"""
    elemMatch_queries = [
        {"cast": {"$elemMatch": {"$eq": "Tom Hanks"}}},
        {"genres": {"$elemMatch": {"$in": ["Drama", "Action"]}}},
        # More complex nested elemMatch would go here if data structure supports it
    ]
    
    for query in elemMatch_queries:
        print(f"Testing $elemMatch query: {query}")
        assert_query_executes_successfully(db.movies, query, "$elemMatch should parse correctly")

def test_mixed_operator_combinations():
    """Test combinations of different operator types"""
    mixed_queries = [
        {
            "imdb.rating": {"$gte": 7.0, "$lte": 9.0},
            "genres": {"$in": ["Drama", "Action"]},
            "year": {"$exists": True}
        },
        {
            "$and": [
                {"genres": {"$nin": ["Horror"]}},
                {"$or": [
                    {"imdb.rating": {"$gte": 8.5}},
                    {"awards.wins": {"$gt": 2}}
                ]}
            ]
        }
    ]
    
    for i, query in enumerate(mixed_queries):
        print(f"Testing mixed operator query {i+1}: {query}")
        assert_query_executes_successfully(db.movies, query, f"Mixed operator query {i+1} should parse correctly")

def test_query_result_structure_validation():
    """Test that complex queries return properly structured results"""
    query = {"genres": "Drama", "imdb.rating": {"$gte": 8.0}}
    projection = {"title": 1, "imdb.rating": 1, "year": 1, "_id": 0}
    
    print(f"Log: Executing complex query: {query} with projection: {projection}")
    docs = list(db.movies.find(query, projection).limit(5))
    print(f"Log: Complex query executed successfully, returned {len(docs)} documents")
    assert_docs_not_empty(docs, "Complex query should return results")
    
    expected_fields = ["title", "imdb", "year"]
    assert_query_result_structure(docs, expected_fields, "Complex query results should have expected structure")
    
    # Validate data types
    field_types = {
        "title": str,
        "year": (int, float),  # Could be either
        "imdb": dict
    }
    assert_data_types_correct(docs, field_types, "Complex query results should have correct data types")

# =============================================================================
# QP-003: Aggregation Pipeline Syntax Validation (Priority P1)
# =============================================================================

def test_basic_aggregation_pipeline():
    """Test basic aggregation pipeline parsing"""
    pipelines = valid_aggregation_pipelines()
    
    for i, pipeline in enumerate(pipelines):
        print(f"Testing valid pipeline {i+1}: {pipeline}")
        assert_aggregation_executes_successfully(db.movies, pipeline, f"Valid pipeline {i+1} should parse and execute")

def test_aggregation_stage_validation():
    """Test individual aggregation stage parsing"""
    individual_stages = [
        [{"$match": {"genres": "Drama"}}],
        [{"$sort": {"imdb.rating": -1}}],
        [{"$limit": 10}],
        [{"$skip": 5}],
        [{"$group": {"_id": "$year", "count": {"$sum": 1}}}],
        [{"$project": {"title": 1, "rating": "$imdb.rating", "_id": 0}}]
    ]
    
    for stage_pipeline in individual_stages:
        stage_name = list(stage_pipeline[0].keys())[0]
        print(f"Testing aggregation stage: {stage_name}")
        assert_aggregation_executes_successfully(db.movies, stage_pipeline, f"Stage {stage_name} should parse correctly")


def test_invalid_aggregation_syntax():
    """Test that invalid aggregation syntax is rejected"""
    invalid_pipelines = invalid_aggregation_pipelines()
    
    # Skip empty pipeline test as it might be valid in some contexts
    test_pipelines = [p for p in invalid_pipelines if p != []]
    
    for i, pipeline in enumerate(test_pipelines):
        print(f"Testing invalid pipeline {i+1}: {pipeline}")
        assert_aggregation_fails_with_error(db.movies, pipeline, OperationFailure, f"Invalid pipeline {i+1} should be rejected")

def test_aggregation_result_validation():
    """Test aggregation results have correct structure and expected data types"""
    pipeline = [
        {"$match": {"genres": "Drama", "imdb.rating": {"$exists": True}}},
        {"$group": {
            "_id": "$year",
            "avgRating": {"$avg": "$imdb.rating"},
            "count": {"$sum": 1},
            "maxRating": {"$max": "$imdb.rating"}
        }},
        {"$sort": {"avgRating": -1}},
        {"$limit": 3}
    ]
    
    print(f"Log: Executing aggregation pipeline: {pipeline}")
    docs = list(db.movies.aggregate(pipeline))
    print(f"Log: Aggregation executed successfully, returned {len(docs)} documents")
    assert_docs_not_empty(docs, "Aggregation should return results")
    assert len(docs) == 3
    expected_fields = ["_id", "avgRating", "count", "maxRating"] 
    assert_query_result_structure(docs, expected_fields, "Aggregation results should have expected structure")
    
    # Validate aggregation result data types (note: _id can be various types depending on data)
    field_types = {
        "avgRating": (int, float),
        "count": int,
        "maxRating": (int, float)
    }
    assert_data_types_correct(docs, field_types, "Aggregation results should have correct data types")
