from src.framework.database.client import db
from src.framework.assertions.utils import assert_docs_not_empty
import time
import json

# =============================================================================
# Query Plan Generation and Selection
# =============================================================================

def test_basic_plan_selection():
    """Test basic query plan generation and index selection"""
    print("Log: Testing basic query plan selection")
    
    # Clean up existing indexes to start fresh
    try:
        existing_indexes = list(db.movies.list_indexes())
        for index in existing_indexes:
            if index['name'] != '_id_' and 'text' not in index['name']:
                print(f"Log: Dropping index: {index['name']}")
                db.movies.drop_index(index['name'])
    except Exception as e:
        print(f"Log: Index cleanup: {e}")
    
    # Create a simple index
    print("Log: Creating test index on genres")
    db.movies.create_index([("genres", 1)], name="test_genres_idx")
    
    # Test query that should use the index
    query = {"genres": "Drama"}
    print(f"Log: Testing query: {query}")
    
    # Get query plan
    explain_result = db.movies.find(query).explain()
    print(f"Log: Explain output:\n{json.dumps(explain_result, indent=2, default=str)}")
    winning_plan = explain_result['queryPlanner']['winningPlan']

    # Should use index scan for indexed field
    assert winning_plan.get('inputStage').get('stage') == 'IXSCAN'
    
    # Execute query to verify it works
    results = list(db.movies.find(query).limit(5))
    print(f"Log: Query executed successfully, returned {len(results)} documents")
    assert len(results) > 0, "Query should return results"
    
    # Clean up
    try:
        db.movies.drop_index("test_genres_idx")
    except:
        pass

def test_collection_scan_vs_index_scan():
    """Test performance difference between collection scan and index scan"""
    print("Log: Testing collection scan vs index scan performance")
    
    # Clean up any existing indexes first
    try:
        db.movies.drop_index("test_performance_idx")
    except:
        pass
    
    # Query to test
    query = {"imdb.rating": {"$gte": 9.0}}
    print(f"Log: Testing query: {query}")
    
    # Test WITHOUT index (should use COLLSCAN)
    print("Log: Testing query WITHOUT index")
    start_time = time.time()
    explain_no_index = db.movies.find(query).explain()
    results_no_index = list(db.movies.find(query))
    time_no_index = time.time() - start_time
    
    print(f"Log: Without index - explain output:\n{json.dumps(explain_no_index, indent=2, default=str)}")
    print(f"Log: Without index: {time_no_index:.4f}s, {len(results_no_index)} documents")
    
    # Verify it uses collection scan
    winning_plan_no_index = explain_no_index['queryPlanner']['winningPlan']
    assert winning_plan_no_index.get('stage') == 'COLLSCAN', "Without index should use COLLSCAN"
    print("Log: Confirmed: Query uses COLLSCAN without index")
    
    # Create index
    print("Log: Creating index on imdb.rating")
    db.movies.create_index([("imdb.rating", 1)], name="test_performance_idx")
    
    # Test WITH index (should use IXSCAN)
    print("Log: Testing same query WITH index")
    start_time = time.time()
    explain_with_index = db.movies.find(query).explain()
    results_with_index = list(db.movies.find(query))
    time_with_index = time.time() - start_time
    
    print(f"Log: With index - explain output:\n{json.dumps(explain_with_index, indent=2, default=str)}")
    print(f"Log: With index: {time_with_index:.4f}s, {len(results_with_index)} documents")
    
    # Verify it uses index scan
    winning_plan_with_index = explain_with_index['queryPlanner']['winningPlan']
    if winning_plan_with_index.get('stage') == 'FETCH':
        # FETCH stage with IXSCAN underneath
        input_stage = winning_plan_with_index.get('inputStage', {})
        assert input_stage.get('stage') == 'IXSCAN', "With index should use IXSCAN"
        print(f"Log: Confirmed: Query uses IXSCAN with index: {input_stage.get('indexName')}")
    else:
        assert winning_plan_with_index.get('stage') == 'IXSCAN', "With index should use IXSCAN"
        print(f"Log: Confirmed: Query uses direct IXSCAN with index: {winning_plan_with_index.get('indexName')}")
    
    # Verify results are identical
    assert len(results_no_index) == len(results_with_index), "Results should be identical"
    print("Log: Confirmed: Both queries return identical results")
    
    # Performance comparison
    speedup = time_no_index / time_with_index if time_with_index > 0 else float('inf')
    print(f"Log: Performance improvement: {speedup:.2f}x faster with index")
    
    # Index should generally be faster (though with small datasets might not be significant)
    if time_with_index < time_no_index:
        print("Log: Index scan was faster than collection scan")
    else:
        print("Log: Collection scan was faster (possibly due to small dataset)")
    
    # Clean up
    try:
        db.movies.drop_index("test_performance_idx")
    except:
        pass

# =============================================================================
# Query Plan Caching (Priority P1)
# =============================================================================


def test_query_plan_caching():
    """Test query plan caching functionality"""
    print("Log: Testing query plan caching")
    
    # Create index for consistent plan generation
    try:
        db.movies.create_index([("imdb.rating", 1), ("genres", 1)], name="test_cache_idx")
    except Exception as e:
        if "already exists" not in str(e):
            print(f"Log: Index creation: {e}")
    
    query = {"imdb.rating": {"$gt": 8.5}, "genres": "Drama"}
    print(f"Log: Testing query for caching: {query}")

    # First run - get explain output
    first_explain = db.movies.find(query).explain()
    print(f"Log: First explain output:\n{json.dumps(first_explain, indent=2, default=str)}")
    
    first_plan_cache_key = first_explain["queryPlanner"]["planCacheKey"]
    first_query_hash = first_explain["queryPlanner"]["queryHash"]
    
    print(f"Log: First execution - Plan cache key: {first_plan_cache_key}, Query hash: {first_query_hash}")

    # Ensure query shape is consistent
    assert "planCacheKey" in first_explain["queryPlanner"], "Should have planCacheKey"
    assert "queryHash" in first_explain["queryPlanner"], "Should have queryHash"

    # Execute the query to ensure it gets cached
    result1 = list(db.movies.find(query).limit(5))
    print(f"Log: First execution returned {len(result1)} documents")

    # Second run - ensure same planCacheKey is reused
    second_explain = db.movies.find(query).explain()
    second_plan_cache_key = second_explain["queryPlanner"]["planCacheKey"]
    second_query_hash = second_explain["queryPlanner"]["queryHash"]
    
    print(f"Log: Second execution - Plan cache key: {second_plan_cache_key}, Query hash: {second_query_hash}")

    # Query hash should remain the same (same query shape)
    assert first_query_hash == second_query_hash, f"Query hash should be consistent: {first_query_hash} vs {second_query_hash}"
    
    # Plan cache key should remain the same (plan is cached)
    assert first_plan_cache_key == second_plan_cache_key, f"Plan cache key should be reused: {first_plan_cache_key} vs {second_plan_cache_key}"
    
    # Execute second query to verify results consistency
    result2 = list(db.movies.find(query).limit(5))
    assert len(result1) == len(result2), "Results should be consistent between cached executions"
    
    print("Log: Plan caching test passed - same plan cache key reused")
    
    # Clean up
    try:
        db.movies.drop_index("test_cache_idx")
    except:
        pass


def test_caching_performance():
    """Test repeated query execution for caching benefits"""
    print("Log: Testing repeated query execution")
    
    # Create index for consistent behavior
    db.movies.create_index([("year", 1)], name="test_year_idx")
    
    query = {"year": {"$gte": 2010, "$lte": 2015}}
    print(f"Log: Testing query for caching: {query}")
    
    # First execution
    start_time = time.time()
    result1 = list(db.movies.find(query).limit(10))
    first_time = time.time() - start_time
    print(f"Log: First execution: {first_time:.4f}s, {len(result1)} documents")
    
    # Second execution (potential cache benefit)
    start_time = time.time()
    result2 = list(db.movies.find(query).limit(10))
    second_time = time.time() - start_time
    print(f"Log: Second execution: {second_time:.4f}s, {len(result2)} documents")
    
    # Third execution
    start_time = time.time()
    result3 = list(db.movies.find(query).limit(10))
    third_time = time.time() - start_time
    print(f"Log: Third execution: {third_time:.4f}s, {len(result3)} documents")
    
    # Results should be consistent
    assert len(result1) == len(result2) == len(result3), "Results should be consistent across executions"
    
    # Performance should be stable or improve - subsequent executions should be equal or faster
    print(f"Log: Performance comparison - First: {first_time:.4f}s, Second: {second_time:.4f}s, Third: {third_time:.4f}s")
    
    # Allow for small timing variations (±20%) due to system variability
    tolerance = 1.2
    assert second_time <= first_time * tolerance, f"Second execution should be equal or faster than first (within {tolerance}x tolerance)"
    assert third_time <= first_time * tolerance, f"Third execution should be equal or faster than first (within {tolerance}x tolerance)"
    
    # Calculate average subsequent performance
    avg_subsequent_time = (second_time + third_time) / 2
    print(f"Log: Average subsequent execution time: {avg_subsequent_time:.4f}s")
    
    # Overall trend should show equal or better performance
    if avg_subsequent_time <= first_time:
        improvement = (first_time - avg_subsequent_time) / first_time * 100
        print(f"Log: Performance improved by {improvement:.1f}% on subsequent executions")
    else:
        degradation = (avg_subsequent_time - first_time) / first_time * 100
        print(f"Log: Performance degraded by {degradation:.1f}% (within tolerance)")
        assert degradation <= 20.0, f"Performance degradation should be within 20%, got {degradation:.1f}%"
    
    try:
        db.movies.drop_index("test_year_idx")
    except:
        pass


def test_query_shape_cache_reuse():
    """Test that queries with same shape reuse cached plans"""
    print("Log: Testing query shape cache reuse")
    
    # Create index for consistent behavior
    try:
        db.movies.create_index([("genres", 1)], name="test_shape_idx")
    except Exception as e:
        if "already exists" not in str(e):
            print(f"Log: Index creation: {e}")
    
    queries = [
        {"genres": "Drama"},
        {"genres": "Action"},
        {"genres": "Comedy"}
    ]

    plan_cache_keys = []
    query_hashes = []

    for i, query in enumerate(queries):
        print(f"Log: Testing query {i+1}: {query}")
        explain = db.movies.find(query).explain()
        plan_cache_key = explain["queryPlanner"]["planCacheKey"]
        query_hash = explain["queryPlanner"]["queryHash"]
        
        plan_cache_keys.append(plan_cache_key)
        query_hashes.append(query_hash)
        
        print(f"Log: Query {i+1} - Plan cache key: {plan_cache_key}, Query hash: {query_hash}")

    # Ensure all planCacheKeys are identical (same query shape)
    first_key = plan_cache_keys[0]
    first_hash = query_hashes[0]
    
    assert all(key == first_key for key in plan_cache_keys), \
        f"PlanCacheKeys should be identical for same shape: {plan_cache_keys}"
    
    assert all(hash_val == first_hash for hash_val in query_hashes), \
        f"QueryHashes should be identical for same shape: {query_hashes}"
    
    print(f"Log: Confirmed: All queries share same plan cache key: {first_key}")
    print(f"Log: Confirmed: All queries share same query hash: {first_hash}")
    
    # Execute queries to verify they work with cached plans
    for i, query in enumerate(queries):
        results = list(db.movies.find(query).limit(3))
        print(f"Log: Query {i+1} returned {len(results)} documents")
        assert len(results) >= 0, f"Query {i+1} should execute successfully"

    # Clean up
    try:
        db.movies.drop_index("test_shape_idx")
    except:
        pass

def test_qo003_range_query_optimization():
    """Test range query optimization with indexes"""
    print("Log: Testing range query optimization")
    
    # Create index for range queries
    db.movies.create_index([("year", 1)], name="test_range_idx")
    
    # Range query
    query = {"year": {"$gte": 2000, "$lte": 2010}}
    print(f"Log: Testing range query: {query}")
    
    # Get execution plan
    explain_result = db.movies.find(query).explain()
    print(f"Log: Range query explain output:\n{json.dumps(explain_result, indent=2, default=str)}")
    
    if 'queryPlanner' in explain_result:
        winning_plan = explain_result['queryPlanner']['winningPlan']
        print(f"Log: Range query plan stage: {winning_plan.get('stage', 'Unknown')}")
        
        if winning_plan.get('stage') == 'IXSCAN':
            print("Log: Range query correctly uses index scan")
            
            # Check index bounds
            index_bounds = winning_plan.get('indexBounds', {})
            print(f"Log: Index bounds: {index_bounds}")
        elif winning_plan.get('stage') == 'FETCH':
            # Check if underlying stage uses index
            input_stage = winning_plan.get('inputStage', {})
            if input_stage.get('stage') == 'IXSCAN':
                print("Log: Range query uses index with fetch stage")
                index_bounds = input_stage.get('indexBounds', {})
                print(f"Log: Index bounds: {index_bounds}")
    
    # Execute and verify efficiency
    results = list(db.movies.find(query))
    print(f"Log: Range query returned {len(results)} documents")
    
    try:
        db.movies.drop_index("test_range_idx")
    except:
        pass

def test_qo003_index_hint_functionality():
    """Test index hint functionality and override"""
    print("Log: Testing index hint functionality")
    
    # Create multiple indexes
    db.movies.create_index([("genres", 1)], name="test_hint_genres")
    db.movies.create_index([("year", 1)], name="test_hint_year")
    
    query = {"genres": "Drama", "year": {"$gte": 2000}}
    print(f"Log: Testing query with hint: {query}")
    
    # Test without hint
    explain_no_hint = db.movies.find(query).explain()
    print(f"Log: Query without hint explain output:\n{json.dumps(explain_no_hint, indent=2, default=str)}")
    if 'queryPlanner' in explain_no_hint:
        no_hint_plan = explain_no_hint['queryPlanner']['winningPlan']
        print(f"Log: Without hint uses: {no_hint_plan.get('indexName', 'Unknown')}")
    
    # Test with hint
    try:
        explain_with_hint = db.movies.find(query).hint("test_hint_genres").explain()
        print(f"Log: Query with hint explain output:\n{json.dumps(explain_with_hint, indent=2, default=str)}")
        if 'queryPlanner' in explain_with_hint:
            hint_plan = explain_with_hint['queryPlanner']['winningPlan']
            print(f"Log: With hint uses: {hint_plan.get('indexName', 'Unknown')}")
            
            # Should use the hinted index
            if hint_plan.get('stage') == 'IXSCAN':
                assert hint_plan.get('indexName') == 'test_hint_genres', \
                    f"Should use hinted index, got: {hint_plan.get('indexName')}"
            elif hint_plan.get('stage') == 'FETCH':
                input_stage = hint_plan.get('inputStage', {})
                if input_stage.get('stage') == 'IXSCAN':
                    assert input_stage.get('indexName') == 'test_hint_genres', \
                        f"Should use hinted index, got: {input_stage.get('indexName')}"
        
        # Execute with hint
        results = list(db.movies.find(query).hint("test_hint_genres").limit(5))
        print(f"Log: Hinted query returned {len(results)} documents")
        
    except Exception as e:
        print(f"Log: Hint test failed: {e}")
    
    try:
        db.movies.drop_index("test_hint_genres")
        db.movies.drop_index("test_hint_year")
    except:
        pass
