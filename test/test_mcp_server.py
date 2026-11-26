# -*- coding: utf-8 -*-
"""
Unit tests for the Mathics3 Wolfram Language MCP Server (`mathics.mcp_server`).
"""

import json
from mathics.mcp_server import MathicsMCPServer


def test_mcp_initialize_and_tools_list() -> None:
    server = MathicsMCPServer()

    init_resp = server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    )
    assert init_resp is not None
    assert init_resp["id"] == 1
    assert init_resp["result"]["serverInfo"]["name"] == "mathics3-mcp"

    tools_resp = server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    )
    assert tools_resp is not None
    tool_names = {t["name"] for t in tools_resp["result"]["tools"]}
    assert {
        "wolfram_eval",
        "wolfram_integrate",
        "wolfram_contour_integrate",
        "wolfram_residue",
        "wolfram_pade_approximant",
        "wolfram_reset_session",
    }.issubset(tool_names)


def test_mcp_tools_call_calculus_and_arbitrary_precision() -> None:
    server = MathicsMCPServer()

    # 1. Improper Fresnel integral with 60-digit precision
    int_resp = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "wolfram_integrate",
                "arguments": {
                    "expr": "Sin[x^2]",
                    "var": "x",
                    "lower": "0",
                    "upper": "Infinity",
                    "numeric_precision": 60,
                },
            },
        }
    )
    assert int_resp is not None
    assert not int_resp["result"]["isError"]
    payload = json.loads(int_resp["result"]["content"][0]["text"])
    assert payload["result"] == "Sqrt[2] Sqrt[Pi] / 4"
    assert payload["numeric_value"].startswith(
        "0.62665706865775012560394132120276131325174668515248457915748"
    )

    # 2. ContourIntegrate tool on P^1(C)
    cnt_resp = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "wolfram_contour_integrate",
                "arguments": {
                    "expr": "1 / (1 + z^4)",
                    "var": "z",
                    "center": "I",
                    "radius": "1",
                },
            },
        }
    )
    assert cnt_resp is not None
    cnt_payload = json.loads(cnt_resp["result"]["content"][0]["text"])
    assert cnt_payload["result"] == "Sqrt[2] Pi / 2"

    # 3. Residue tool at Infinity
    res_resp = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "wolfram_residue",
                "arguments": {
                    "expr": "1 / z",
                    "var": "z",
                    "pole": "Infinity",
                },
            },
        }
    )
    assert res_resp is not None
    res_payload = json.loads(res_resp["result"]["content"][0]["text"])
    assert res_payload["result"] == "-1"

    # 4. PadeApproximant tool
    pade_resp = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "wolfram_pade_approximant",
                "arguments": {
                    "expr": "Exp[x]",
                    "var": "x",
                    "x0": "0",
                    "m": 2,
                    "n": 2,
                },
            },
        }
    )
    assert pade_resp is not None
    pade_payload = json.loads(pade_resp["result"]["content"][0]["text"])
    assert pade_payload["result"] == "(12 + 6 x + x ^ 2) / (12 - 6 x + x ^ 2)"
