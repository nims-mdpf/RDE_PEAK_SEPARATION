from __future__ import annotations

from rdetoolkit.models.rde2types import RdeInputDirPaths, RdeOutputResourcePath
from rdetoolkit.rde2util import Meta

from modules.graph_handler import GraphPlotter
from modules.inputfile_handler import FileReader
from modules.invoice_handler import InvoiceWriter
from modules.meta_handler import MetaParser
from modules.structured_handler import StructuredDataProcessor


class PeakSeparationProcessingCoordinator:
    """Coordinator class for managing peak separation processing modules.

    This class serves as a coordinator for custom processing modules,
    facilitating the use of various components such as file reading,
    metadata parsing, graph plotting, and structured data processing.
    It is responsible for managing these components and providing an organized
    way to execute the required tasks.

    Args:
        file_reader (FileReader): An instance of the file reader component.
        meta_parser (MetaParser): An instance of the metadata parsing component.
        graph_plotter (GraphPlotter): An instance of the graph plotting component.
        structured_processer (StructuredDataProcessor): An instance of the structured data processing component.

    Attributes:
        file_reader (FileReader): The file reader component for reading input data.
        meta_parser (MetaParser): The metadata parsing component for processing metadata.
        graph_plotter (GraphPlotter): The graph plotting component for visualization.
        structured_processer (StructuredDataProcessor): The component for processing structured data.

    Example:
        module = PeakSeparationProcessingCoordinator(FileReader(),
         MetaParser(), GraphPlotter(), StructuredDataProcessor())
        # Note: The method 'execute_processing' hasn't been defined
        # in the provided code,
        # so its usage is just an example here.
        _module.execute_processing(srcpaths, resource_paths)

    """

    def __init__(
        self,
        invoice_writer: InvoiceWriter,
        file_reader: FileReader,
        meta_parser: MetaParser,
        graph_plotter: GraphPlotter,
        structured_processer: StructuredDataProcessor,
    ):
        self.invoice_writer = invoice_writer
        self.file_reader = file_reader
        self.meta_parser = meta_parser
        self.graph_plotter = graph_plotter
        self.structured_processer = structured_processer


def dataset(srcpaths: RdeInputDirPaths, resource_paths: RdeOutputResourcePath) -> None:
    """Execute structured processing in peak separation.

    Args:
        srcpaths (RdeInputDirPaths): Paths to input resources for processing.
        resource_paths (RdeOutputResourcePath): Paths to output resources for saving results.

    Returns:
        None

    """
    module = PeakSeparationProcessingCoordinator(
        InvoiceWriter(), FileReader(), MetaParser(), GraphPlotter(), StructuredDataProcessor(),
    )

    module.file_reader.check(resource_paths)

    # Read invoice and fitting data.
    invoice_obj = module.invoice_writer.read_invoice(resource_paths.invoice_org)
    module.file_reader.fit(resource_paths, invoice_obj)

    # Move csv file.
    module.structured_processer.move_files(resource_paths, invoice_obj)

    # Output meta. (empty)
    module.meta_parser.save_meta(
        resource_paths.meta.joinpath("metadata.json"),
        Meta(srcpaths.tasksupport.joinpath("metadata-def.json")),
        const_meta_info={},
        repeated_meta_info={},
    )

    # Move graph file.
    module.graph_plotter.move_files(resource_paths)

    # Overwrite invoice
    module.invoice_writer.overwrite_invoice_calculation(resource_paths, invoice_obj)
