from pathlib import Path
import pytest

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath

from modules.inputfile_handler import FileReader


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


def test_check(temp_dir, resource_paths):
    """入力チェック"""

    # ファイルがない
    resource_paths.rawfiles = ((temp_dir),)
    reader = FileReader()
    with pytest.raises(StructuredError) as e:
        reader.check(resource_paths)
    assert str(e.value).startswith("target .csv are required.")

    # ファイルの拡張子がcsv以外
    resource_paths.rawfiles = ((temp_dir / "test.txt"),)
    reader = FileReader()
    with pytest.raises(StructuredError) as e:
        reader.check(resource_paths)
    assert str(e.value).startswith("target .csv are required.")

# MEMO: fitting実行は解析Gの範疇なのでここではテストしない。
