"""Phase 0 guardrail tests: masking, anonymisation, and junk filtering.

These lock in the PII-protection behaviour so future changes can't silently
regress it. Run: python -m pytest -q
"""
import pandas as pd

from src.anonymise import is_junk_identity, normalize
from src.utils import mask_email, mask_id, mask_mobile, mask_name, mask_text_blob


# --------------------------- masking ------------------------------------- #
def test_mask_mobile_keeps_first2_last2():
    assert mask_mobile("9822270199") == "98XXXXXX99"
    assert mask_mobile("98765") == "98X65"


def test_mask_mobile_handles_blanks():
    assert mask_mobile(None) == ""
    assert mask_mobile(float("nan")) == ""


def test_mask_email():
    assert mask_email("sukhakartashirur@gmail.com").startswith("s***")
    assert "@gmail.com" in mask_email("sukhakartashirur@gmail.com")


def test_mask_id_last4_only():
    assert mask_id("ASPLDR106") == "*****R106"


def test_mask_name():
    assert mask_name("Sharma Traders").startswith("Name_S")


def test_mask_text_blob_masks_embedded_phone():
    out = mask_text_blob("call 9822270199 or mail a@b.com")
    assert "9822270199" not in out
    assert "a@b.com" not in out


# --------------------------- normalize / junk ---------------------------- #
def test_normalize_collapses_case_and_punct():
    assert normalize("  VEDANTA (A)  MEDICAL ") == "VEDANTA A MEDICAL"


def test_junk_identities_rejected():
    for j in ["Totals:", "TOTAL", "Opening Balance", "", "  ", "12345", "NA"]:
        assert is_junk_identity(normalize(j)) is True


def test_real_identity_accepted():
    assert is_junk_identity(normalize("Sharma Medical Stores")) is False


# --------------------------- anonymise round-trip ------------------------ #
def test_anonymise_df_replaces_names_with_codes(tmp_path, monkeypatch):
    # Use the real lookup if present; otherwise this asserts the masking path.
    from src import anonymise
    cfg = anonymise.load_config()
    df = pd.DataFrame({
        "Customer name": ["VEDANTA (A)  MEDICAL"],
        "Mobile": ["9822270199"],
        "Net": [3867],
    })
    out = anonymise.anonymise_df(df, cfg)
    val = str(out.loc[0, "Customer name"])
    assert val.startswith("Customer_")          # never the real name
    assert "9822270199" not in str(out.loc[0, "Mobile"])
    assert out.loc[0, "Net"] == 3867            # business figures untouched
