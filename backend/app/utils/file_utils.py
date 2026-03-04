import os
import re


def sanitize_filename(filename: str) -> str:
    """
    Strip directory components and replace unsafe characters.
    Preserves only alphanumerics, dots, hyphens, and underscores.
    """
    # Strip any directory path components
    name = os.path.basename(filename)
    # Replace unsafe characters with underscores
    name = re.sub(r"[^\w.\-]", "_", name)
    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name)
    return name


def generate_unique_filepath(directory: str, filename: str) -> str:
    """
    If `filename` already exists in `directory`, append _1, _2, etc.
    before the extension until a unique name is found.

    Returns the full path to the unique file.
    """
    filepath = os.path.join(directory, filename)
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{base}_{counter}{ext}"
        new_path = os.path.join(directory, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1
