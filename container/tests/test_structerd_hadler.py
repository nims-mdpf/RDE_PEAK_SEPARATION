import pytest
from pathlib import Path

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath

from modules.structured_handler import StructuredDataProcessor


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def resource_paths(temp_dir):
    return RdeOutputResourcePath(
        raw=Path('tests'),
        nonshared_raw=Path('tests'),
        rawfiles=(temp_dir,),
        struct=temp_dir,
        main_image=Path('tests'),
        other_image=Path('tests'),
        meta=Path('tests'),
        thumbnail=Path('tests'),
        logs=Path('tests'),
        invoice=Path('tests'),
        invoice_schema_json=Path('tests'),
        invoice_org=Path('tests')
    )


def test_move_files(resource_paths):

    # fittingが失敗していた場合
    invoice_obj = {}
    invoice_obj.setdefault("custom", {})["model_type"] = "pseudo voigt"

    processor = StructuredDataProcessor()
    with pytest.raises(StructuredError) as e:
        processor.move_files(resource_paths, invoice_obj)
    assert str(e.value).startswith("failed in file moving.")

# MEMO: fitting成功時はtest_output.pyで確認済み。
