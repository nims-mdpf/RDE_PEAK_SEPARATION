from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pandas as pd
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import MetaType, RdeOutputResourcePath


class FileReader:
    """Template class for reading and parsing input data.

    This class serves as a template for the development team
    to read and parse input data.It implements the IInputFileParser interface.
    Developers can use this template class as a foundation for adding specific
    file reading and parsing logic based on the project's requirements.

    Args:
        srcpaths (tuple[Path, ...]): Paths to input source files.

    Returns:
        Any: The loaded data from the input file(s).

    Example:
        file_reader = FileReader()
        loaded_data = file_reader.read(('file1.txt', 'file2.txt'))
        file_reader.to_csv('output.csv')

    """

    def check(self, resource_paths: RdeOutputResourcePath) -> None:
        """Check input file.

        Args:
            resource_paths (RdeOutputResourcePath): resource paths.

        Returns:
            list: target files.

        """
        if len(resource_paths.rawfiles) < 1:
            err_msg = "target .csv are required."
            raise StructuredError(err_msg)
        for candidate_rawfile in resource_paths.rawfiles:
            if candidate_rawfile.suffix.lower() != ".csv":
                err_msg = "target .csv are required."
                raise StructuredError(err_msg)

    def fit(self, resource_paths: RdeOutputResourcePath, invoice_obj: dict) -> None:
        """Perform peak fitting.

        Args:
            resource_paths (RdeOutputResourcePath): resource paths.
            invoice_obj (dict): invoice data.

        """
        if invoice_obj["custom"]["model_type"] == "pseudo voigt":
            self._fit_pseudo_voigt(resource_paths)
        else:
            self._fit_voigt_given_by_convolution(resource_paths, invoice_obj)

    def _fit_pseudo_voigt(self, resource_paths: RdeOutputResourcePath) -> None:
        """Fit pseudo voigt.

        Args:
            resource_paths (RdeOutputResourcePath): resource paths.

        Raises:
            StructuredError: Fitting failure.

        """
        try:
            target_file = Path(resource_paths.rawfiles[0])
            temp_dir = Path(resource_paths.temp)

            target = target_file.name
            dst = temp_dir / target

            if target_file.resolve() != dst.resolve():
                shutil.copy(target_file, dst)

            input_file = temp_dir / "_data.csv"

            with open(dst, encoding="utf-8") as fin, \
                    open(input_file, "w", encoding="utf-8") as fout:
                next(fin)
                for line in fin:
                    fout.write(line)

            cmds = [
                "python",
                "/app/packages/pseudo_voigt/automatic_xps_peak_separation_single.py",
                "-p",
                "_data.csv",
            ]

            result = subprocess.run(
                cmds,
                check=False,
                cwd=temp_dir,
                encoding="utf-8",
                capture_output=True,
            )

            if result.returncode != 0:
                msg = "pseudo voigt process failed."
                raise RuntimeError(msg)

            logs_dir = temp_dir.parent / "logs"
            logs_dir.mkdir(exist_ok=True)

            for log_file in temp_dir.glob("log*.txt"):
                shutil.move(
                    str(log_file),
                    str(logs_dir / log_file.name),
                )

        except Exception as e:
            msg = "failed in data fitting."
            raise StructuredError(msg) from e

    def _fit_voigt_given_by_convolution(
            self,
            resource_paths: RdeOutputResourcePath,
            invoice_obj: dict,
    ) -> None:
        """Fit voigt given by convolution.

        Args:
            resource_paths (RdeOutputResourcePath): resource paths.
            invoice_obj (dict): invoice data.

        Raises:
            StructuredError: Fitting failure.

        """
        try:
            target_file = Path(resource_paths.rawfiles[0])
            temp_dir = Path(resource_paths.temp)

            target = target_file.name
            dst = temp_dir / target

            if target_file.resolve() != dst.resolve():
                shutil.copy(target_file, dst)

            cmds = [
                "python",
                "/app/packages/convolution_voigt/peakSeparationForXPS.py",
                "--noise",
                invoice_obj["custom"]["noise_type"],
                target,
            ]

            result = subprocess.run(
                cmds,
                check=False,
                cwd=temp_dir,
                encoding="utf-8",
                capture_output=True,
            )

            if result.returncode != 0:
                msg = "convolution voigt process failed."
                raise RuntimeError(msg)

            logs_dir = temp_dir.parent / "logs"
            logs_dir.mkdir(exist_ok=True)

            log_file = temp_dir / "process.log"

            if log_file.exists():
                shutil.move(
                    str(log_file),
                    str(logs_dir / log_file.name),
                )

        except Exception as e:
            msg = "failed in data fitting."
            raise StructuredError(msg) from e

    def read(self, srcpath: Path) -> tuple[MetaType, pd.DataFrame]:
        """Read input file (No use)."""
        # Caution! dummy data
        self.data = pd.DataFrame([[1, 11], [2, 22], [3, 33]])
        self.meta = {"meta1": "value1", "meta2": "value2"}
        return self.data, self.meta
