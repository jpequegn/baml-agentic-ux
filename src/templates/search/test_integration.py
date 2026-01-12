"""Tests for {{PROJECT_NAME_TITLE}} integration.

These tests demonstrate expected behavior and serve as documentation.
Generated from the SEARCH template on {{CREATED_DATE}}.
"""

import pytest
from integration import (
    load_schema,
    find_component,
    match_invocation,
    extract_search_params,
    calculate_pagination,
    apply_sort,
    generate_feedback,
)


class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_loads_schema(self):
        """Test that schema loads successfully."""
        schema = load_schema()
        assert schema is not None
        assert "schema_id" in schema
        assert "components" in schema

    def test_schema_has_components(self):
        """Test that schema has expected components."""
        schema = load_schema()
        assert len(schema["components"]) >= 5

    def test_schema_domain_is_search(self):
        """Test that schema domain is search-focused."""
        schema = load_schema()
        assert schema["domain"]["subdomain"] == "search-and-discovery"


class TestComponentFinding:
    """Test component finding functionality."""

    def test_finds_search_component(self):
        """Test finding the search component."""
        schema = load_schema()
        component = find_component(schema, "search-items")
        assert component is not None
        assert component["component_type"] == "QUERY"

    def test_finds_filter_component(self):
        """Test finding the filter component."""
        schema = load_schema()
        component = find_component(schema, "filter-results")
        assert component is not None
        assert component["component_type"] == "ACTION"

    def test_finds_sort_component(self):
        """Test finding the sort component."""
        schema = load_schema()
        component = find_component(schema, "sort-results")
        assert component is not None

    def test_finds_paginate_component(self):
        """Test finding the pagination component."""
        schema = load_schema()
        component = find_component(schema, "paginate")
        assert component is not None

    def test_finds_view_details_component(self):
        """Test finding the view details component."""
        schema = load_schema()
        component = find_component(schema, "view-details")
        assert component is not None

    def test_returns_none_for_missing(self):
        """Test that missing components return None."""
        schema = load_schema()
        component = find_component(schema, "nonexistent")
        assert component is None


class TestInvocationMatching:
    """Test invocation pattern matching."""

    def test_matches_search_primary_phrase(self):
        """Test matching search on primary phrase."""
        schema = load_schema()
        component = find_component(schema, "search-items")
        assert match_invocation(component, "search items for laptops")

    def test_matches_search_alternate_phrase(self):
        """Test matching search on alternate phrases."""
        schema = load_schema()
        component = find_component(schema, "search-items")
        assert match_invocation(component, "find items matching wireless")

    def test_matches_filter_phrase(self):
        """Test matching filter component."""
        schema = load_schema()
        component = find_component(schema, "filter-results")
        assert match_invocation(component, "filter results by category")

    def test_matches_sort_phrase(self):
        """Test matching sort component."""
        schema = load_schema()
        component = find_component(schema, "sort-results")
        assert match_invocation(component, "sort by price")

    def test_no_match_on_unrelated_input(self):
        """Test that unrelated input doesn't match."""
        schema = load_schema()
        component = find_component(schema, "search-items")
        assert not match_invocation(component, "delete everything")


class TestSearchParameterExtraction:
    """Test search parameter extraction."""

    def test_extracts_simple_query(self):
        """Test extracting a simple search query."""
        params = extract_search_params("search for laptops")
        assert "query" in params
        assert "laptops" in params["query"]

    def test_extracts_max_price_filter(self):
        """Test extracting maximum price filter."""
        params = extract_search_params("search for phones under $500")
        assert "max_price" in params
        assert params["max_price"] == 500

    def test_extracts_min_price_filter(self):
        """Test extracting minimum price filter."""
        params = extract_search_params("search for tablets over $300")
        assert "min_price" in params
        assert params["min_price"] == 300

    def test_extracts_category_filter(self):
        """Test extracting category filter."""
        params = extract_search_params("search for items in electronics")
        assert "category" in params
        assert params["category"] == "electronics"

    def test_extracts_multiple_filters(self):
        """Test extracting multiple filters together."""
        params = extract_search_params("search for keyboards under $100 in electronics")
        assert "query" in params
        assert "max_price" in params
        assert "category" in params


class TestPaginationCalculations:
    """Test pagination calculation logic."""

    def test_calculates_first_page(self):
        """Test pagination for first page."""
        pagination = calculate_pagination(current_page=1, page_size=20, total_results=100)
        assert pagination["current_page"] == 1
        assert pagination["total_pages"] == 5
        assert pagination["start_index"] == 0
        assert pagination["end_index"] == 20
        assert pagination["has_previous"] is False
        assert pagination["has_next"] is True

    def test_calculates_middle_page(self):
        """Test pagination for middle page."""
        pagination = calculate_pagination(current_page=3, page_size=20, total_results=100)
        assert pagination["current_page"] == 3
        assert pagination["start_index"] == 40
        assert pagination["end_index"] == 60
        assert pagination["has_previous"] is True
        assert pagination["has_next"] is True

    def test_calculates_last_page(self):
        """Test pagination for last page."""
        pagination = calculate_pagination(current_page=5, page_size=20, total_results=100)
        assert pagination["current_page"] == 5
        assert pagination["has_previous"] is True
        assert pagination["has_next"] is False

    def test_calculates_partial_last_page(self):
        """Test pagination when last page is partial."""
        pagination = calculate_pagination(current_page=3, page_size=20, total_results=47)
        assert pagination["total_pages"] == 3
        assert pagination["end_index"] == 47  # Not 60

    def test_handles_single_page(self):
        """Test pagination with only one page."""
        pagination = calculate_pagination(current_page=1, page_size=20, total_results=10)
        assert pagination["total_pages"] == 1
        assert pagination["has_previous"] is False
        assert pagination["has_next"] is False


class TestSortingLogic:
    """Test sorting functionality."""

    def test_sorts_by_price_ascending(self):
        """Test sorting by price (low to high)."""
        results = [
            {"name": "A", "price": 100},
            {"name": "B", "price": 50},
            {"name": "C", "price": 75},
        ]
        sorted_results = apply_sort(results, "price", "asc")
        assert sorted_results[0]["price"] == 50
        assert sorted_results[1]["price"] == 75
        assert sorted_results[2]["price"] == 100

    def test_sorts_by_price_descending(self):
        """Test sorting by price (high to low)."""
        results = [
            {"name": "A", "price": 100},
            {"name": "B", "price": 50},
            {"name": "C", "price": 75},
        ]
        sorted_results = apply_sort(results, "price", "desc")
        assert sorted_results[0]["price"] == 100
        assert sorted_results[1]["price"] == 75
        assert sorted_results[2]["price"] == 50

    def test_sorts_by_rating(self):
        """Test sorting by rating."""
        results = [
            {"name": "A", "rating": 4.0},
            {"name": "B", "rating": 5.0},
            {"name": "C", "rating": 3.5},
        ]
        sorted_results = apply_sort(results, "rating", "desc")
        assert sorted_results[0]["rating"] == 5.0
        assert sorted_results[1]["rating"] == 4.0
        assert sorted_results[2]["rating"] == 3.5

    def test_sorts_by_name(self):
        """Test sorting by name alphabetically."""
        results = [
            {"name": "Charlie"},
            {"name": "Alice"},
            {"name": "Bob"},
        ]
        sorted_results = apply_sort(results, "name", "asc")
        assert sorted_results[0]["name"] == "Alice"
        assert sorted_results[1]["name"] == "Bob"
        assert sorted_results[2]["name"] == "Charlie"

    def test_sorts_by_relevance(self):
        """Test sorting by relevance score."""
        results = [
            {"name": "A", "relevance_score": 0.8},
            {"name": "B", "relevance_score": 0.9},
            {"name": "C", "relevance_score": 0.7},
        ]
        sorted_results = apply_sort(results, "relevance", "desc")
        assert sorted_results[0]["relevance_score"] == 0.9
        assert sorted_results[1]["relevance_score"] == 0.8
        assert sorted_results[2]["relevance_score"] == 0.7


class TestFeedbackGeneration:
    """Test feedback message generation."""

    def test_generates_search_success_feedback(self):
        """Test success feedback for search with result count."""
        schema = load_schema()
        component = find_component(schema, "search-items")

        feedback = generate_feedback(
            component,
            success=True,
            context={"result_count": 42, "query": "laptops"}
        )

        assert "42" in feedback
        assert "laptops" in feedback

    def test_generates_error_feedback(self):
        """Test error feedback generation."""
        schema = load_schema()
        component = find_component(schema, "search-items")

        feedback = generate_feedback(
            component,
            success=False,
            context={"error": "Network timeout"}
        )

        assert "Network timeout" in feedback

    def test_generates_sort_feedback(self):
        """Test feedback for sort action."""
        schema = load_schema()
        component = find_component(schema, "sort-results")

        feedback = generate_feedback(
            component,
            success=True,
            context={"sort_by": "price", "order": "asc"}
        )

        assert "price" in feedback
        assert "asc" in feedback

    def test_generates_pagination_feedback(self):
        """Test feedback for pagination."""
        schema = load_schema()
        component = find_component(schema, "paginate")

        feedback = generate_feedback(
            component,
            success=True,
            context={"current_page": 3, "total_pages": 10}
        )

        assert "3" in feedback
        assert "10" in feedback
