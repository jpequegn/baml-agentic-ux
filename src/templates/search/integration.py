"""{{PROJECT_NAME_TITLE}} - Integration Example.

This module demonstrates how to use a search-focused LUI schema with the BAML client.
Generated from the SEARCH template on {{CREATED_DATE}}.
"""

import json
from pathlib import Path
from typing import Any


def load_schema() -> dict:
    """Load the LUI schema from schema.json.

    Returns:
        The parsed schema dictionary
    """
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


def find_component(schema: dict, component_id: str) -> dict | None:
    """Find a component by ID in the schema.

    Args:
        schema: The loaded schema
        component_id: ID of the component to find

    Returns:
        The component dictionary or None if not found
    """
    for component in schema.get("components", []):
        if component.get("component_id") == component_id:
            return component
    return None


def match_invocation(component: dict, user_input: str) -> bool:
    """Check if user input matches a component's invocation patterns.

    This is a simplified matcher - in production, use BAML's
    ExtractIntent function for intelligent matching.

    Args:
        component: The component to match against
        user_input: The user's input text

    Returns:
        True if the input matches any invocation pattern
    """
    invocation = component.get("invocation", {})
    user_lower = user_input.lower()

    # Check primary phrase
    if invocation.get("primary_phrase", "").lower() in user_lower:
        return True

    # Check alternate phrases
    for alt in invocation.get("alternate_phrases", []):
        if alt.lower() in user_lower:
            return True

    return False


def extract_search_params(user_input: str) -> dict[str, Any]:
    """Extract search parameters from user input.

    This is a simplified extractor - in production, use BAML's
    parameter extraction with proper type handling.

    Args:
        user_input: The user's input text

    Returns:
        Dictionary of extracted parameters
    """
    params = {}
    user_lower = user_input.lower()

    # Extract query (simplified - just take the input after "search for")
    if "search for" in user_lower:
        query_start = user_lower.find("search for") + len("search for")
        query = user_input[query_start:].strip()
        # Remove filter phrases
        for phrase in ["under $", "in ", "category"]:
            if phrase in query.lower():
                query = query[: query.lower().find(phrase)].strip()
        params["query"] = query

    # Extract price filters
    if "under $" in user_lower:
        try:
            price_str = user_lower.split("under $")[1].split()[0]
            params["max_price"] = float(price_str.replace(",", ""))
        except (IndexError, ValueError):
            pass

    if "over $" in user_lower or "above $" in user_lower:
        try:
            marker = "over $" if "over $" in user_lower else "above $"
            price_str = user_lower.split(marker)[1].split()[0]
            params["min_price"] = float(price_str.replace(",", ""))
        except (IndexError, ValueError):
            pass

    # Extract category
    if " in " in user_lower:
        try:
            category = user_lower.split(" in ")[1].split()[0]
            params["category"] = category
        except IndexError:
            pass

    return params


def calculate_pagination(
    current_page: int, page_size: int, total_results: int
) -> dict[str, Any]:
    """Calculate pagination information.

    Args:
        current_page: Current page number (1-indexed)
        page_size: Number of results per page
        total_results: Total number of results

    Returns:
        Dictionary with pagination details
    """
    total_pages = (total_results + page_size - 1) // page_size  # Ceiling division
    start_index = (current_page - 1) * page_size
    end_index = min(start_index + page_size, total_results)

    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "page_size": page_size,
        "total_results": total_results,
        "start_index": start_index,
        "end_index": end_index,
        "has_previous": current_page > 1,
        "has_next": current_page < total_pages,
    }


def apply_sort(results: list[dict], sort_by: str, order: str = "asc") -> list[dict]:
    """Sort search results by specified criteria.

    Args:
        results: List of result dictionaries
        sort_by: Field to sort by (relevance, price, date, rating, name)
        order: Sort order ('asc' or 'desc')

    Returns:
        Sorted list of results
    """
    if sort_by == "relevance":
        # Relevance typically defaults to descending (highest first)
        reverse = order != "asc"
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=reverse)
    elif sort_by == "price":
        # Price typically defaults to ascending (lowest first)
        reverse = order == "desc"
        return sorted(results, key=lambda x: x.get("price", 0), reverse=reverse)
    elif sort_by == "date":
        # Date typically defaults to descending (newest first)
        reverse = order != "asc"
        return sorted(results, key=lambda x: x.get("date", ""), reverse=reverse)
    elif sort_by == "rating":
        # Rating typically defaults to descending (highest first)
        reverse = order != "asc"
        return sorted(results, key=lambda x: x.get("rating", 0), reverse=reverse)
    elif sort_by == "name":
        # Name typically defaults to ascending (A-Z)
        reverse = order == "desc"
        return sorted(results, key=lambda x: x.get("name", "").lower(), reverse=reverse)
    else:
        return results


def generate_feedback(component: dict, success: bool, context: dict = None) -> str:
    """Generate feedback message for a component action.

    Args:
        component: The component that was invoked
        success: Whether the action succeeded
        context: Dictionary of values to substitute in template

    Returns:
        The formatted feedback message
    """
    feedback = component.get("feedback", {})
    context = context or {}

    if success:
        template = feedback.get("success_template", "Done")
    else:
        template = feedback.get("error_template", "An error occurred")

    # Simple template substitution
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{key}}}", str(value))

    return result


def main():
    """Demonstrate schema usage with search patterns."""
    schema = load_schema()
    print(f"Loaded schema: {schema['name']}")
    print(f"Components: {len(schema['components'])}")
    print()

    # Demo 1: Search with parameters
    print("=== Demo 1: Search with Parameters ===")
    search_component = find_component(schema, "search-items")
    if search_component:
        print(f"Component: {search_component['component_id']}")

        test_input = "search for laptops under $1000"
        if match_invocation(search_component, test_input):
            print(f"Matched input: '{test_input}'")

            params = extract_search_params(test_input)
            print(f"Extracted params: {params}")

            feedback = generate_feedback(
                search_component,
                success=True,
                context={"result_count": 42, "query": params.get("query", "")}
            )
            print(f"Feedback: {feedback}")
    print()

    # Demo 2: Pagination calculation
    print("=== Demo 2: Pagination ===")
    pagination = calculate_pagination(current_page=3, page_size=20, total_results=147)
    print(f"Page {pagination['current_page']} of {pagination['total_pages']}")
    print(f"Showing results {pagination['start_index'] + 1}-{pagination['end_index']}")
    print(f"Has previous: {pagination['has_previous']}")
    print(f"Has next: {pagination['has_next']}")
    print()

    # Demo 3: Sorting
    print("=== Demo 3: Sorting ===")
    mock_results = [
        {"name": "Item C", "price": 50, "rating": 4.5, "relevance_score": 0.8},
        {"name": "Item A", "price": 100, "rating": 4.0, "relevance_score": 0.9},
        {"name": "Item B", "price": 75, "rating": 5.0, "relevance_score": 0.7},
    ]

    print("Original order:")
    for item in mock_results:
        print(f"  {item['name']} - ${item['price']}")

    sorted_by_price = apply_sort(mock_results, "price", "asc")
    print("\nSorted by price (asc):")
    for item in sorted_by_price:
        print(f"  {item['name']} - ${item['price']}")

    sorted_by_rating = apply_sort(mock_results, "rating", "desc")
    print("\nSorted by rating (desc):")
    for item in sorted_by_rating:
        print(f"  {item['name']} - {item['rating']} stars")


if __name__ == "__main__":
    main()
