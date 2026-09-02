from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from postulate.models import PostulateSpec

SUPPORTED_POLICIES = frozenset({"unit_tests_stay_offline", "no_secrets_in_output"})

NETWORK_MODULES = frozenset({"httpx", "requests"})
SANITIZER_PATTERN = re.compile(
    r"sanitize|redact|mask|scrub|assert_safe|anonymize",
    re.IGNORECASE,
)
SECRET_PREFIXES = ("sk-", "pk_", "AKIA", "Bearer ", "api_key")


@dataclass
class PolicyCheckResult:
    warnings: list[str]
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def check_policies(spec: PostulateSpec, project_root: Path) -> PolicyCheckResult:
    warnings: list[str] = []
    project_root = project_root.resolve()
    tests_dir = project_root / "tests"

    for policy in spec.policies:
        if policy == "unit_tests_stay_offline":
            warnings.extend(_check_unit_tests_stay_offline(tests_dir))
        elif policy == "no_secrets_in_output":
            warnings.extend(_check_no_secrets_in_output(tests_dir))

    return PolicyCheckResult(warnings=warnings, errors=[])


def apply_fail_on_warnings(result: PolicyCheckResult) -> PolicyCheckResult:
    if not result.warnings:
        return result
    return PolicyCheckResult(
        warnings=result.warnings,
        errors=[f"[policy] {message}" for message in result.warnings],
    )


def _iter_test_python_files(tests_dir: Path) -> list[Path]:
    if not tests_dir.is_dir():
        return []
    return sorted(tests_dir.rglob("*.py"))


def _check_unit_tests_stay_offline(tests_dir: Path) -> list[str]:
    violations: list[str] = []
    for path in _iter_test_python_files(tests_dir):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError):
            continue

        checker = _OfflineTestVisitor()
        checker.visit(tree)
        if checker.uses_network_client and not (
            checker.has_respx or checker.has_monkeypatch
        ):
            rel = _display_path(path, tests_dir)
            modules = ", ".join(sorted(checker.network_modules))
            violations.append(
                f"unit_tests_stay_offline: {rel} uses {modules} without "
                "respx or monkeypatch patterns"
            )
    return violations


def _check_no_secrets_in_output(tests_dir: Path) -> list[str]:
    violations: list[str] = []
    for path in _iter_test_python_files(tests_dir):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError):
            continue

        checker = _SecretsInAssertVisitor(path)
        checker.visit(tree)
        violations.extend(checker.violations)
    return violations


def _display_path(path: Path, tests_dir: Path) -> str:
    try:
        return path.relative_to(tests_dir.parent).as_posix()
    except ValueError:
        return path.as_posix()


class _OfflineTestVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.network_modules: set[str] = set()
        self.has_respx = False
        self.has_monkeypatch = False

    @property
    def uses_network_client(self) -> bool:
        return bool(self.network_modules)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root in NETWORK_MODULES:
                self.network_modules.add(root)
            if root == "respx":
                self.has_respx = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            root = node.module.split(".", 1)[0]
            if root in NETWORK_MODULES:
                self.network_modules.add(root)
            if root == "respx":
                self.has_respx = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg == "monkeypatch":
                self.has_monkeypatch = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg == "monkeypatch":
                self.has_monkeypatch = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in NETWORK_MODULES:
                    self.network_modules.add(node.func.value.id)
                if (
                    node.func.value.id == "monkeypatch"
                    and node.func.attr == "setattr"
                ):
                    self.has_monkeypatch = True
        elif isinstance(node.func, ast.Name) and node.func.id in NETWORK_MODULES:
            self.network_modules.add(node.func.id)
        self.generic_visit(node)


class _SecretsInAssertVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.violations: list[str] = []

    def visit_Assert(self, node: ast.Assert) -> None:
        if _assert_contains_secret_literal(node.test):
            rel = self.path.as_posix()
            self.violations.append(
                f"no_secrets_in_output: {rel}:{node.lineno} assertion embeds "
                "a secret-like literal without a sanitizer"
            )
        self.generic_visit(node)


def _assert_contains_secret_literal(node: ast.AST) -> bool:
    if isinstance(node, ast.Assert):
        return _assert_contains_secret_literal(node.test)
    if _node_has_sanitizer(node):
        return False
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _is_secret_like(node.value)
    if isinstance(node, ast.Compare):
        return any(_assert_contains_secret_literal(operand) for operand in node.comparators)
    if isinstance(node, ast.BoolOp):
        return any(_assert_contains_secret_literal(value) for value in node.values)
    if isinstance(node, ast.UnaryOp):
        return _assert_contains_secret_literal(node.operand)
    if isinstance(node, ast.BinOp):
        return _assert_contains_secret_literal(node.left) or _assert_contains_secret_literal(
            node.right
        )
    if isinstance(node, ast.Call):
        if _node_has_sanitizer(node):
            return False
        return any(_assert_contains_secret_literal(arg) for arg in node.args)
    return False


def _node_has_sanitizer(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        name = _call_name(node.func)
        if name and SANITIZER_PATTERN.search(name):
            return True
    if isinstance(node, ast.Name) and SANITIZER_PATTERN.search(node.id):
        return True
    if isinstance(node, ast.Attribute) and SANITIZER_PATTERN.search(node.attr):
        return True
    return False


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_secret_like(value: str) -> bool:
    if len(value) < 16:
        return False
    if any(value.startswith(prefix) for prefix in SECRET_PREFIXES):
        return True
    if len(value) >= 20 and re.fullmatch(r"[A-Za-z0-9_\-+/=]+", value):
        return len(set(value)) > 10
    lowered = value.lower()
    if any(token in lowered for token in ("password", "secret", "token", "apikey")):
        return True
    return False


def print_policy_check_result(result: PolicyCheckResult) -> None:
    for message in result.warnings:
        print(f"! {message}")
    for message in result.errors:
        print(f"✗ {message}")
    if result.ok and not result.warnings:
        print("✓ postulate policies check passed")
    elif result.ok:
        print("✓ postulate policies check passed (with warnings)")
    else:
        count = len(result.errors)
        suffix = "" if count == 1 else "s"
        print(f"✗ postulate policies check failed ({count} error{suffix})")
