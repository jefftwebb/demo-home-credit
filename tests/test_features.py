"""Tests for EDA-derived application cleaning and feature creation."""

import unittest

import numpy as np
import pandas as pd

from home_credit.features import (
    clean_application_data,
    create_application_features,
    prepare_application_data,
)


def example_applications() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "SK_ID_CURR": [1, 2, 3],
            "TARGET": [0, 1, 0],
            "DAYS_EMPLOYED": [-3652.5, 365243.0, -7305.0],
            "ORGANIZATION_TYPE": ["Business", "XNA", "School"],
            "DAYS_BIRTH": [-14610.0, -6209.25, -10957.5],
            "DAYS_REGISTRATION": [-730.5, 1.0, -365.25],
            "DAYS_ID_PUBLISH": [-365.25, 0.0, 2.0],
            "AMT_INCOME_TOTAL": [120000.0, 0.0, 80000.0],
            "AMT_ANNUITY": [1000.0, 0.0, 800.0],
            "AMT_CREDIT": [60000.0, -1.0, 40000.0],
            "AMT_GOODS_PRICE": [50000.0, 0.0, 50000.0],
            "EXT_SOURCE_1": [0.4, np.nan, 0.2],
            "EXT_SOURCE_2": [np.nan, np.nan, 0.3],
            "EXT_SOURCE_3": [0.6, np.nan, 0.5],
            "APARTMENTS_AVG": [0.2, np.nan, 0.1],
            "TOTALAREA_MODE": [np.nan, np.nan, 0.3],
            "PROPERTY_LABEL_MODE": ["Panel", None, "Stone"],
            "CODE_GENDER": ["F", "XNA", "M"],
            "NAME_FAMILY_STATUS": ["Married", "Unknown", "Single"],
        }
    )


class CleanApplicationDataTests(unittest.TestCase):
    def test_cleans_eda_sentinel_without_mutating_input(self) -> None:
        source = example_applications()

        cleaned = clean_application_data(source)

        self.assertEqual(source.loc[1, "DAYS_EMPLOYED"], 365243.0)
        self.assertEqual(source.loc[1, "ORGANIZATION_TYPE"], "XNA")
        self.assertTrue(cleaned.loc[1, "_EMPLOYED_SENTINEL"])
        self.assertTrue(pd.isna(cleaned.loc[1, "DAYS_EMPLOYED"]))
        self.assertTrue(pd.isna(cleaned.loc[1, "ORGANIZATION_TYPE"]))
        self.assertEqual(cleaned.loc[1, "CODE_GENDER"], "XNA")
        self.assertEqual(cleaned.loc[1, "NAME_FAMILY_STATUS"], "Unknown")

    def test_cleaning_is_idempotent(self) -> None:
        once = clean_application_data(example_applications())
        twice = clean_application_data(once)

        pd.testing.assert_frame_equal(once, twice)


class CreateApplicationFeaturesTests(unittest.TestCase):
    def test_creates_ratios_and_validity_guarded_tenures(self) -> None:
        prepared = prepare_application_data(example_applications())

        self.assertAlmostEqual(prepared.loc[0, "_ANNUAL_PAYMENT_TO_INCOME"], 0.1)
        self.assertAlmostEqual(
            prepared.loc[0, "_PAYMENT_TO_INCOME_UNANNUALIZED"], 1 / 120
        )
        self.assertAlmostEqual(prepared.loc[0, "_CREDIT_TO_INCOME"], 0.5)
        self.assertAlmostEqual(prepared.loc[0, "_CREDIT_TO_GOODS"], 1.2)
        self.assertAlmostEqual(prepared.loc[0, "_AGE_YEARS"], 40.0)
        self.assertAlmostEqual(prepared.loc[0, "_EMPLOYED_YEARS"], 10.0)
        self.assertAlmostEqual(prepared.loc[0, "_REGISTRATION_YEARS"], 2.0)
        self.assertAlmostEqual(prepared.loc[0, "_ID_PUBLISH_YEARS"], 1.0)

        for column in (
            "_ANNUAL_PAYMENT_TO_INCOME",
            "_PAYMENT_TO_INCOME_UNANNUALIZED",
            "_CREDIT_TO_INCOME",
            "_CREDIT_TO_GOODS",
            "_AGE_YEARS",
            "_EMPLOYED_YEARS",
            "_REGISTRATION_YEARS",
        ):
            self.assertTrue(pd.isna(prepared.loc[1, column]), column)

        self.assertTrue(pd.isna(prepared.loc[2, "_EMPLOYED_YEARS"]))
        self.assertTrue(pd.isna(prepared.loc[2, "_ID_PUBLISH_YEARS"]))

    def test_creates_notebook_missingness_and_audit_features(self) -> None:
        prepared = prepare_application_data(example_applications())

        self.assertEqual(prepared.loc[0, "_PROPERTY_MISSING_COUNT"], 1)
        self.assertEqual(prepared.loc[1, "_PROPERTY_MISSING_COUNT"], 2)
        self.assertEqual(prepared.loc[0, "_EXT_SOURCES_OBSERVED"], 2)
        self.assertEqual(prepared.loc[1, "_EXT_SOURCES_OBSERVED"], 0)
        self.assertEqual(prepared.loc[0, "_AGE_BAND"], "36–45")
        self.assertTrue(pd.isna(prepared.loc[1, "_AGE_BAND"]))
        self.assertEqual(prepared.loc[0, "_MISSING_COUNT"], 2)
        self.assertEqual(prepared.loc[1, "_MISSING_COUNT"], 8)

    def test_feature_creation_requires_the_home_credit_schema(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            create_application_features(pd.DataFrame({"DAYS_BIRTH": [-10000]}))


if __name__ == "__main__":
    unittest.main()
