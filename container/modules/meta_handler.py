from __future__ import annotations

from pathlib import Path

from rdetoolkit import rde2util
from rdetoolkit.models.rde2types import MetaType, RepeatedMetaType

from modules.interfaces import IMetaParser


class MetaParser(IMetaParser[MetaType]):
    """Template class for parsing and saving metadata.

    This class serves as a template for the development team
    to parse and save metadata. It implements the IMetaParser interface.
    Developers can use this template class as a foundation for adding specific
    parsing and saving logic for metadata based on the project's requirements.

    Args:
        data (MetaType): The metadata to be parsed and saved.

    Returns:
        tuple[MetaType, MetaType]:
         A tuple containing the parsed constant and repeated metadata.

    Example:
        meta_parser = MetaParser()
        parsed_const_meta, parsed_repeated_meta = meta_parser.parse(data)
        meta_obj = rde2util.Meta(metaDefFilePath='meta_definition.json')
        saved_info = meta_parser.save_meta('saved_meta.json', meta_obj,
                                       const_meta_info=parsed_const_meta,
                                       repeated_meta_info=parsed_repeated_meta)

    """

    def parse(self, data: MetaType) -> tuple[MetaType, RepeatedMetaType]:
        """Parse and extract constant and repeated metadata from the provided data.

        Args:
            data (MetaType): meta type.

        """
        # dummy return
        self.const_meta_info: MetaType = data
        self.repeated_meta_info: RepeatedMetaType = {
            "key": ["key_value1", "key_value2"],
            "sample": ["sample_value1", "sample_value2"],
        }
        return self.const_meta_info, self.repeated_meta_info

    def save_meta(
        self,
        save_path: Path,
        metaobj: rde2util.Meta,
        *,
        const_meta_info: MetaType | None = None,
        repeated_meta_info: RepeatedMetaType | None = None,
    ) -> None:
        """Save parsed metadata to a file using the provided Meta object.

        Args:
            save_path (Path): metadata.json path.
            metaobj (rde2util.Meta): meta data define object.
            const_meta_info (MetaType | None): const meta data.
            repeated_meta_info (RepeatedMetaType | None): variable meta data.

        """
        if const_meta_info is None:
            const_meta_info = self.const_meta_info
        if repeated_meta_info is None:
            repeated_meta_info = self.repeated_meta_info
        metaobj.assign_vals(const_meta_info)
        metaobj.assign_vals(repeated_meta_info)

        metaobj.writefile(save_path)
