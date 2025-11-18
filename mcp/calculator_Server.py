
from __future__ import annotations

import ast
import operator
from typing import Callable, Mapping

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-mcp")


_SAFE_OPERATORS: Mapping[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Num):
        return float(node.n)
    if isinstance(node, ast.UnaryOp) and isinstance(
        node.op, (ast.UAdd, ast.USub)
    ):
        value = _eval_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _SAFE_OPERATORS[type(node.op)](left, right)
    detail = ast.dump(node, include_attributes=False)
    msg = f"Unsupported expression component: {detail}"
    raise ValueError(msg)


@mcp.tool()
def evaluate(expression: str) -> str:
    """Evaluate a Python-like math expression in a safe manner."""

    parsed = ast.parse(expression, mode="eval")
    result = _eval_node(parsed)
    return f"{expression} = {result:g}"


@mcp.tool()
def add(left: float, right: float) -> float:
    """Add two numbers."""

    return left + right


@mcp.tool()
def multiply(left: float, right: float) -> float:
    """Multiply two numbers."""

    return left * right


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise ``base`` to ``exponent``."""

    return base**exponent


if __name__ == "__main__":
    mcp.run(transport="stdio")
