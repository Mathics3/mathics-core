# -*- coding: utf-8 -*-

import re
import unicodedata


def slugify(value: str) -> str:
    """
    Converts to lowercase, removes non-word characters apart from '$',
    and converts spaces to hyphens. Also strips leading and trailing
    whitespace.

    Based on the Django version, but modified to preserve '$'.
    """
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^$`\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s`]+", "-", value)
