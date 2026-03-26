"""Parse partition offsets from parameter.txt at runtime.

Reads the CMDLINE line containing mtdparts and extracts partition
name, size, and offset for each entry. Offsets are NEVER hardcoded.

Format:
    CMDLINE:mtdparts=:SIZE@OFFSET(NAME),SIZE@OFFSET(NAME),...

Where:
    SIZE   = hex sector count (e.g. 0x00002000) or '-' for grow-to-fill
    OFFSET = hex sector number (e.g. 0x00002000)
    NAME   = partition name, optionally with ':grow' suffix

Example line:
    CMDLINE:mtdparts=:0x00002000@0x00002000(uboot),0x00006000@0x00004000(boot),-@0x00010000(rootfs:grow)

Parsed result:
    [
        PartitionInfo(name='uboot',  offset='0x00002000', offset_decimal=8192,  size='0x00002000'),
        PartitionInfo(name='boot',   offset='0x00004000', offset_decimal=16384, size='0x00006000'),
        PartitionInfo(name='rootfs', offset='0x00010000', offset_decimal=65536, size='-'),
    ]
"""

import re
from pathlib import Path

from agent.models.schemas import PartitionInfo


# Regex for one mtdparts entry: SIZE@OFFSET(NAME)
# SIZE can be hex (0x...) or '-' (grow to fill)
# OFFSET is always hex (0x...)
# NAME can contain ':grow' suffix which we strip
_MTDPART_ENTRY_RE = re.compile(
    r"(?P<size>0x[0-9a-fA-F]+|-)@(?P<offset>0x[0-9a-fA-F]+)\((?P<name>[^)]+)\)"
)

# Image file mapping: partition name → image filename
_PARTITION_TO_IMAGE: dict[str, str] = {
    "uboot": "uboot.img",
    "boot": "boot.img",
    "rootfs": "ExportImage.img",
}


def parse_parameter_file(parameter_path: Path) -> list[PartitionInfo]:
    """Parse partition table from a Rockchip parameter.txt file.

    Reads the file, finds the CMDLINE line with mtdparts, and extracts
    each partition entry into a PartitionInfo model.

    Args:
        parameter_path: Absolute path to parameter.txt.

    Returns:
        List of PartitionInfo entries, ordered as they appear in the file.

    Raises:
        FileNotFoundError: If parameter_path does not exist.
        ValueError: If no CMDLINE/mtdparts line is found, or it contains
                    no valid partition entries.
    """
    if not parameter_path.is_file():
        raise FileNotFoundError(f"parameter.txt not found at: {parameter_path}")

    content = parameter_path.read_text(encoding="utf-8")

    # Find the CMDLINE line containing mtdparts=
    cmdline = _extract_cmdline(content)
    if cmdline is None:
        raise ValueError(
            f"No CMDLINE line with 'mtdparts=' found in: {parameter_path}"
        )

    # Parse each SIZE@OFFSET(NAME) entry
    partitions = _parse_mtdparts(cmdline)
    if not partitions:
        raise ValueError(
            f"No partition entries found in CMDLINE: {cmdline}"
        )

    return partitions


def _extract_cmdline(content: str) -> str | None:
    """Extract the CMDLINE value containing mtdparts from file content.

    Args:
        content: Full text content of parameter.txt.

    Returns:
        The mtdparts portion of the CMDLINE line, or None if not found.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("CMDLINE:") and "mtdparts=" in stripped:
            # Extract everything after 'mtdparts='
            idx = stripped.index("mtdparts=")
            return stripped[idx:]
    return None


def _parse_mtdparts(mtdparts_line: str) -> list[PartitionInfo]:
    """Parse mtdparts string into a list of PartitionInfo.

    Args:
        mtdparts_line: String starting with 'mtdparts=' containing
                       comma-separated SIZE@OFFSET(NAME) entries.

    Returns:
        List of PartitionInfo entries.
    """
    partitions: list[PartitionInfo] = []

    for match in _MTDPART_ENTRY_RE.finditer(mtdparts_line):
        raw_name = match.group("name")
        size_str = match.group("size")
        offset_str = match.group("offset")

        # Strip ':grow' or any other suffix from partition name
        clean_name = raw_name.split(":")[0]

        # Convert offset hex string to decimal integer
        offset_decimal = int(offset_str, 16)

        # Look up the corresponding image file
        image_file = _PARTITION_TO_IMAGE.get(clean_name, "")

        partitions.append(
            PartitionInfo(
                name=clean_name,
                offset=offset_str,
                offset_decimal=offset_decimal,
                size=size_str,
                image_file=image_file,
            )
        )

    return partitions


def get_partition_offset(
    partitions: list[PartitionInfo],
    name: str,
) -> str:
    """Get the hex offset for a named partition.

    Args:
        partitions: Parsed partition list from parse_parameter_file().
        name: Partition name (e.g. 'uboot', 'boot', 'rootfs').

    Returns:
        Hex offset string (e.g. '0x00002000').

    Raises:
        KeyError: If partition name is not found.
    """
    for part in partitions:
        if part.name == name:
            return part.offset
    available = [p.name for p in partitions]
    raise KeyError(
        f"Partition '{name}' not found. Available: {available}"
    )
