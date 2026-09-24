"""Cleaning and feature creation for Home Credit application data.

The transformations in this module mirror the explicit treatments and derived
fields in ``notebooks/01_eda.qmd`` (Q5, Q7, Q9, Q10, Q14, and Q16). The EDA did
not approve imputation, outlier capping, rare-category grouping, or redundant
feature removal, so none of those operations happen here.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


DAYS_PER_YEAR = 365.25
EMPLOYMENT_SENTINEL = 365243

RATIO_FEATURES = (
    "_ANNUAL_PAYMENT_TO_INCOME",
    "_PAYMENT_TO_INCOME_UNANNUALIZED",
    "_CREDIT_TO_INCOME",
    "_CREDIT_TO_GOODS",
)

TENURE_FEATURES = (
    "_AGE_YEARS",
    "_EMPLOYED_YEARS",
    "_REGISTRATION_YEARS",
    "_ID_PUBLISH_YEARS",
)

AUDIT_ONLY_COLUMNS = (
    "CODE_GENDER",
    "DAYS_BIRTH",
    "NAME_FAMILY_STATUS",
    "_AGE_YEARS",
    "_AGE_BAND",
)

_CLEANING_COLUMNS = ("DAYS_EMPLOYED", "ORGANIZATION_TYPE")
_FEATURE_COLUMNS = (
    "AMT_INCOME_TOTAL",
    "AMT_ANNUITY",
    "AMT_CREDIT",
    "AMT_GOODS_PRICE",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
)
_EXTERNAL_SOURCE_COLUMNS = ("EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3")


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], operation: str) -> None:
    missing = sorted(set(columns).difference(frame.columns))
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Cannot {operation}; missing required columns: {joined}")


def _require_numeric(frame: pd.DataFrame, columns: Iterable[str], operation: str) -> None:
    nonnumeric = sorted(column for column in columns if not is_numeric_dtype(frame[column]))
    if nonnumeric:
        joined = ", ".join(nonnumeric)
        raise TypeError(f"Cannot {operation}; expected numeric columns: {joined}")


def _safe_ratio(
    numerator: pd.Series,
    denominator: pd.Series,
    valid: pd.Series,
) -> pd.Series:
    result = pd.Series(np.nan, index=numerator.index, dtype="float64")
    result.loc[valid] = numerator.loc[valid] / denominator.loc[valid]
    return result


def clean_application_data(
    frame: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Apply the EDA-approved sentinel and unavailable-category treatments.

    ``DAYS_EMPLOYED = 365243`` becomes missing and is retained in the boolean
    ``_EMPLOYED_SENTINEL`` feature. ``ORGANIZATION_TYPE = XNA`` becomes missing
    because the EDA identifies it as unavailable employer information.

    Undocumented ``CODE_GENDER = XNA`` and
    ``NAME_FAMILY_STATUS = Unknown`` values are intentionally preserved for
    audit and policy review, as directed by the notebook.
    """

    _require_columns(frame, _CLEANING_COLUMNS, "clean application data")
    _require_numeric(frame, ("DAYS_EMPLOYED",), "clean application data")

    result = frame.copy(deep=True) if copy else frame
    sentinel = result["DAYS_EMPLOYED"].eq(EMPLOYMENT_SENTINEL)
    if "_EMPLOYED_SENTINEL" in result:
        sentinel = sentinel | result["_EMPLOYED_SENTINEL"].fillna(False).astype(bool)

    result["_EMPLOYED_SENTINEL"] = sentinel.astype(bool)
    result.loc[sentinel, "DAYS_EMPLOYED"] = np.nan
    result.loc[result["ORGANIZATION_TYPE"].eq("XNA"), "ORGANIZATION_TYPE"] = pd.NA
    return result


def create_application_features(
    frame: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Create the reusable fields defined in the EDA notebook.

    Ratio denominators and inputs must be positive. Derived age is limited to
    the EDA's plausible 18--100 year range, and employment tenure is missing
    when it implies employment before age 14. No values are imputed or capped.
    ``_MISSING_COUNT`` is calculated after cleaning, so the employment sentinel
    and unavailable organization category contribute to modeled missingness.

    ``_AGE_YEARS`` and ``_AGE_BAND`` are created for the notebook's fairness
    audit but remain listed in :data:`AUDIT_ONLY_COLUMNS` pending policy review.
    """

    _require_columns(frame, _FEATURE_COLUMNS, "create application features")
    _require_numeric(frame, _FEATURE_COLUMNS, "create application features")

    result = frame.copy(deep=True) if copy else frame
    source_columns = [column for column in result.columns if not column.startswith("_")]
    result["_MISSING_COUNT"] = result[source_columns].isna().sum(axis=1)

    income = result["AMT_INCOME_TOTAL"]
    annuity = result["AMT_ANNUITY"]
    credit = result["AMT_CREDIT"]
    goods_price = result["AMT_GOODS_PRICE"]

    valid_payment_income = income.gt(0) & annuity.gt(0)
    unannualized_payment_income = _safe_ratio(annuity, income, valid_payment_income)
    result["_PAYMENT_TO_INCOME_UNANNUALIZED"] = unannualized_payment_income
    result["_ANNUAL_PAYMENT_TO_INCOME"] = 12 * unannualized_payment_income
    result["_CREDIT_TO_INCOME"] = _safe_ratio(
        credit,
        income,
        income.gt(0) & credit.gt(0),
    )
    result["_CREDIT_TO_GOODS"] = _safe_ratio(
        credit,
        goods_price,
        goods_price.gt(0) & credit.gt(0),
    )

    age_years = -result["DAYS_BIRTH"] / DAYS_PER_YEAR
    result["_AGE_YEARS"] = age_years.where(age_years.between(18, 100))

    employed_years = (-result["DAYS_EMPLOYED"] / DAYS_PER_YEAR).where(
        result["DAYS_EMPLOYED"].lt(0)
    )
    employed_before_age_14 = employed_years.gt(result["_AGE_YEARS"] - 14)
    result["_EMPLOYED_YEARS"] = employed_years.mask(employed_before_age_14)

    result["_REGISTRATION_YEARS"] = (
        -result["DAYS_REGISTRATION"] / DAYS_PER_YEAR
    ).where(result["DAYS_REGISTRATION"].le(0))
    result["_ID_PUBLISH_YEARS"] = (
        -result["DAYS_ID_PUBLISH"] / DAYS_PER_YEAR
    ).where(result["DAYS_ID_PUBLISH"].le(0))

    property_columns = [
        column
        for column in source_columns
        if (
            column.endswith(("_AVG", "_MODE", "_MEDI"))
            or column == "TOTALAREA_MODE"
        )
        and is_numeric_dtype(result[column])
    ]
    result["_PROPERTY_MISSING_COUNT"] = (
        result[property_columns].isna().sum(axis=1) if property_columns else 0
    )
    result["_EXT_SOURCES_OBSERVED"] = result[list(_EXTERNAL_SOURCE_COLUMNS)].notna().sum(axis=1)
    result["_AGE_BAND"] = pd.cut(
        result["_AGE_YEARS"],
        bins=[18, 25, 35, 45, 55, 65, 100],
        include_lowest=True,
        labels=["18–25", "26–35", "36–45", "46–55", "56–65", "66+"],
    )
    return result


def prepare_application_data(
    frame: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Clean application data and create EDA-derived fields in one call."""

    cleaned = clean_application_data(frame, copy=copy)
    return create_application_features(cleaned, copy=False)
