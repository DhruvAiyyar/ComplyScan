"""
ComplyScan - Database Models

This file defines the 3 database tables used by the project:

1. products
2. scans
3. rule_results
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


# Base class for all SQLAlchemy models.
Base = declarative_base()


# ============================================================
# PRODUCTS TABLE
# ============================================================

class Product(Base):
    """
    Stores information about a packaged product.
    """

    __tablename__ = "products"

    # Unique ID for every product.
    id = Column(Integer, primary_key=True, index=True)

    # URL/path of the uploaded product label image.
    image = Column(String(500), nullable=True)

    # Time when the product was uploaded.
    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One product can have multiple scans.
    scans = relationship(
        "Scan",
        back_populates="product"
    )


# ============================================================
# SCANS TABLE
# ============================================================

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    # Raw OCR text from the label.
    extracted_text = Column(
        Text,
        nullable=True
    )

    overall_status = Column(
        String(20),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="scans"
    )

    rule_results = relationship(
        "RuleResult",
        back_populates="scan",
        cascade="all, delete-orphan"
    )

# ============================================================
# RULE RESULTS TABLE
# ============================================================

class RuleResult(Base):
    """
    Stores the result of each individual compliance rule.

    Example:
        rule_name = "MRP"
        status = "pass"
        detail = "Found price declaration: MRP Rs. 120"
    """

    __tablename__ = "rule_results"

    # Unique ID for every rule result.
    id = Column(Integer, primary_key=True, index=True)

    # Connect this result to a scan.
    scan_id = Column(
        Integer,
        ForeignKey("scans.id"),
        nullable=False
    )

    # Name of the rule.
    rule_name = Column(
        String(100),
        nullable=False
    )

    # Rule result: "pass" or "fail".
    status = Column(
        String(20),
        nullable=False
    )

    # Explanation of why the rule passed or failed.
    detail = Column(
        Text,
        nullable=True
    )

    # Relationship back to Scan.
    scan = relationship(
        "Scan",
        back_populates="rule_results"
    )  