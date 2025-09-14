# Reusable query builders for test scenarios

def drama_movies_query(min_rating=8.5):
    return {
        "genres": "Drama",
        "imdb.rating": {"$gt": min_rating}
    }

def aggregation_avg_rating_by_year(min_year=2000):
    return [
        {"$match": {"year": {"$gte": min_year}}},
        {"$group": {"_id": "$year", "avgRating": {"$avg": "$imdb.rating"}}},
        {"$sort": {"avgRating": -1}}
    ]

# Query parsing test utilities

def basic_find_queries():
    """Returns a list of basic valid find queries for parsing tests"""
    return [
        {"title": "The Godfather"},
        {"imdb.rating": {"$gt": 8.0}},
        {"year": {"$gte": 2000, "$lte": 2010}},
        {"genres": {"$in": ["Drama", "Action"]}},
        {"cast": {"$exists": True}}
    ]

def invalid_find_queries():
    """Returns a list of invalid queries that should be rejected"""
    return [
        {"$invalidOperator": "value"},
        # Note: {"field": {"$gt": }} would cause Python syntax error, so we test invalid operators instead
        {"": "empty_field_name"},
        {"field": {"$invalidOp": "value"}}
    ]

def complex_nested_query():
    """Returns a complex nested query for testing deep parsing"""
    return {
        "$and": [
            {"genres": "Drama"},
            {
                "$or": [
                    {"imdb.rating": {"$gte": 8.5}},
                    {"awards.wins": {"$gt": 3}}
                ]
            },
            {"cast.0": {"$exists": True}},
            {
                "tomatoes.viewer": {
                    "$elemMatch": {
                        "rating": {"$gte": 4.0},
                        "numReviews": {"$gt": 100}
                    }
                }
            }
        ]
    }

def valid_aggregation_pipelines():
    """Returns valid aggregation pipelines for parsing tests"""
    return [
        # Basic pipeline
        [
            {"$match": {"genres": "Drama"}},
            {"$sort": {"imdb.rating": -1}},
            {"$limit": 10}
        ],
        # Complex pipeline with multiple stages
        [
            {"$match": {"imdb.rating": {"$exists": True}}},
            {"$group": {
                "_id": "$year",
                "avgRating": {"$avg": "$imdb.rating"},
                "count": {"$sum": 1},
                "topMovie": {"$first": "$title"}
            }},
            {"$sort": {"avgRating": -1}},
            {"$project": {
                "year": "$_id",
                "avgRating": {"$round": ["$avgRating", 2]},
                "movieCount": "$count",
                "topMovie": 1,
                "_id": 0
            }}
        ]
    ]

def invalid_aggregation_pipelines():
    """Returns invalid aggregation pipelines that should be rejected"""
    return [
        # Invalid stage name
        [{"$invalidStage": {"field": "value"}}],
        # Invalid operator in $group
        [{"$group": {"_id": "$field", "result": {"$invalidAccumulator": "$value"}}}],
        # Empty pipeline
        [],
        # Invalid stage structure
        [{"$match": "invalid_structure"}]
    ]
