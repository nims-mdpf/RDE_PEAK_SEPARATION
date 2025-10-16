from __future__ import annotations

import json
from pathlib import Path

from rdetoolkit.invoicefile import InvoiceFile
from rdetoolkit.models.rde2types import RdeOutputResourcePath
from rdetoolkit.rde2util import CharDecEncoding, read_from_json_file, write_to_json_file


class InvoiceWriter:
    """Invoice overwriter.

    Overwrite invoice.json files depending on conditions.

    """

    def read_invoice(self, invoice_path: Path) -> dict:
        """Read invoice file.

        Args:
            invoice_path (Path): invoice file path

        Returns:
            dict: invoice data

        """
        enc = CharDecEncoding.detect_text_file_encoding(invoice_path)
        with open(invoice_path, encoding=enc) as f:
            return json.load(f)

    def overwrite_invoice_calculation(
        self,
        resource_paths: RdeOutputResourcePath,
        invoice_obj: dict,
    ) -> None:
        """When using model pseudo voigt, Overwrite invoice calculation meta.

        Args:
            resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.
            invoice_obj (dict): invoice data.

        """
        invoice_org_obj = InvoiceFile(resource_paths.invoice_org)
        invoice_org_obj.invoice_obj = read_from_json_file(resource_paths.invoice_org)

        if invoice_obj["custom"]["model_type"] == "pseudo voigt":
            invoice_org_obj.invoice_obj["custom"]["calculation_software_name"] = "XPS Peak Separation Tool"
            invoice_org_obj.invoice_obj["custom"]["calculation_software_version"] = "xps-ps-pv-20220419"
            invoice_org_obj.invoice_obj["custom"]["calculation_key_object"] = \
                "Peak number, Peak position, Peak height, Peak width, Lorentz ratio, Peak area"
        else:
            invoice_org_obj.invoice_obj["custom"]["calculation_software_name"] = "XPS-peak-separation-convolutionVoigt"
            invoice_org_obj.invoice_obj["custom"]["calculation_software_version"] = "xps-ps-cv-20240712"

        enc = CharDecEncoding.detect_text_file_encoding(resource_paths.invoice_org)
        write_to_json_file(resource_paths.invoice_org, invoice_org_obj.invoice_obj, enc=enc)
        invoice_org_obj.overwrite(resource_paths.invoice.joinpath("invoice.json"))
