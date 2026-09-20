"""
ComplyScan - Rule Engine

This file contains the 6 core compliance checks defined
for the hackathon prototype.

Each rule returns:
{
    "rule": "...",
    "status": "pass" or "fail",
    "detail": "..."
}

The main function check_compliance() runs all 6 rules.
"""

import re


# ============================================================
# HELPER FUNCTION
# ============================================================

def _get_text(item):
    """
    Extract text from either:

    1. A simple string:
       "MRP Rs. 120"

    2. A Textract-style dictionary:
       {"text": "MRP Rs. 120", "height": 18.5}

    This lets us test the rule engine manually now and
    connect it to Amazon Textract later.
    """
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        return str(item.get("text", ""))

    return ""


def _combined_text(text):
    """
    Combine all extracted text lines into one searchable string.
    """
    return " ".join(_get_text(item) for item in text)


# ============================================================
# RULE 1 - NET QUANTITY
# ============================================================

def check_net_quantity(text):
    """
    Rule:
    A number followed by a valid unit should be present.

    Examples:
        500 g
        1 kg
        250 ml
        1 L
        10 pcs
    """

    combined = _combined_text(text)

    # Accept integers and decimal quantities.
    # Also accept pcs because it is part of our hackathon rule.
    pattern = r"\b\d+(?:\.\d+)?\s*(?:g|kg|ml|l|pcs)\b"

    match = re.search(pattern, combined, re.IGNORECASE)

    if match:
        return {
            "rule": "Net Quantity",
            "status": "pass",
            "detail": f"Found quantity: {match.group(0)}"
        }

    return {
        "rule": "Net Quantity",
        "status": "fail",
        "detail": "No net quantity with g, kg, ml, l or pcs was found."
    }


# ============================================================
# RULE 2 - MRP
# ============================================================

def check_mrp(text):
    """
    Rule:
    Look for MRP or a currency symbol / Rs. followed by a number.

    Examples:
        MRP ₹120
        MRP: Rs. 120
        MRP 120
        ₹120
        Rs. 120
    """

    combined = _combined_text(text)

    # MRP followed by optional currency notation and a number.
    mrp_pattern = (
        r"\bMRP\b\s*[:\-]?\s*"
        r"(?:₹|Rs\.?|INR|\$|€|£)?\s*"
        r"\d+(?:\.\d{1,2})?"
    )

    # Direct currency + number.
    currency_pattern = (
        r"(?:₹|Rs\.?|INR|\$|€|£)\s*"
        r"\d+(?:\.\d{1,2})?"
    )

    match = re.search(
        rf"(?:{mrp_pattern})|(?:{currency_pattern})",
        combined,
        re.IGNORECASE
    )

    if match:
        return {
            "rule": "MRP",
            "status": "pass",
            "detail": f"Found price declaration: {match.group(0)}"
        }

    return {
        "rule": "MRP",
        "status": "fail",
        "detail": "No MRP or currency-price declaration was found."
    }


# ============================================================
# RULE 3 - MANUFACTURER / PACKER / IMPORTER
# ============================================================

def check_manufacturer_address(text):
    """
    Rule:
    Look for a manufacturer / packer / importer declaration
    together with address-like information.

    Examples:
        Mfd by ABC Foods Pvt Ltd
        Packed by XYZ Ltd
        Marketed by ABC Pvt Ltd
        Imported by ABC Imports

    An Indian-style PIN code or common address keyword is
    treated as evidence of an address block.
    """

    combined = _combined_text(text)

    # Common declaration phrases specified for this project.
    organisation_pattern = (
        r"\b(?:"
        r"mfd\.?\s*by|"
        r"manufactured\s*by|"
        r"packed\s*by|"
        r"marketed\s*by|"
        r"imported\s*by|"
        r"manufacturer|"
        r"packer|"
        r"importer"
        r")\b"
    )

    organisation_match = re.search(
        organisation_pattern,
        combined,
        re.IGNORECASE
    )

    # Indian PIN code = six digits.
    pin_pattern = r"\b\d{6}\b"

    # Common words that suggest an address.
    address_keyword_pattern = (
        r"\b(?:"
        r"road|rd\.?|"
        r"street|st\.?|"
        r"lane|"
        r"nagar|"
        r"sector|"
        r"phase|"
        r"industrial|"
        r"estate|"
        r"city|"
        r"district"
        r")\b"
    )

    pin_match = re.search(pin_pattern, combined)
    address_keyword_match = re.search(
        address_keyword_pattern,
        combined,
        re.IGNORECASE
    )

    if organisation_match and (pin_match or address_keyword_match):
        return {
            "rule": "Manufacturer / Packer / Importer",
            "status": "pass",
            "detail": (
                f"Found '{organisation_match.group(0)}' and "
                "address-like information."
            )
        }

    if organisation_match:
        return {
            "rule": "Manufacturer / Packer / Importer",
            "status": "fail",
            "detail": (
                f"Found '{organisation_match.group(0)}' but "
                "no clear address/PIN information was detected."
            )
        }

    return {
        "rule": "Manufacturer / Packer / Importer",
        "status": "fail",
        "detail": (
            "No manufacturer, packer or importer declaration "
            "was found."
        )
    }


# ============================================================
# RULE 4 - MONTH & YEAR OF MANUFACTURE
# ============================================================

def check_manufacture_date(text):
    """
    Rule:
    Look for a month/year manufacture or packing date.

    Examples:
        08/2026
        08-2026
        Mfg. Date: 08/2026
        Mfg Date: 08/2026
        Pkd Date: 08/2026
        Aug 2026
    """

    combined = _combined_text(text)

    # Numeric month/year:
    # 08/2026
    # 08-2026
    # 08.2026
    # 2026/08
    numeric_date = (
        r"(?:"
        r"\b(?:0?[1-9]|1[0-2])[-/.]\d{4}\b"
        r"|"
        r"\b\d{4}[-/.](?:0?[1-9]|1[0-2])\b"
        r")"
    )

    # Month written as text.
    month_date = (
        r"\b(?:"
        r"Jan(?:uary)?|"
        r"Feb(?:ruary)?|"
        r"Mar(?:ch)?|"
        r"Apr(?:il)?|"
        r"May|"
        r"Jun(?:e)?|"
        r"Jul(?:y)?|"
        r"Aug(?:ust)?|"
        r"Sep(?:tember)?|"
        r"Oct(?:ober)?|"
        r"Nov(?:ember)?|"
        r"Dec(?:ember)?"
        r")\s+\d{4}\b"
    )

    # Prefer dates that occur after manufacturing/packing labels.
    labelled_date = (
        r"\b(?:"
        r"mfg\.?\s*date|"
        r"mfg\s*date|"
        r"manufacturing\s*date|"
        r"manufactured\s*date|"
        r"pkd\.?\s*date|"
        r"pkd\s*date|"
        r"packing\s*date|"
        r"packed\s*date"
        r")\s*[:\-]?\s*"
        rf"(?:{numeric_date}|{month_date})"
    )

    match = re.search(
        labelled_date,
        combined,
        re.IGNORECASE
    )

    if not match:
        # Also accept a standalone month/year pattern because
        # Textract may separate the label from the date.
        match = re.search(
            rf"(?:{numeric_date}|{month_date})",
            combined,
            re.IGNORECASE
        )

    if match:
        return {
            "rule": "Month & Year of Manufacture",
            "status": "pass",
            "detail": f"Found manufacture/packing date: {match.group(0)}"
        }

    return {
        "rule": "Month & Year of Manufacture",
        "status": "fail",
        "detail": "No month/year manufacture date was found."
    }


# ============================================================
# RULE 5 - CONSUMER CARE DETAILS
# ============================================================

def check_consumer_care(text):
    """
    Rule:
    Look for:
        - phone number
        - email
        - 'Consumer Care'
        - 'Customer Care'

    The hackathon plan explicitly allows the words Consumer Care
    or Customer Care as a signal.
    """

    combined = _combined_text(text)

    # Email address.
    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    # A practical phone-number pattern that tolerates:
    # +91 9876543210
    # 1800-123-4567
    # 98765 43210
    phone_pattern = (
        r"(?:\+91[\s-]?)?"
        r"\b(?:\d[\s-]?){9,12}\b"
    )

    # Explicit care wording.
    care_pattern = (
        r"\b(?:"
        r"consumer\s+care|"
        r"customer\s+care"
        r")\b"
    )

    email_match = re.search(
        email_pattern,
        combined,
        re.IGNORECASE
    )

    if email_match:
        return {
            "rule": "Consumer Care Details",
            "status": "pass",
            "detail": f"Found email: {email_match.group(0)}"
        }

    phone_match = re.search(phone_pattern, combined)

    if phone_match:
        return {
            "rule": "Consumer Care Details",
            "status": "pass",
            "detail": f"Found phone number: {phone_match.group(0)}"
        }

    care_match = re.search(
        care_pattern,
        combined,
        re.IGNORECASE
    )

    if care_match:
        return {
            "rule": "Consumer Care Details",
            "status": "pass",
            "detail": f"Found label: {care_match.group(0)}"
        }

    return {
        "rule": "Consumer Care Details",
        "status": "fail",
        "detail": (
            "No phone number, email, Customer Care or "
            "Consumer Care was found."
        )
    }


# ============================================================
# RULE 6 - APPROXIMATE FONT SIZE / READABILITY
# ============================================================

def check_font_size(text, tolerance=0.30):
    """
    Rule:
    Compare text-height values supplied by OCR.

    Example input:
        [
            {"text": "MRP Rs. 120", "height": 20},
            {"text": "Net Qty 500 g", "height": 19},
            {"text": "Consumer Care", "height": 18}
        ]

    We use the smallest and largest supplied heights.

    If the variation is <= 30%, we consider the text heights
    approximately consistent.

    If height information is not supplied, the rule cannot be
    meaningfully checked, so it fails with an explanatory detail.
    """

    heights = []

    for item in text:
        if isinstance(item, dict):
            height = item.get("height")

            if isinstance(height, (int, float)) and height > 0:
                heights.append(float(height))

    if len(heights) < 2:
        return {
            "rule": "Font Size / Readability",
            "status": "fail",
            "detail": (
                "Not enough text-height values were provided "
                "for an approximate font-size check."
            )
        }

    minimum = min(heights)
    maximum = max(heights)

    variation = (maximum - minimum) / minimum

    if variation <= tolerance:
        return {
            "rule": "Font Size / Readability",
            "status": "pass",
            "detail": (
                f"Text heights are approximately consistent. "
                f"Min={minimum:.1f}, Max={maximum:.1f}, "
                f"Variation={variation * 100:.1f}%."
            )
        }

    return {
        "rule": "Font Size / Readability",
        "status": "fail",
        "detail": (
            f"Text heights vary noticeably. "
            f"Min={minimum:.1f}, Max={maximum:.1f}, "
            f"Variation={variation * 100:.1f}%."
        )
    }


# ============================================================
# MAIN COMPLIANCE FUNCTION
# ============================================================

def check_compliance(text):
    """
    Run all six rules and calculate the overall result.

    Returns:

    {
        "overall_status": "pass" or "fail",
        "rule_results": [
            {
                "rule": "...",
                "status": "pass/fail",
                "detail": "..."
            },
            ...
        ]
    }
    """

    results = [
        check_net_quantity(text),
        check_mrp(text),
        check_manufacturer_address(text),
        check_manufacture_date(text),
        check_consumer_care(text),
        check_font_size(text),
    ]

    # Overall result passes only when all six rules pass.
    overall_status = (
        "pass"
        if all(result["status"] == "pass" for result in results)
        else "fail"
    )

    return {
        "overall_status": overall_status,
        "rule_results": results
    }


# ============================================================
# SIMPLE LOCAL TEST
# ============================================================

if __name__ == "__main__":

    # Sample label that should pass all six rules.
    sample_text = [
        {"text": "ABC Foods Pvt Ltd", "height": 20},
        {"text": "Mfd by ABC Foods Pvt Ltd", "height": 20},
        {"text": "123 Industrial Road, Delhi 110001", "height": 19},
        {"text": "Net Quantity: 500 g", "height": 20},
        {"text": "MRP: Rs. 120", "height": 20},
        {"text": "Mfg. Date: 08/2026", "height": 19},
        {"text": "Consumer Care: 1800-123-4567", "height": 20},
        {"text": "care@example.com", "height": 19},
    ]

    result = check_compliance(sample_text)

    print("\n===== COMPLISCAN RESULT =====")
    print("Overall:", result["overall_status"])

    for rule in result["rule_results"]:
        print(
            f"{rule['rule']}: "
            f"{rule['status']} -> "
            f"{rule['detail']}"
        )