# -*- coding: utf-8 -*-
import sys
from mathics.builtin import check_requires_list
from mathics.core.utils import IS_PYPY

if IS_PYPY or not check_requires_list(["scipy", "numpy"]):
    raise ImportError

import numpy as np


def _scipy_interface(integrator, options_map, mandatory=None, adapt_func=None):
    """
    This function provides a proxy for scipy.integrate
    functions, adapting the parameters.
    """

    def _scipy_proxy_func_filter(fun, a, b, **opts):
        native_opts = {}
        if mandatory:
            native_opts.update(mandatory)
        for opt, val in opts.items():
            native_opt = options_map.get(opt, None)
            if native_opt:
                if native_opt[1]:
                    val = native_opt[1](val)
                native_opts[native_opt[0]] = val
        return adapt_func(integrator(fun, a, b, **native_opts))

    def _scipy_proxy_func(fun, a, b, **opts):
        native_opts = {}
        if mandatory:
            native_opts.update(mandatory)
        for opt, val in opts.items():
            native_opt = options_map.get(opt, None)
            if native_opt:
                if native_opt[1]:
                    val = native_opt[1](val)
                native_opts[native_opt[0]] = val
        return integrator(fun, a, b, **native_opts)

    return _scipy_proxy_func_filter if adapt_func else _scipy_proxy_func


try:
    from scipy.integrate import romberg, quad, nquad
except Exception:
    scipy_nintegrate_methods = {}
else:
    scipy_nintegrate_methods = {
        "NQuadrature": tuple(
            (
                _scipy_interface(
                    nquad, {}, {"full_output": 1}, lambda res: (res[0], res[1])
                ),
                True,
            )
        ),
        "Quadrature": tuple(
            (
                _scipy_interface(
                    quad,
                    {
                        "tol": ("epsabs", None),
                        "maxrec": ("limit", lambda maxrec: int(2**maxrec)),
                    },
                    {"full_output": 1},
                    lambda res: (res[0], res[1]),
                ),
                False,
            )
        ),
        "Romberg": tuple(
            (
                _scipy_interface(
                    romberg,
                    {"tol": ("tol", None), "maxrec": ("divmax", None)},
                    None,
                    lambda x: (x, np.nan),
                ),
                False,
            )
        ),
    }

scipy_nintegrate_methods["Automatic"] = scipy_nintegrate_methods["Quadrature"]
scipy_nintegrate_messages = dict()
