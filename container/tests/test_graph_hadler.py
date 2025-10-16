from pathlib import Path
import pytest

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath

from modules.graph_handler import GraphPlotter


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def resource_paths(temp_dir):
    return RdeOutputResourcePath(
        raw=Path('tests'),
        nonshared_raw=Path('tests'),
        rawfiles=(Path('tests'),),
        struct=temp_dir,
        main_image=temp_dir,
        other_image=temp_dir,
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

    plotter = GraphPlotter()
    with pytest.raises(StructuredError) as e:
        plotter.move_files(resource_paths, invoice_obj)
    assert str(e.value).startswith("failed in file format conversion failure.")

# MEMO: fitting成功時はtest_output.pyで確認済み。
