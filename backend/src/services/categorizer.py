"""Intelligent categorization engine for PhonePe transaction merchant names."""

import re
from typing import Dict, List

# Primary category keyword map
CATEGORY_MAP: Dict[str, List[str]] = {
    "Food": [
        "swiggy", "zomato", "canteen", "tea", "chai", "coffee", "restaurant",
        "cafe", "bakery", "mcdonald", "kfc", "dominos", "pizza", "burger",
        "dhaba", "barbeque", "instamart", "blinkit", "zepto", "food"
    ],
    "Travel": [
        "ola", "uber", "rapido", "metro", "petrol", "diesel", "fuel", "hpcl",
        "bpcl", "ioc", "irctc", "flight", "indigo", "airindia", "redbus",
        "toll", "fastag", "auto", "taxi", "bus", "train", "parking"
    ],
    "Shopping": [
        "dmart", "amazon", "flipkart", "flipcart", "myntra", "ajio", "zara",
        "h&m", "nykaa", "meesho", "supermarket", "mall", "clothing",
        "electronics", "croma", "reliance digital", "tata cliq", "shopping"
    ],
    "Bills": [
        "recharge", "electricity", "bescom", "tneb", "mseb", "wifi", "airtel",
        "jio", "vi", "bsnl", "broadband", "water", "gas", "cylinder",
        "indane", "hp gas", "bill", "piped gas", "maintenance", "rent"
    ],
    "Health": [
        "pharmacy", "medical", "apollo", "medplus", "1mg", "pharmeasy",
        "hospital", "clinic", "doctor", "lab", "gym", "cult.fit",
        "fitness", "diagnostics", "dental", "opticals"
    ],
    "Entertainment": [
        "netflix", "spotify", "youtube", "cinema", "movie", "bookmyshow",
        "pvr", "inox", "prime video", "hotstar", "disney", "gaming", "steam"
    ],
    "Education": [
        "coursera", "udemy", "school", "college", "tuition", "books",
        "stationery", "exam", "fees", "university"
    ],
    "Investment": [
        "zerodha", "groww", "upstox", "sip", "mutual fund", "gold", "stocks"
    ],
}


def get_category(merchant_name: str) -> str:
    """Classifies a merchant name into a primary spending category."""
    if not merchant_name:
        return "Other"

    clean_name = merchant_name.lower().strip()
    words = set(re.findall(r"\b\w+\b", clean_name))

    # Exact word match first
    for category, keywords in CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword in words or keyword in clean_name:
                return category

    return "Other"
