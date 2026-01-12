# {{PROJECT_NAME_TITLE}} - Search Template

This template demonstrates search and discovery LUI (Language User Interface) patterns using BAML.

## What You'll Learn

1. **Search Patterns** - Full-text search with query parameters
2. **Faceted Filtering** - Multi-dimensional result refinement
3. **Sorting & Ranking** - Relevance scoring and custom sort orders
4. **Pagination** - Handling large result sets efficiently
5. **Result Navigation** - Drilling down from search results to details

## When to Use This Template

Use the search template when your application includes:
- **Product Catalogs** - E-commerce, marketplaces, inventory systems
- **Content Discovery** - Articles, documents, media libraries
- **Data Exploration** - Analytics dashboards, reporting tools
- **Directory Services** - User directories, company listings
- **Any searchable collection** - When users need to find items in large datasets

## Quick Start

```bash
# Load the schema
python integration.py

# Run tests
pytest test_integration.py -v
```

## Schema Structure

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| `search-items` | QUERY | Execute searches with query, filters, pagination |
| `filter-results` | ACTION | Apply faceted filters to narrow results |
| `sort-results` | ACTION | Sort by relevance, price, date, rating |
| `paginate` | ACTION | Navigate through result pages |
| `view-details` | QUERY | View detailed info for a specific item |

## Key Concepts

### 1. Full-Text Search
The `search-items` component demonstrates how to handle natural language search queries:
- **Query text**: The main search term(s)
- **Filters**: Category, price range, availability
- **Pagination**: Page number and page size
- **Example**: "Search for wireless keyboards under $50 in electronics"

### 2. Faceted Filtering
Faceted search lets users refine results by multiple dimensions simultaneously:
```json
{
  "category": "electronics",
  "price_range": "$50-$200",
  "availability": true,
  "rating": 4.0
}
```

This is more user-friendly than complex boolean queries.

### 3. Relevance Scoring
Search results should be ranked by relevance to the query. Common factors:
- **Text match quality**: Exact matches rank higher than partial matches
- **Field weighting**: Matches in titles rank higher than descriptions
- **Recency**: Newer items may rank higher (time-decay)
- **Popularity**: Click-through rate, sales volume, ratings
- **Personalization**: User preferences and history

### 4. Sorting Options
Beyond relevance, users often want to sort by:
- **Price**: Low to high, high to low
- **Date**: Newest first, oldest first
- **Rating**: Highest rated first
- **Name**: Alphabetical order

The `sort-results` component handles this with `sort_by` and `order` parameters.

### 5. Pagination Strategies
For large result sets, pagination is essential:
- **Offset-based**: Traditional page numbers (page 1, 2, 3...)
- **Cursor-based**: More efficient for real-time data
- **Infinite scroll**: Load more results as user scrolls

This template demonstrates offset-based pagination (most common for search).

## Pattern Examples

### Basic Search
```
User: "Search for laptops"
→ Extracts: { query: "laptops" }
→ Returns: Relevant laptop results, sorted by relevance
```

### Search with Filters
```
User: "Find wireless mice under $30"
→ Extracts: {
    query: "wireless mice",
    max_price: 30
  }
→ Returns: Filtered results
```

### Multi-Step Refinement
```
1. User: "Search for headphones"
   → Shows all headphone results

2. User: "Filter by price range $50-$100"
   → Narrows to 50-100 price range

3. User: "Sort by rating"
   → Reorders by highest rating first
```

### Pagination Flow
```
User: "Search for keyboards"
→ Shows page 1 (results 1-20)

User: "Next page"
→ Shows page 2 (results 21-40)

User: "Go to page 5"
→ Shows page 5 (results 81-100)
```

## Customization Guide

### 1. Add Domain-Specific Filters
Extend the `filter-results` component with filters specific to your domain:

```json
{
  "name": "brand",
  "type": "string",
  "description": "Filter by brand name"
},
{
  "name": "condition",
  "type": "string",
  "description": "Filter by condition: new, used, refurbished"
}
```

### 2. Customize Sort Options
Add domain-specific sorting criteria:

```json
{
  "name": "sort_by",
  "type": "string",
  "description": "Sort by: relevance, price, date, rating, popularity, distance"
}
```

### 3. Add Saved Searches
Create a component for saving and retrieving search queries:

```json
{
  "component_id": "save-search",
  "component_type": "ACTION",
  "intent": "Save current search for future use"
}
```

### 4. Implement Search Suggestions
Add auto-complete or "did you mean" functionality:

```json
{
  "component_id": "suggest",
  "component_type": "QUERY",
  "intent": "Get search suggestions as user types"
}
```

## Implementation Tips

### Relevance Scoring
Consider using:
- **Elasticsearch**: Built-in BM25 scoring algorithm
- **PostgreSQL**: Full-text search with `ts_rank`
- **Vector search**: Embedding-based semantic search
- **Hybrid approach**: Combine keyword and semantic search

### Performance Optimization
- **Index your search fields**: Critical for speed
- **Cache popular queries**: Redis or CDN caching
- **Limit page size**: 20-50 results is typical
- **Use aggregations**: Pre-compute filter counts
- **Implement rate limiting**: Prevent search abuse

### User Experience
- **Show result count**: "Found 147 items matching 'laptop'"
- **Highlight query terms**: Bold matching text in results
- **Preserve context**: Remember filters when paginating
- **Provide feedback**: "No results found" with suggestions
- **Enable refinement**: Easy to adjust filters/sorting

## Testing Strategy

The test suite demonstrates:
1. **Schema loading**: Verify schema is valid
2. **Component matching**: Test invocation pattern recognition
3. **Parameter extraction**: Validate filter/pagination parsing
4. **Pagination math**: Test page calculations
5. **Sort validation**: Verify sort order handling

## Files

- `schema.json` - The LUI schema definition
- `integration.py` - Python code demonstrating search patterns
- `test_integration.py` - Tests showing expected behavior
- `README.md` - This file

## Next Steps

1. Customize filters and sort options for your domain
2. Implement relevance scoring algorithm
3. Add search analytics (popular queries, zero-result searches)
4. Test with the LUI simulator
5. Export to OpenAPI or MCP format

## Real-World Examples

- **E-commerce**: Amazon-style product search with filters
- **Job boards**: Search jobs by location, salary, skills
- **Real estate**: Search properties by price, bedrooms, location
- **Documentation**: Search help articles and guides
- **Media libraries**: Search photos, videos, music by metadata

Generated on: {{CREATED_DATE}}
