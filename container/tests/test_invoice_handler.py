import json
import os
from pathlib import Path
import pytest

from rdetoolkit.models.rde2types import RdeOutputResourcePath

from modules.invoice_handler import InvoiceWriter


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def resource_paths(temp_dir):
    return RdeOutputResourcePath(
        raw=Path('tests'),
        nonshared_raw=Path('tests'),
        rawfiles=(Path('tests'),),
        struct=Path('tests'),
        main_image=Path('tests'),
        other_image=Path('tests'),
        meta=Path('tests'),
        thumbnail=Path('tests'),
        logs=Path('tests'),
        invoice=temp_dir,
        invoice_schema_json=Path('tests'),
        invoice_org=temp_dir / 'invoice.json'
    )


def test_overwrite_invoice_calculation(resource_paths):

    # 上書き確認
    invoice_obj = {}
    invoice_obj = {
        'custom': {
            'model_type': "pseudo voigt",
            'calculation_software_name': None,
            'calculation_software_version': None,
            'calculation_key_object': None,
        },
    }

    writer = InvoiceWriter()
    with open(resource_paths.invoice_org, 'w') as fw:
        json.dump(invoice_obj, fw)
    writer.overwrite_invoice_calculation(resource_paths, invoice_obj)
    with open(resource_paths.invoice.joinpath("invoice.json")) as fr:
        assert json.load(fr) == {
            'custom': {
                'model_type': "pseudo voigt",
                'calculation_software_name': "XPS Peak Separation Tool",
                'calculation_software_version': "xps-ps-pv-20220419",
                'calculation_key_object': "Peak number, Peak position, Peak height, Peak width, Lorentz ratio, Peak area",
            },
        }

    if os.path.exists(resource_paths.invoice_org):
        os.remove(resource_paths.invoice_org)
