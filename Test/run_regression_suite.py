"""
ATLAS General Regression Suite v0.1

ATLAS motorundaki unit ve gerçek saha regresyon testlerini
kategori bazında otomatik keşfeder ve çalıştırır.

Kullanım:

    PYTHONPATH=. python Test/run_regression_suite.py

Yalnızca belirli bir grup:

    PYTHONPATH=. python Test/run_regression_suite.py castles

Gelecekte desteklenecek gruplar:

    bridges
    dams
    districts
    water
    terrain
    buildings
    roads
    nature

Yeni bir test, uygun adlandırmayla Test klasörüne eklendiğinde
ilgili gruba otomatik olarak dahil edilir.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "Test"

SUITE_FILENAME = Path(__file__).name


GROUP_PATTERNS = {
    "castles": [
        "test_*castle*.py",
        "test_rumeli_*.py",
        "test_castle_*.py",
    ],
    "diagnostics": [
        "test_*sweep*.py",
        "test_*diagnostic*.py",
        "test_*reconstruction*.py",
    ],
    "bridges": [
        "test_*bridge*.py",
    ],
    "dams": [
        "test_*dam*.py",
    ],
    "districts": [
        "test_*district*.py",
        "test_*neighborhood*.py",
        "test_*mahalle*.py",
    ],
    "water": [
        "test_*water*.py",
        "test_*river*.py",
        "test_*lake*.py",
        "test_*coast*.py",
    ],
    "terrain": [
        "test_*terrain*.py",
        "test_*srtm*.py",
    ],
    "buildings": [
        "test_*building*.py",
    ],
    "roads": [
        "test_*road*.py",
        "test_*path*.py",
    ],
    "nature": [
        "test_*nature*.py",
        "test_*tree*.py",
        "test_*park*.py",
    ],
}


def discover_tests(group_name):
    patterns = GROUP_PATTERNS[group_name]
    discovered = {}

    for pattern in patterns:
        for test_path in TEST_ROOT.glob(pattern):
            if not test_path.is_file():
                continue

            if test_path.name == SUITE_FILENAME:
                continue
            if group_name != "diagnostics" and (
                "sweep" in test_path.name or "diagnostic" in test_path.name
            ):
                continue

            discovered[str(test_path.resolve())] = test_path

    return sorted(
        discovered.values(),
        key=lambda path: path.name.lower(),
    )


def discover_selected_tests(selected_groups):
    selected_tests = {}

    for group_name in selected_groups:
        for test_path in discover_tests(group_name):
            resolved_path = str(test_path.resolve())

            if resolved_path not in selected_tests:
                selected_tests[resolved_path] = {
                    "path": test_path,
                    "groups": [],
                }

            selected_tests[resolved_path]["groups"].append(group_name)

    return sorted(
        selected_tests.values(),
        key=lambda item: item["path"].name.lower(),
    )


def build_environment():
    environment = os.environ.copy()

    existing_pythonpath = environment.get(
        "PYTHONPATH",
        "",
    )

    pythonpath_parts = [
        str(PROJECT_ROOT),
    ]

    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)

    environment["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    environment["PYTHONWARNINGS"] = "error::RuntimeWarning"

    return environment


def run_test(test_record, environment):
    test_path = test_record["path"]
    groups = ", ".join(test_record["groups"])

    relative_path = test_path.relative_to(PROJECT_ROOT)

    print("")
    print("=" * 78)
    print(f"RUNNING : {relative_path}")
    print(f"GROUPS  : {groups}")
    print("=" * 78)

    started_at = time.perf_counter()

    result = subprocess.run(
        [
            sys.executable,
            str(relative_path),
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
    )

    elapsed_seconds = time.perf_counter() - started_at

    if result.returncode != 0:
        print("")
        print("=" * 78)
        print(f"FAILED  : {relative_path}")
        print(f"EXIT    : {result.returncode}")
        print(f"RUNTIME : " f"{elapsed_seconds:.2f} seconds")
        print("=" * 78)

        return False, elapsed_seconds

    print("")
    print("=" * 78)
    print(f"PASSED  : {relative_path}")
    print(f"RUNTIME : " f"{elapsed_seconds:.2f} seconds")
    print("=" * 78)

    return True, elapsed_seconds


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=("Run ATLAS regression tests by group.")
    )

    parser.add_argument(
        "groups",
        nargs="*",
        help=("Groups to run. " "Leave empty to run all groups."),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help=("List discovered tests without " "running them."),
    )

    return parser.parse_args()


def validate_groups(requested_groups):
    unknown_groups = [
        group_name
        for group_name in requested_groups
        if group_name not in GROUP_PATTERNS
    ]

    if unknown_groups:
        print("Unknown regression group(s): " + ", ".join(unknown_groups))
        print("Available groups: " + ", ".join(GROUP_PATTERNS))

        return False

    return True


def print_discovered_tests(
    selected_groups,
    selected_tests,
):
    print("")
    print("=" * 78)
    print("ATLAS REGRESSION TEST DISCOVERY")
    print("=" * 78)
    print("Selected groups : " + ", ".join(selected_groups))
    print(f"Discovered tests: " f"{len(selected_tests)}")
    print("-" * 78)

    for test_record in selected_tests:
        test_path = test_record["path"]
        groups = ", ".join(test_record["groups"])

        relative_path = test_path.relative_to(PROJECT_ROOT)

        print(f"{relative_path} " f"[{groups}]")

    print("=" * 78)
    print("")


def main():
    arguments = parse_arguments()

    selected_groups = arguments.groups if arguments.groups else list(GROUP_PATTERNS)

    if not validate_groups(selected_groups):
        return 2

    selected_tests = discover_selected_tests(selected_groups)

    print_discovered_tests(
        selected_groups=selected_groups,
        selected_tests=selected_tests,
    )

    if arguments.list:
        return 0

    if not selected_tests:
        print("No regression tests were found " "for the selected groups.")
        return 0

    environment = build_environment()

    passed_count = 0
    total_runtime = 0.0

    for test_record in selected_tests:
        success, elapsed_seconds = run_test(
            test_record=test_record,
            environment=environment,
        )

        total_runtime += elapsed_seconds

        if not success:
            print("")
            print("=" * 78)
            print("ATLAS REGRESSION SUITE STOPPED")
            print(f"Passed before failure: " f"{passed_count}")
            print(f"Failed test: " f"{test_record['path'].name}")
            print("=" * 78)

            return 1

        passed_count += 1

    print("")
    print("=" * 78)
    print("ATLAS REGRESSION SUITE PASSED")
    print(f"Passed test files : " f"{passed_count}")
    print(f"Total runtime     : " f"{total_runtime:.2f} seconds")
    print("=" * 78)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
