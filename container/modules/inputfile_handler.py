from __future__ import annotations

import glob
import os
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
            invoice_obj (dict): invoice data.

        Raises:
            StructuredError: Fitting failure.

        """
        # 入力ファイルを'temp'にコピーし、一行目を削除したファイル'_data.csv'を作成
        target_file = resource_paths.rawfiles[0]  # There can only be one file.
        shutil.copy(target_file, resource_paths.temp)
        input_file = os.path.join(resource_paths.temp, Path(target_file).name)
        with open(input_file, encoding='utf-8') as fin, \
                open(os.path.join(resource_paths.temp, "_data.csv"), 'w', encoding='utf-8') as fout:
            next(fin)
            for line in fin:
                fout.write(line)
        os.remove(input_file)

        # ピーク分離実行
        os.chdir(resource_paths.temp)
        cmds = [
            "python",
            "/app/packages/pseudo_voigt/automatic_xps_peak_separation_single.py",
            "-p",
            "_data.csv",
        ]
        try:
            subprocess.run(
                cmds,
                encoding="utf_8",
                capture_output=True,
                check=True,
            )
            move_files = glob.glob("log*.txt")
            for move_file in move_files:
                shutil.move(move_file, "../logs/")
        except Exception as e:
            err_msg = "failed in data fitting."
            raise StructuredError(err_msg) from e

    def _fit_voigt_given_by_convolution(self, resource_paths: RdeOutputResourcePath, invoice_obj: dict) -> None:
        """Fit voigt given by convolution.

        Args:
            resource_paths (RdeOutputResourcePath): resource paths.
            invoice_obj (dict): invoice data.

        Raises:
            StructuredError: Fitting failure.

        """
        # 入力ファイルを'temp'にコピー
        target_file = resource_paths.rawfiles[0]  # There can only be one file.
        target = Path(target_file).name
        shutil.copy(target_file, resource_paths.temp)

        # ピーク分離実行
        os.chdir(resource_paths.temp)
        cmds = [
            "python",
            "/app/packages/convolution_voigt/peakSeparationForXPS.py",
            "--noise",
            invoice_obj["custom"]["noise_type"],
            target,
        ]
        try:
            log_file = "process.log"
            with open(log_file, "w") as fp:
                subprocess.run(
                    cmds,
                    encoding="utf_8",
                    stdout=fp,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
            shutil.move(log_file, "../logs/")
        except Exception as e:
            err_msg = "failed in data fitting."
            raise StructuredError(err_msg) from e

    def read(self, srcpath: Path) -> tuple[MetaType, pd.DataFrame]:
        """Read input file (No use)."""
        # Caution! dummy data
        self.data = pd.DataFrame([[1, 11], [2, 22], [3, 33]])
        self.meta = {"meta1": "value1", "meta2": "value2"}
        return self.data, self.meta
