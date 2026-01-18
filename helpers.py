# Helper functions for Bootstrap Budget Tracker
# ROI calculations, budget alerts, and data processing

def calculate_roi(total_conversions, total_spend, avg_conversion_value=50):
    """
    Calculate Return on Investment (ROI) for a campaign
    
    Args:
        total_conversions: Number of conversions
        total_spend: Amount spent on campaign
        avg_conversion_value: Average value of each conversion (default $50)
    
    Returns:
        ROI as a percentage
    """
    if total_spend == 0:
        return 0
    
    revenue = total_conversions * avg_conversion_value
    roi = ((revenue - total_spend) / total_spend) * 100
    return round(roi, 2)


def calculate_budget_usage(budget, total_spend):
    """
    Calculate what percentage of budget has been used
    
    Args:
        budget: Total campaign budget
        total_spend: Amount spent so far
    
    Returns:
        Percentage of budget used
    """
    if budget == 0:
        return 0
    
    usage = (total_spend / budget) * 100
    return round(usage, 2)


def check_budget_alert(budget, total_spend, threshold=80):
    """
    Check if budget usage has reached alert threshold
    
    Args:
        budget: Total campaign budget
        total_spend: Amount spent so far
        threshold: Alert threshold percentage (default 80%)
    
    Returns:
        True if alert should be shown, False otherwise
    """
    usage = calculate_budget_usage(budget, total_spend)
    return usage >= threshold


def calculate_ctr(clicks, impressions):
    """
    Calculate Click-Through Rate (CTR)
    
    Args:
        clicks: Number of clicks
        impressions: Number of impressions
    
    Returns:
        CTR as a percentage
    """
    if impressions == 0:
        return 0
    
    ctr = (clicks / impressions) * 100
    return round(ctr, 2)


def calculate_conversion_rate(conversions, clicks):
    """
    Calculate Conversion Rate
    
    Args:
        conversions: Number of conversions
        clicks: Number of clicks
    
    Returns:
        Conversion rate as a percentage
    """
    if clicks == 0:
        return 0
    
    rate = (conversions / clicks) * 100
    return round(rate, 2)


def validate_date_range(start_date, end_date):
    """
    Validate that end date is after start date
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
    
    Returns:
        True if valid, False otherwise
    """
    from datetime import datetime
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return end >= start
    except ValueError:
        return False


def validate_budget(budget):
    """
    Validate budget is a positive number
    
    Args:
        budget: Budget amount (string or number)
    
    Returns:
        True if valid, False otherwise
    """
    try:
        budget_float = float(budget)
        return budget_float > 0
    except (ValueError, TypeError):
        return False
