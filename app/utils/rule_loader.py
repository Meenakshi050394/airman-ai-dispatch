import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.db_models import RuleDocument


# =====================================================
# Load rule from database
# =====================================================

def load_rule_from_db(db: Session, doc_name: str) -> str:

    rule = (
        db.query(RuleDocument)
        .filter_by(doc_name=doc_name)
        .first()
    )

    if not rule:
        raise ValueError(f"Rule document '{doc_name}' not found in database.")

    return rule.content


# =====================================================
# Load rule directly from file (fallback only)
# =====================================================

def load_rule_from_file(doc_name: str) -> str:

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, "data")
    path = os.path.join(data_dir, doc_name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Rule file '{doc_name}' not found.")

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


# =====================================================
# Unified rule loader
# =====================================================

def load_rule(db: Session, doc_name: str) -> str:

    try:
        return load_rule_from_db(db, doc_name)

    except ValueError:
        # Only fallback if rule not found in DB
        return load_rule_from_file(doc_name)

    except SQLAlchemyError:
        # If DB error, do NOT silently fallback
        raise
