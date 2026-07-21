import re
from typing import Tuple

CATEGORY_RULES = {
    "GST": [
        "gst", "gstin", "gstr", "goods and services tax", "input tax credit",
        "itc", "sgst", "cgst", "igst", "e-invoice", "e-way bill", "hsn",
        "composition scheme", "reverse charge", "gst registration"
    ],
    "Income Tax": [
        "income tax", "itr", "assessment year", "previous year", "deduction",
        "exemption", "section 80", "section 10", "advance tax", "self assessment",
        "tds certificate", "form 26as", "capital gains", "house property",
        "salary income", "rebate", "surcharge", "cess", "new tax regime",
        "old tax regime", "section 115bac"
    ],
    "TDS": [
        "tds", "tax deducted at source", "section 194", "section 192",
        "section 193", "form 16", "form 16a", "tds return", "tan",
        "tds deduction", "tcs", "tax collected at source"
    ],
    "EPF": [
        "epf", "provident fund", "pf", "epfo", "employee provident",
        "uan", "universal account number", "pf withdrawal", "pf transfer",
        "pf contribution", "employees provident fund"
    ],
    "ESI": [
        "esi", "esic", "employee state insurance", "esi contribution",
        "esi registration", "esi return"
    ],
    "Professional Tax": [
        "professional tax", "pt", "profession tax", "state tax"
    ],
    "Company Law": [
        "mca", "roc", "companies act", "director", "incorporation",
        "annual return", "form aoc", "form mgт", "registered office",
        "memorandum", "articles of association"
    ],
    "Customs": [
        "customs", "import duty", "export duty", "cbic", "customs act",
        "bill of entry", "shipping bill", "customs tariff"
    ]
}

SUBCATEGORY_RULES = {
    "GST": {
        "Returns": ["gstr-1", "gstr-3b", "gstr-9", "gstr-2b", "return filing", "due date"],
        "Registration": ["registration", "gstin", "new registration", "cancellation"],
        "Rates": ["rate", "hsn", "sac", "tax rate", "nil rated", "exempt"],
        "ITC": ["input tax credit", "itc", "credit", "blocked credit"],
        "E-Invoice": ["e-invoice", "irn", "einvoice"],
    },
    "Income Tax": {
        "Deductions": ["deduction", "section 80c", "section 80d", "chapter vi"],
        "Returns": ["itr", "return filing", "due date", "form"],
        "TDS": ["tds", "tax deducted", "form 16", "194"],
        "Capital Gains": ["capital gain", "ltcg", "stcg", "section 54"],
        "Slabs": ["slab", "rate", "tax rate", "percentage"],
    },
    "TDS": {
        "Salary": ["salary", "section 192", "form 16"],
        "Rent": ["rent", "section 194i"],
        "Professional": ["professional", "section 194j", "consultant"],
        "Interest": ["interest", "section 194a", "bank"],
        "Contractor": ["contractor", "section 194c"],
    }
}

def detect_category(text: str) -> Tuple[str, str]:
    """
    Detect category and subcategory from text.
    Returns: (category, subcategory)
    """
    text_lower = text.lower()
    
    category_scores = {}
    for category, keywords in CATEGORY_RULES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return "General", "General"

    category = max(category_scores, key=category_scores.get)

    subcategory = "General"
    if category in SUBCATEGORY_RULES:
        sub_scores = {}
        for sub, keywords in SUBCATEGORY_RULES[category].items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                sub_scores[sub] = score
        if sub_scores:
            subcategory = max(sub_scores, key=sub_scores.get)

    return category, subcategory

def detect_financial_year(text: str) -> str:
    """Extract financial year from text."""
    patterns = [
        r'F\.?Y\.?\s*(\d{4}[-–]\d{2,4})',
        r'financial year\s*(\d{4}[-–]\d{2,4})',
        r'assessment year\s*(\d{4}[-–]\d{2,4})',
        r'A\.?Y\.?\s*(\d{4}[-–]\d{2,4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "General"

def detect_credibility(source_url: str) -> float:
    """Score source credibility based on URL."""
    official_sources = [
        "incometax.gov.in", "incometaxindia.gov.in",
        "gst.gov.in", "cbic.gov.in",
        "epfindia.gov.in", "esic.gov.in",
        "mca.gov.in", "icai.org",
        "tgct.gov.in", "finmin.nic.in"
    ]
    trusted_sources = [
        "caclubindia.com", "taxmann.com",
        "cleartax.in", "indiafilings.com"
    ]

    for source in official_sources:
        if source in source_url:
            return 1.0

    for source in trusted_sources:
        if source in source_url:
            return 0.8

    if source_url.startswith("pdf://"):
        return 0.9

    return 0.7