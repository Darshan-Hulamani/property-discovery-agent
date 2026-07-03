from google.genai import types

from app.tools.commute import estimate_commute
from app.tools.compare import compare_properties
from app.tools.neighbourhood import get_neighbourhood_profile
from app.tools.property_details import get_property_details
from app.tools.search_listings import search_properties
from app.tools.mortgage_calculator import calculate_mortgage
from app.tools.profile_memory import update_buyer_profile

TOOL_FUNCTIONS = {
    "search_properties": search_properties,
    "get_property_details": get_property_details,
    "estimate_commute": estimate_commute,
    "get_neighbourhood_profile": get_neighbourhood_profile,
    "compare_properties": compare_properties,
    "calculate_mortgage": calculate_mortgage,
    "update_buyer_profile": update_buyer_profile,
}

FUNCTION_DECLARATIONS = [
    types.FunctionDeclaration(
        name="search_properties",
        description="Search and rank curated Indian property listings by city, budget, BHK, locality, type, and semantic preference tags. Returns explainable scores and score reasons.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "city": types.Schema(type=types.Type.STRING, description="City name e.g. Bangalore, Mumbai"),
                "max_budget_inr": types.Schema(type=types.Type.INTEGER, description="Maximum budget in INR"),
                "min_bhk": types.Schema(type=types.Type.INTEGER, description="Minimum BHK count"),
                "locality": types.Schema(type=types.Type.STRING, description="Locality or area name"),
                "property_type": types.Schema(type=types.Type.STRING, description="apartment or villa"),
                "possession": types.Schema(type=types.Type.STRING, description="Possession preference e.g. Ready to move or Under construction"),
                "must_have_tags": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="Required or preferred tags e.g. metro_nearby, gated, schools_nearby, it_hub_nearby, budget_friendly, premium",
                ),
                "limit": types.Schema(type=types.Type.INTEGER, description="Max results, default 10"),
            },
        ),
    ),
    types.FunctionDeclaration(
        name="get_property_details",
        description="Get full details for one property by its ID.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "property_id": types.Schema(type=types.Type.STRING, description="Property ID e.g. blr-001"),
            },
            required=["property_id"],
        ),
    ),
    types.FunctionDeclaration(
        name="estimate_commute",
        description="Estimate live driving commute from a property or locality to a workplace/landmark.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "destination": types.Schema(type=types.Type.STRING, description="Workplace or landmark e.g. Electronic City Bangalore"),
                "property_id": types.Schema(type=types.Type.STRING, description="Origin property ID"),
                "origin_locality": types.Schema(type=types.Type.STRING, description="Origin locality if no property_id"),
                "origin_city": types.Schema(type=types.Type.STRING, description="Origin city if no property_id"),
            },
            required=["destination"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_neighbourhood_profile",
        description="Get school scores, safety, metro distance, and amenities for a locality.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "city": types.Schema(type=types.Type.STRING),
                "locality": types.Schema(type=types.Type.STRING),
            },
            required=["city", "locality"],
        ),
    ),
    types.FunctionDeclaration(
        name="compare_properties",
        description="Compare 2-5 properties side by side on price, schools, safety, metro, etc.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "property_ids": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="List of property IDs to compare",
                ),
                "criteria": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="Buyer priorities e.g. budget, commute, schools",
                ),
            },
            required=["property_ids"],
        ),
    ),
    types.FunctionDeclaration(
        name="calculate_mortgage",
        description="Calculate estimated monthly mortgage payments (EMI) for a property.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "property_price_inr": types.Schema(type=types.Type.INTEGER, description="Total property price in INR"),
                "down_payment_percent": types.Schema(type=types.Type.NUMBER, description="Down payment percentage (e.g., 20.0)"),
                "interest_rate_percent": types.Schema(type=types.Type.NUMBER, description="Annual interest rate (e.g., 8.5)"),
                "loan_term_years": types.Schema(type=types.Type.INTEGER, description="Loan term in years (e.g., 20)"),
            },
            required=["property_price_inr"],
        ),
    ),
    types.FunctionDeclaration(
        name="update_buyer_profile",
        description="Update the persistent buyer profile. Call this whenever the user states their preferences (budget, bhk, city, locality, landmark, must-have features). Do NOT ask the user for confirmation before calling this.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "city": types.Schema(type=types.Type.STRING, description="City name"),
                "max_budget_inr": types.Schema(type=types.Type.INTEGER, description="Max budget in INR"),
                "min_bhk": types.Schema(type=types.Type.INTEGER, description="Min BHK required"),
                "locality": types.Schema(type=types.Type.STRING, description="Preferred locality"),
                "office_landmark": types.Schema(type=types.Type.STRING, description="Office address or landmark for commute"),
                "must_have_tags": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="Must-have property tags (e.g. gated, metro_nearby)",
                ),
            },
        ),
    ),
]

GEMINI_TOOLS = [types.Tool(function_declarations=FUNCTION_DECLARATIONS)]


def execute_tool(name: str, args: dict) -> tuple[dict, str]:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        result = {"error": f"Unknown tool: {name}"}
        return result, str(result)

    try:
        result = fn(**args)
    except TypeError as exc:
        result = {"error": f"Invalid arguments for {name}: {exc}"}
    except Exception as exc:
        result = {"error": f"Tool {name} failed: {exc}"}

    summary = _summarize_result(name, result)
    return result, summary


def _summarize_result(name: str, result: dict) -> str:
    if "error" in result:
        return f"{name}: {result['error']}"
    if name == "search_properties":
        return f"{name}: ranked {result.get('count', 0)} properties"
    if name == "estimate_commute":
        return f"{name}: {result.get('duration_minutes')} min, {result.get('distance_km')} km"
    if name == "compare_properties":
        return f"{name}: compared {len(result.get('properties', []))} properties"
    if name == "calculate_mortgage":
        return f"{name}: EMI {result.get('monthly_emi')} for {result.get('loan_term')}"
    if name == "update_buyer_profile":
        return f"{name}: updated profile"
    return f"{name}: ok"
