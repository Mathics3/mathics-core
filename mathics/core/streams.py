# -*- coding: utf-8 -*-

"""
File Stream Operations
"""
import os
import os.path as osp
import sys
import tempfile
from io import open as io_open
from typing import Dict, List, Optional, Tuple

import requests

from mathics.core.util import canonic_filename
from mathics.settings import ROOT_DIR, USER_PACKAGE_DIR

HOME_DIR = osp.expanduser("~")
PATH_VAR: List[str] = [
    ".",
    HOME_DIR,
    USER_PACKAGE_DIR,
    osp.join(ROOT_DIR, "data"),
    osp.join(ROOT_DIR, "Packages"),
]


def create_temporary_file(prefix="Mathics3-", suffix=None, delete=True):
    if suffix == "":
        suffix = None

    fp = tempfile.NamedTemporaryFile(delete=delete, suffix=suffix)
    result = fp.name
    fp.close()
    return result


def urlsave_tmp(url, location=None, **kwargs):
    suffix = ""
    strip_url = url.split("/")
    if len(strip_url) > 3:
        strip_url = strip_url[-1]
        if strip_url != "":
            suffix = strip_url[len(strip_url.split(".")[0]) :]
        try:
            r = requests.get(url, allow_redirects=True)
            if location is None:
                location = create_temporary_file(prefix="Mathics3-url-", suffix=suffix)
            with open(location, "wb") as fp:
                fp.write(r.content)
                result = fp.name
            return result
        except Exception:
            return None
    return None


def path_search(filename: str) -> Tuple[Optional[str], bool]:
    """
    Search for a Mathics `filename` possibly adding extensions ".mx", ".m", or ".wl"
    or as a file under directory PATH_VAR or as an Internet address.

    Return the resolved file name and True if this is a file in the
    a temporary file created, which happens for Internet addresses,
    or False if the file is a file in the filesystem.
    """
    # For names of the form "name`", search for name.mx and name.m
    is_temporary_file = False
    if filename[-1] == "`":
        filename = filename[:-1].replace("`", osp.sep)
        for ext in [".mx", ".m", ".wl"]:
            result, is_temporary_file = path_search(filename + ext)
            if result is not None:
                return result, is_temporary_file
    if filename is not None:
        result = None
        # If filename is an Internet address, download the file
        # and store it in a temporary file
        lenfn = len(filename)
        if (
            (lenfn > 7 and filename[:7] == "http://")
            or (lenfn > 8 and filename[:8] == "https://")
            or (lenfn > 6 and filename[:6] == "ftp://")
        ):
            result = urlsave_tmp(filename)
            is_temporary_file = True
        else:
            for p in list(PATH_VAR) + [""]:
                path = canonic_filename(osp.join(p, filename))
                if osp.exists(path):
                    result = path
                    break

            # If `result` resolves to a dir, search within for Kernel/init.m and init.m
            if result is not None and osp.isdir(result):
                for ext in [osp.join("Kernel", "init.m"), "init.m"]:
                    tmp = osp.join(result, ext)
                    if osp.isfile(tmp):
                        return tmp, is_temporary_file
    return result, is_temporary_file


class Stream:
    """
    Opens a stream

    This can be used in a context_manager like this:

    with Stream(pypath, "r") as f:
         ...

    However see StreamManager and MathicsOpen which wraps this.
    """

    def __init__(
        self,
        name: str,
        mode="r",
        path: Optional[str] = None,
        encoding=None,
        io=None,
        channel_num=None,
        is_temporary_file: bool = False,
    ):
        if channel_num is None:
            channel_num = stream_manager.next
        if mode is None:
            mode = "r"
        if path is None:
            path = name
        self.name = name  # name provided by user
        self.path = path  # resolved path name
        self.mode = mode
        self.encoding = encoding
        self.io = io
        self.n = channel_num
        self.is_temporary_file = is_temporary_file

        if mode not in ["r", "w", "a", "rb", "wb", "ab"]:
            raise ValueError("Can't handle mode {0}".format(mode))

    def __enter__(self):
        # find path
        path, is_temporary_file = path_search(self.name)
        if path is None and self.mode in ["w", "a", "wb", "ab"]:
            path = self.name
        if path is None:
            raise IOError

        # determine encoding
        if "b" not in self.mode:
            encoding = self.encoding
        else:
            encoding = None

        # open the stream
        fp = io_open(path, self.mode, encoding=encoding)
        stream_manager.add(
            name=self.name,
            mode=self.mode,
            path=path,
            encoding=encoding,
            io=fp,
            is_temporary_file=is_temporary_file,
        )
        return fp

    def __exit__(self, type, value, traceback):
        if self.io is not None:
            self.io.close()
        # Leave around self.io so we can call closed() to query its status.
        stream_manager.delete(self.n)


class StreamsManager:
    __instance = None
    STREAMS: Dict[int, Stream] = {}

    @staticmethod
    def get_instance():
        """Static access method."""
        if StreamsManager.__instance is None:
            StreamsManager()
        return StreamsManager.__instance

    def __init__(self):
        """Virtually private constructor."""
        if StreamsManager.__instance is not None:
            raise Exception("this class is a singleton!")
        else:
            StreamsManager.__instance = self

    def add(
        self,
        name: str,
        mode: Optional[str] = None,
        path: Optional[str] = None,
        encoding=None,
        io=None,
        num: Optional[int] = None,
        is_temporary_file: bool = False,
    ) -> Optional["Stream"]:
        if num is None:
            num = self.next
            assert isinstance(num, int)
            # In theory in this branch we won't find num.
        if path is None:
            path = name
        if mode is None:
            mode = "r"
        # sanity check num
        found = self.lookup_stream(num)
        if found and found is not None:
            raise Exception(f"Stream {num} already open")
        stream = Stream(name, mode, path, encoding, io, num, is_temporary_file)
        self.STREAMS[num] = stream
        return stream

    def delete(self, n: int) -> bool:
        stream = self.lookup_stream(n)
        if stream is None:
            return False
        self.delete_stream(stream)
        return True

    def delete_stream(self, stream: Stream):
        """
        Delete `stream` from the list of streams we
        keep track of.
        """
        is_temporary_file = stream.is_temporary_file
        if is_temporary_file:
            os.unlink(stream.path)
        del self.STREAMS[stream.n]

    def get_stream_by_name(self, name: str) -> Optional[Stream]:
        """
        Find and return a stream given its stream name.
        Return None if not stream is found.
        """
        for i in self.STREAMS:
            if self.STREAMS[i].name == name:
                return self.STREAMS[i]
        return None

    # Note: WMA documentationspecifies that lookup by "name" should be unique, but it appears it
    # as of 13.2.0 name does not have to be unique. We'll follow what WMA
    # does as opposed to what the documentation says.
    def get_stream_and_channel_by_name(self, name: str) -> Tuple[Optional[Stream], int]:
        """
        Find a stream given its stream name. If there is only one channel associated with that
        name, then return a tuple of the the name and channel.
        """
        # When there are duplicates, WMA seems to find largest, the most-recent? stream
        # first. We will mimic this behavior using reversed().
        for i in reversed(self.STREAMS):
            if self.STREAMS[i].name == name:
                return self.STREAMS[i], i
        return None, -1

    def lookup_stream(self, n: int) -> Optional[Stream]:
        """
        Find and return a stream given is stream number `n`.
        None is returned if no stream found.
        """
        return self.STREAMS.get(n, None)

    @property
    def next(self):
        numbers = [stream.n for stream in self.STREAMS.values()] + [2]
        return max(numbers) + 1


stream_manager = StreamsManager()


stream_manager.add("stdin", mode="r", num=0, io=sys.stdin)
stream_manager.add("stdout", mode="w", num=1, io=sys.stdout)
stream_manager.add("stderr", mode="w", num=2, io=sys.stderr)
