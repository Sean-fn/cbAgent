"""
Query Parser - Detects query type and extracts component name from natural language
"""

import re
from typing import Tuple, Optional
from enum import Enum


class QueryType(Enum):
    """Supported query types"""
    USAGE = "usage"
    RESTRICTIONS = "restrictions"
    DEPENDENCIES = "dependencies"
    BUSINESS_RULES = "business_rules"
    UNKNOWN = "unknown"


class QueryParser:
    """
    Parses natural language queries to extract:
    - Component name
    - Query type (usage, restrictions, dependencies, business rules)
    """

    # Keywords for each query type
    USAGE_KEYWORDS = [
        "how to use", "how do i use", "how can i use",
        "example", "usage", "implement", "integrate",
        "add", "include", "setup", "configure"
    ]

    RESTRICTION_KEYWORDS = [
        "limitation", "constraint", "restriction",
        "can't", "cannot", "can not", "doesn't",
        "requirement", "limit", "allowed",
        "prohibited", "prevent", "avoid"
    ]

    DEPENDENCY_KEYWORDS = [
        "depend", "require", "need", "import",
        "prerequisite", "must have", "relies on"
    ]

    BUSINESS_RULE_KEYWORDS = [
        "business rule", "business logic",
        "validation", "validate", "rule",
        "allowed", "permitted", "workflow",
        "process", "policy"
    ]

    def parse(self, query: str) -> Tuple[Optional[str], QueryType]:
        """
        Parse a natural language query

        Args:
            query: User's natural language question

        Returns:
            Tuple of (component_name, query_type)
        """
        query_lower = query.lower()

        # Detect query type
        query_type = self._detect_query_type(query_lower)

        # Extract component name
        component_name = self._extract_component_name(query)

        return component_name, query_type

    def _detect_query_type(self, query: str) -> QueryType:
        """Detect the type of query based on keywords"""
        # Check each category
        if any(keyword in query for keyword in self.USAGE_KEYWORDS):
            return QueryType.USAGE

        if any(keyword in query for keyword in self.RESTRICTION_KEYWORDS):
            return QueryType.RESTRICTIONS

        if any(keyword in query for keyword in self.DEPENDENCY_KEYWORDS):
            return QueryType.DEPENDENCIES

        if any(keyword in query for keyword in self.BUSINESS_RULE_KEYWORDS):
            return QueryType.BUSINESS_RULES

        # Default to usage if unclear
        return QueryType.USAGE

    def _extract_component_name(self, query: str) -> Optional[str]:
        """
        Extract component name from query

        Looks for:
        - Capitalized words (e.g., PaymentButton, UserProfile)
        - Quoted strings
        - Words after "the" or "for"
        """
        # Try to find quoted component names first
        quoted_match = re.search(r'["\']([A-Z][a-zA-Z0-9_]*)["\']', query)
        if quoted_match:
            return quoted_match.group(1)

        # Look for patterns like "the ComponentName" or "for ComponentName" first
        # This helps avoid matching sentence-starting words
        pattern_match = re.search(r'(?:the|for|about|of|use|using)\s+([A-Z][a-zA-Z0-9_]+)', query)
        if pattern_match:
            return pattern_match.group(1)

        # Look for PascalCase component names (must have multiple capital letters or be long)
        # Avoid single-word sentence starters like "How", "What", etc.
        pascal_case_matches = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', query)
        if pascal_case_matches:
            # Return the longest match to avoid short words
            return max(pascal_case_matches, key=len)

        # Look for any capitalized word that might be a component (but not at sentence start)
        # Match words that appear after lowercase words
        word_match = re.search(r'[a-z]\s+([A-Z][a-zA-Z0-9_]{2,})\b', query)
        if word_match:
            return word_match.group(1)

        # Try to extract from common phrases (case insensitive)
        phrases = [
            r'(?:use|using)\s+(?:the\s+)?([a-zA-Z][a-zA-Z0-9_]+)',
            r'(?:about|regarding)\s+(?:the\s+)?([a-zA-Z][a-zA-Z0-9_]+)',
            r'([a-zA-Z][a-zA-Z0-9_]+)\s+component',
            r'([a-zA-Z][a-zA-Z0-9_]+)\s+feature'
        ]

        for pattern in phrases:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                component = match.group(1)
                # Capitalize first letter
                return component[0].upper() + component[1:]

        return None

    def get_suggestions(self, query: str, available_components: list) -> list:
        """
        Suggest components based on fuzzy matching

        Args:
            query: User's query
            available_components: List of available component names

        Returns:
            List of suggested component names
        """
        query_lower = query.lower()
        suggestions = []

        for component in available_components:
            component_lower = component.lower()

            # Exact match
            if component_lower in query_lower:
                suggestions.append(component)
            # Partial match
            elif any(part in query_lower for part in component_lower.split('_')):
                suggestions.append(component)

        return suggestions[:5]  # Return top 5 suggestions
