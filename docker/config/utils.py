import os
import jinja2
from typing import List

_THISDIR = os.path.dirname(__file__)

def read_txt(filename:str) -> List[str]:
    """
    Return list of non-empty, non-comment lines of 'filename'
    """
    comment_char = "#"

    filepath = (filename
                if filename.startswith('/')
                else os.path.join(_THISDIR, f"{filename}.py"))

    images = []
    with open(filepath, 'r') as fp:
        for entry in fp.readlines():
            entry = entry.strip()
            if entry and entry[0] != comment_char:
                images.append(entry)

    return images
