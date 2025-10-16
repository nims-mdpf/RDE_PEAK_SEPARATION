from __future__ import annotations

import glob
import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
from pdf2image import convert_from_path
from rdetoolkit.exceptions import StructuredError
from rdetoolkit.models.rde2types import RdeOutputResourcePath

from modules.interfaces import IGraphPlotter


class GraphPlotter(IGraphPlotter[pd.DataFrame]):
    """Template class for creating graphs and visualizations.

    This class serves as a template for the development team to create graphs
    and visualizations.It implements the IGraphPlotter interface.
    Developers can use this template class as a foundation for adding specific
    graphing logic and customizations based on the project's requirements.

    Args:
        df (pd.DataFrame): The DataFrame containing data to be plotted.
        save_path (Path): The path where the generated graph will be saved.

    Keyword Args:
        header (Optional[list[str]], optional):
         A list of column names to use as headers in the graph.
        Defaults to None.

    Example:
        graph_plotter = GraphPlotter()
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_plotter.plot(data, 'graph.png', header=['X Axis', 'Y Axis'])

    """

    def move_files(self, resource_paths: RdeOutputResourcePath) -> None:
        """Move the file to the given RDE's directory.

        Convert the file format from ppt to pdf, retrieve the images,
        and move it to the designated directory.

        Args:
            resource_paths (RdeOutputResourcePath): Paths to output resources for processing.

        Raises:
            StructuredError: File format conversion failure.

        """
        target_file = resource_paths.rawfiles[0]  # There can only be one file.
        try:
            os.chdir(resource_paths.temp)
            os.mkdir("image")
            cmds = [
                "libreoffice",
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to",
                "pdf",
                "result_figures.pptx",
            ]
            subprocess.run(
                cmds,
                encoding="utf_8",
                capture_output=True,
                check=True,
            )
            dist_path = Path(target_file).stem + "_summary.pdf"
            pdf_path = Path("result_figures.pdf").rename(dist_path)
            img_path = Path("image")
            convert_from_path(
                pdf_path,
                output_folder=img_path,
                fmt="png",
                output_file=pdf_path.stem,
                size=800,
            )
            os.remove("result_figures.pptx")

            os.chdir("../..")
            move_files = glob.glob(os.path.join(resource_paths.temp, "image", "*-1.png"))
            shutil.move(move_files[0], resource_paths.main_image)
            move_files = glob.glob(os.path.join(resource_paths.temp, "image", "*"))
            for move_file in move_files:
                shutil.move(move_file, resource_paths.temp)
            move_files = glob.glob(os.path.join(resource_paths.temp, "*.png"))
            for move_file in move_files:
                shutil.move(move_file, resource_paths.other_image)
        except Exception as e:
            err_msg = "failed in file format conversion failure."
            raise StructuredError(err_msg) from e
