# -*- coding: utf-8 -*-
"""
Model Context Protocol (MCP) Server for Mathics3 (Wolfram Language + Projective CAS).

Exposes a zero-dependency JSON-RPC 2.0 stdio MCP server (`mathics3-mcp` or
`python -m mathics.mcp_server`) allowing AI agents (Claude, OpenCode, Cursor, etc.)
to evaluate Wolfram Language expressions, symbolic & improper integrals over
Q(i, sqrt(d-1)), Riemann sphere contour integrals, Cauchy-Lagrange residues,
Pade approximants, and arbitrary-precision numeric evaluations without requiring
a proprietary Wolfram Engine license.
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Dict, Optional

from mathics.session import MathicsSession, load_default_settings_files
from mathics.version import __version__

SERVER_NAME = "mathics3-mcp"
PROTOCOL_VERSION = "2024-11-05"

TOOLS_SPEC = [
    {
        "name": "wolfram_eval",
        "description": (
            "Evaluate any Wolfram Language (Mathematica) expression in a persistent Mathics3 session. "
            "Returns the exact result in InputForm, optional TeXForm (LaTeX), and any printed/warning messages."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Wolfram Language expression, e.g. 'Integrate[Sin[x^2], {x, 0, Infinity}]' or 'Solve[x^4 + 1 == 0, x]'.",
                },
                "include_tex": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include TeXForm (LaTeX) rendering of the result.",
                },
            },
            "required": ["code"],
        },
    },
    {
        "name": "wolfram_integrate",
        "description": (
            "Compute an indefinite, definite, or improper integral in Wolfram Language using the "
            "Projective Calculus kernel over Q(i, sqrt(d-1)) and SymPy. Supports arbitrary-precision numeric evaluation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": "Integrand in Wolfram Language syntax, e.g. '1/(1 + x^4)', 'Sqrt[Tan[x]]', 'Sin[x^2]'.",
                },
                "var": {
                    "type": "string",
                    "default": "x",
                    "description": "Integration variable name, e.g. 'x' or 'z'.",
                },
                "lower": {
                    "type": "string",
                    "description": "Optional lower limit (e.g. '0', '-Infinity', '1 + I'). Omit for indefinite integral.",
                },
                "upper": {
                    "type": "string",
                    "description": "Optional upper limit (e.g. '1', 'Infinity', '2 + 3 I'). Omit for indefinite integral.",
                },
                "numeric_precision": {
                    "type": "integer",
                    "description": "Optional arbitrary precision (number of decimal digits, e.g. 50 or 200) via N[..., digits].",
                },
            },
            "required": ["expr"],
        },
    },
    {
        "name": "wolfram_contour_integrate",
        "description": (
            "Compute a closed contour integral ContourIntegrate[expr, {var, center, radius}] around "
            "the circle |var - center| = radius on the Riemann sphere P^1(C) via Ostrowski-Hermite reduction "
            "and Cauchy-Lagrange residues."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": "Rational integrand in Wolfram Language syntax, e.g. '1/(1 + z^4)'.",
                },
                "var": {
                    "type": "string",
                    "default": "z",
                    "description": "Complex variable name (default: 'z').",
                },
                "center": {
                    "type": "string",
                    "default": "0",
                    "description": "Complex circle center, e.g. '0', 'I', '1 + I'.",
                },
                "radius": {
                    "type": "string",
                    "default": "1",
                    "description": "Positive circle radius, e.g. '1' or '2'.",
                },
            },
            "required": ["expr"],
        },
    },
    {
        "name": "wolfram_residue",
        "description": (
            "Compute the Cauchy-Lagrange residue Residue[expr, {var, pole}] at any pole on the "
            "Riemann sphere P^1(C), including 'Infinity'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": "Meromorphic expression in Wolfram Language syntax, e.g. '1/(1 + z^4)' or '1/z'.",
                },
                "var": {
                    "type": "string",
                    "default": "z",
                    "description": "Complex variable name (default: 'z').",
                },
                "pole": {
                    "type": "string",
                    "description": "Pole location in C or 'Infinity', e.g. '(1 + I)/Sqrt[2]' or 'Infinity'.",
                },
            },
            "required": ["expr", "pole"],
        },
    },
    {
        "name": "wolfram_pade_approximant",
        "description": (
            "Compute the exact rational Pade approximant PadeApproximant[expr, {var, x0, {m, n}}] "
            "of degree [m/n] about var = x0."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": "Expression in Wolfram Language syntax, e.g. 'Exp[x]' or 'ArcTan[x]'.",
                },
                "var": {
                    "type": "string",
                    "default": "x",
                    "description": "Variable name (default: 'x').",
                },
                "x0": {
                    "type": "string",
                    "default": "0",
                    "description": "Expansion point x0 (default: '0').",
                },
                "m": {
                    "type": "integer",
                    "default": 3,
                    "description": "Numerator polynomial degree m >= 0.",
                },
                "n": {
                    "type": "integer",
                    "default": 3,
                    "description": "Denominator polynomial degree n >= 0.",
                },
            },
            "required": ["expr"],
        },
    },
    {
        "name": "wolfram_reset_session",
        "description": "Reset the persistent Mathics3 Wolfram Language session, clearing all user definitions.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


class MathicsMCPServer:
    """Persistent Mathics3 MCP Server handling JSON-RPC 2.0 tool requests."""

    def __init__(self) -> None:
        self._session: Optional[MathicsSession] = None

    @property
    def session(self) -> MathicsSession:
        if self._session is None:
            self._session = MathicsSession()
            load_default_settings_files(self._session.definitions)
        return self._session

    def reset_session(self) -> None:
        self._session = MathicsSession()
        load_default_settings_files(self._session.definitions)

    def eval_wl(self, code: str, include_tex: bool = True) -> Dict[str, Any]:
        res = self.session.evaluate_as_in_cli(code)
        out_msgs = [str(getattr(m, "text", m)) for m in (res.out or [])]
        payload: Dict[str, Any] = {
            "input": code,
            "result": res.result,
            "messages": out_msgs,
            "line_no": res.line_no,
        }
        if include_tex and res.result is not None and res.result != "Null":
            try:
                tex_res = self.session.evaluate_as_in_cli(f"TeXForm[{res.result}]")
                payload["tex"] = tex_res.result
            except Exception:
                payload["tex"] = None
        return payload

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "wolfram_eval":
            code = str(arguments["code"])
            include_tex = bool(arguments.get("include_tex", True))
            return self.eval_wl(code, include_tex=include_tex)

        if name == "wolfram_integrate":
            expr = str(arguments["expr"])
            var = str(arguments.get("var", "x"))
            lower = arguments.get("lower")
            upper = arguments.get("upper")
            prec = arguments.get("numeric_precision")

            if lower is not None and upper is not None:
                wl_cmd = f"Integrate[{expr}, {{{var}, {lower}, {upper}}}]"
            else:
                wl_cmd = f"Integrate[{expr}, {var}]"

            out = self.eval_wl(wl_cmd, include_tex=True)
            if prec is not None and int(prec) >= 2 and out.get("result"):
                n_digits = int(prec)
                n_res = self.session.evaluate_as_in_cli(
                    f"N[{out['result']}, {n_digits}]"
                )
                out["numeric_value"] = n_res.result
                out["numeric_precision"] = n_digits
            return out

        if name == "wolfram_contour_integrate":
            expr = str(arguments["expr"])
            var = str(arguments.get("var", "z"))
            center = str(arguments.get("center", "0"))
            radius = str(arguments.get("radius", "1"))
            wl_cmd = f"ContourIntegrate[{expr}, {{{var}, {center}, {radius}}}]"
            return self.eval_wl(wl_cmd, include_tex=True)

        if name == "wolfram_residue":
            expr = str(arguments["expr"])
            var = str(arguments.get("var", "z"))
            pole = str(arguments["pole"])
            wl_cmd = f"Residue[{expr}, {{{var}, {pole}}}]"
            return self.eval_wl(wl_cmd, include_tex=True)

        if name == "wolfram_pade_approximant":
            expr = str(arguments["expr"])
            var = str(arguments.get("var", "x"))
            x0 = str(arguments.get("x0", "0"))
            m = int(arguments.get("m", 3))
            n = int(arguments.get("n", 3))
            wl_cmd = f"PadeApproximant[{expr}, {{{var}, {x0}, {{{m}, {n}}}}}]"
            return self.eval_wl(wl_cmd, include_tex=True)

        if name == "wolfram_reset_session":
            self.reset_session()
            return {"status": "reset", "message": "Mathics3 session reset."}

        raise ValueError(f"Unknown MCP tool: {name!r}")

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}

        # Notifications have no id and expect no response
        if req_id is None:
            return None

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "version": __version__,
                        },
                    },
                }

            if method == "ping":
                return {"jsonrpc": "2.0", "id": req_id, "result": {}}

            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS_SPEC},
                }

            if method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments") or {}
                payload = self.call_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(payload, ensure_ascii=False, indent=2),
                            }
                        ],
                        "isError": False,
                    },
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "error": str(exc),
                                    "traceback": traceback.format_exc(limit=6),
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ],
                    "isError": True,
                },
            }


def main() -> int:
    """Run the Mathics3 MCP Server over stdin/stdout (newline-delimited JSON-RPC 2.0)."""
    server = MathicsMCPServer()
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith("content-length:"):
            # Support LSP-style Content-Length framing if used by client
            length = int(line.split(":", 1)[1].strip())
            # consume blank header separator line
            sys.stdin.readline()
            body = sys.stdin.read(length)
            req = json.loads(body)
            resp = server.handle_request(req)
            if resp is not None:
                out_bytes = json.dumps(resp, ensure_ascii=False).encode("utf-8")
                sys.stdout.write(f"Content-Length: {len(out_bytes)}\r\n\r\n")
                sys.stdout.write(out_bytes.decode("utf-8"))
                sys.stdout.flush()
            continue

        req = json.loads(line)
        resp = server.handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
