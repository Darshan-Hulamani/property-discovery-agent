from app.tools.data_loader import format_inr

def calculate_mortgage(
    property_price_inr: int,
    down_payment_percent: float = 20.0,
    interest_rate_percent: float = 8.5,
    loan_term_years: int = 20,
) -> dict:
    """Calculates monthly mortgage (EMI) based on standard Indian loan terms."""
    
    if down_payment_percent < 0 or down_payment_percent > 100:
        return {"error": "down_payment_percent must be between 0 and 100."}
        
    down_payment = property_price_inr * (down_payment_percent / 100.0)
    principal = property_price_inr - down_payment
    
    # EMI Formula: P x R x (1+R)^N / [(1+R)^N-1]
    # P = Principal
    # R = Monthly interest rate
    # N = Number of monthly installments
    
    monthly_rate = (interest_rate_percent / 100.0) / 12.0
    num_payments = loan_term_years * 12
    
    if monthly_rate > 0:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** num_payments) / (((1 + monthly_rate) ** num_payments) - 1)
    else:
        emi = principal / num_payments if num_payments > 0 else 0
        
    total_payment = emi * num_payments
    total_interest = total_payment - principal
    
    return {
        "property_price": format_inr(property_price_inr),
        "down_payment_percent": f"{down_payment_percent}%",
        "down_payment_amount": format_inr(int(down_payment)),
        "loan_amount": format_inr(int(principal)),
        "interest_rate": f"{interest_rate_percent}%",
        "loan_term": f"{loan_term_years} years",
        "monthly_emi": format_inr(int(emi)),
        "total_interest": format_inr(int(total_interest)),
        "total_payment": format_inr(int(total_payment)),
        "note": "This is an estimate. Actual bank EMI may vary slightly based on processing fees and reducing balance nuances."
    }
