from __future__ import annotations

import glob
import os
import shutil

from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath


class StructuredDataProcessor:
    """Template class for parsing structured data.

    This class serves as a template for the development team
    to read and parse structured data.
    Developers can use this template class
    as a foundation for adding specific file reading and
    parsing logic based on the project's requirements.

    Example:
        csv_handler = StructuredDataProcessor()
        df = pd.DataFrame([[1,2,3],[4,5,6]])

    """

    def move_files(self, resource_paths: RdeOutputResourcePath, invoice_obj: dict) -> None:
        """Move the file to the given RDE's directory.

        Args:
            resource_paths (RdeOutputResourcePath): Paths to output resources for processing.
            invoice_obj (dict): invoice data.

        Raises:
            StructuredError: File format conversion failure.

        """
        try:

            target_csv_patterns = [
                "*_parameters.csv",
                "*_result.csv",
                "summary_BIC.csv",
            ]
            move_files = []
            if invoice_obj["custom"]["model_type"] == "pseudo voigt":
                for pattern in target_csv_patterns:
                    move_files.extend(glob.glob(os.path.join(resource_paths.temp, pattern)))
                move_files += glob.glob(os.path.join(resource_paths.temp, "*.txt"))
                data_file = os.path.join(resource_paths.temp, "_data.csv")
                if data_file in move_files:
                    move_files.remove(data_file)
            else:
                for pattern in target_csv_patterns:
                    move_files.extend(glob.glob(os.path.join(resource_paths.temp, pattern)))
                raw_file = os.path.join(
                    resource_paths.temp,
                    resource_paths.rawfiles[0].name,
                )
                if raw_file in move_files:
                    move_files.remove(raw_file)

            for move_file in move_files:
                shutil.move(move_file, resource_paths.struct)

            shutil.copy(
                os.path.join(resource_paths.temp, "result_figures.pptx"),
                resource_paths.struct,
            )

        except Exception as e:
            err_msg = "failed in file moving."
            raise StructuredError(err_msg) from e
