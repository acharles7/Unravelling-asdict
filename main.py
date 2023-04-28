import collections
import functools
import itertools
import subprocess
import sys
from dataclasses import asdict, dataclass
from platform import machine, node, platform, system, uname
from pprint import pprint


def _unknown_as_blank(val):
    return '' if val == 'unknown' else val

# Python 3.8
# uname_result = collections.namedtuple("uname_result",
#                     "system node release version machine processor")


class _Processor:
    @classmethod
    def get(cls):
        func = getattr(cls, f'get_{sys.platform}', cls.from_subprocess)
        return func() or ''

    def from_subprocess():
        """
        Fall back to `uname -p`
        """
        try:
            return subprocess.check_output(
                ['uname', '-p'],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            pass


# Python 3.10
class uname_result(
    collections.namedtuple(
        "uname_result_base",
        "system node release version machine")
        ):
    """
    A uname_result that's largely compatible with a
    simple namedtuple except that 'processor' is
    resolved late and cached to avoid calling "uname"
    except when needed.
    """

    @functools.cached_property
    def processor(self):
        return _unknown_as_blank(_Processor.get())

    def __iter__(self):
        return itertools.chain(
            super().__iter__(),
            (self.processor,)
        )

    @classmethod
    def _make(cls, iterable):
        # override factory to affect length check
        num_fields = len(cls._fields)
        result = cls.__new__(cls, *iterable)
        if len(result) != num_fields + 1:
            msg = f'Expected {num_fields} arguments, got {len(result)}'
            raise TypeError(msg)
        return result

    def __getitem__(self, key):
        return tuple(self)[key]

    def __len__(self):
        return len(tuple(iter(self)))

    def __reduce__(self):
        return uname_result, tuple(self)[:len(self._fields)]


# Python master
class uname_result2(
    collections.namedtuple(
        "uname_result_base",
        "system node release version machine")
        ):
    """
    A uname_result that's largely compatible with a
    simple namedtuple except that 'processor' is
    resolved late and cached to avoid calling "uname"
    except when needed.
    """

    _fields = ('system', 'node', 'release', 'version', 'machine', 'processor')

    @functools.cached_property
    def processor(self):
        return _unknown_as_blank(_Processor.get())

    def __iter__(self):
        return itertools.chain(
            super().__iter__(),
            (self.processor,)
        )

    @classmethod
    def _make(cls, iterable):
        # override factory to affect length check
        num_fields = len(cls._fields) - 1
        result = cls.__new__(cls, *iterable)
        if len(result) != num_fields + 1:
            msg = f'Expected {num_fields} arguments, got {len(result)}'
            raise TypeError(msg)
        return result

    def __getitem__(self, key):
        return tuple(self)[key]

    def __len__(self):
        return len(tuple(iter(self)))

    def __reduce__(self):
        return uname_result, tuple(self)[:len(self._fields) - 1]


@dataclass
class UnameInfo:
    uname: uname_result2


def main():

    _system = "Darwin"
    _node = "CHARLESs-MBP.attlocal.net"
    _release = "21.5.0"
    _version = "Darwin Kernel Version 21.5.0: Tue Apr 26 21:08:22 PDT 2022; root:xnu-8020.121.3~4/RELEASE_X86_64"
    _machine = "x86_64"
    _processor = "i386"

    vals = _system, _node, _release, _version, _machine

    _uname_cache = uname_result2(*map(_unknown_as_blank, vals))
    print(_uname_cache)

    s_info = UnameInfo(uname=_uname_cache)
    s_info_as_dict = asdict(s_info)
    print(s_info_as_dict)


if __name__ == '__main__':
    main()
