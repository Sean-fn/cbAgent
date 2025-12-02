"""
Query Templates - Pre-defined prompts for different query types
"""

from typing import Dict


def get_query_template(query_type: str, component_name: str, repo_path: str) -> str:
    """
    Get the query template for a specific query type

    Args:
        query_type: Type of query (usage, restrictions, dependencies, business_rules)
        component_name: Name of the component to analyze
        repo_path: Path to the repository

    Returns:
        Formatted query template
    """
    templates: Dict[str, str] = {
        "usage": USAGE_TEMPLATE,
        "restrictions": RESTRICTIONS_TEMPLATE,
        "dependencies": DEPENDENCIES_TEMPLATE,
        "business_rules": BUSINESS_RULES_TEMPLATE
    }

    template = templates.get(query_type, USAGE_TEMPLATE)
    return template.format(component_name=component_name, repo_path=repo_path)


# Template for usage queries
USAGE_TEMPLATE = """Analyze the {component_name} component in the repository at {repo_path}.

Find and provide:
1. File location where {component_name} is defined
2. How to import and use {component_name}
3. What parameters, props, or configuration it accepts
4. Actual code examples from the repository showing {component_name} in use
5. Common usage patterns and best practices
6. Integration steps for adding {component_name} to a new feature

Search in:
- Component definition files
- Test files (for usage examples)
- Documentation files
- Example/demo files
- Other components that use {component_name}

Be thorough and include specific code examples."""

# Template for restrictions queries
RESTRICTIONS_TEMPLATE = """Analyze restrictions and constraints for the {component_name} component in {repo_path}.

Find and provide:
1. Input validation rules (type checking, prop validation, schema validation)
2. Documented limitations in comments, JSDoc, or documentation
3. Error handling and edge cases
4. What {component_name} CANNOT do or handle
5. Technical constraints (browser compatibility, performance limits, etc.)
6. Required conditions or prerequisites
7. Warnings or deprecated features

Search in:
- Component implementation code
- Validation logic
- Error handling code
- Comments and documentation
- Test files (especially error case tests)

Focus on identifying what users should avoid and what won't work."""

# Template for dependencies queries
DEPENDENCIES_TEMPLATE = """Analyze dependencies for the {component_name} component in {repo_path}.

Find and provide:
1. All import statements in the component file
2. External packages required (from package.json, requirements.txt, etc.)
3. Internal dependencies (other components, utilities, services it uses)
4. Peer dependencies required by the component
5. Optional dependencies
6. System requirements or environment dependencies
7. Version constraints or compatibility requirements

Search in:
- Component source file
- Package manifest files (package.json, etc.)
- Import/require statements
- Dependency injection configurations
- Build configuration files

List all dependencies clearly with their purpose."""

# Template for business rules queries
BUSINESS_RULES_TEMPLATE = """Analyze business logic and rules implemented in the {component_name} component in {repo_path}.

Find and provide:
1. Validation logic that enforces business rules (e.g., "amount must be positive")
2. Workflow steps or state transitions
3. Business constraints mentioned in comments or code
4. Conditional logic based on business requirements
5. Data transformation rules
6. Access control or permission rules
7. Business-specific calculations or formulas
8. Compliance or regulatory requirements

Search in:
- Validation functions
- Conditional statements with business logic
- Comments explaining business requirements
- State management code
- Event handlers with business logic
- Configuration files with business rules

Focus on identifying WHY the code does what it does from a business perspective."""


def get_query_description(query_type: str) -> str:
    """Get a human-readable description of what each query type finds"""
    descriptions = {
        "usage": "Find examples, parameters, and integration steps",
        "restrictions": "Identify limitations, constraints, and edge cases",
        "dependencies": "List required packages and related components",
        "business_rules": "Explain validation logic and business workflows"
    }
    return descriptions.get(query_type, "General component analysis")
