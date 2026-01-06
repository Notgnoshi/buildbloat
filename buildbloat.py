#!/usr/bin/env python3
"""Convert Ninja build logs to webtreemap input format."""

import argparse
import io
import logging
import os
import sys
from typing import Dict, Iterable, Optional, Tuple


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging output level. Defaults to INFO.",
    )
    parser.add_argument("--build-dir", "-b", type=str, help="Path to the build directory")
    group = parser.add_argument_group()
    group.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Script input. Defaults to stdin.",
    )
    group.add_argument(
        "output",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Script output. Defaults to stdout.",
    )

    return parser.parse_args()


def parse_ninja_log(log: io.TextIOWrapper) -> Iterable[Tuple[int, int, int, str, str]]:
    """Parse a Ninja build log v5 logs and yield entries one-by-one.

    See: https://pkg.go.dev/go.fuchsia.dev/fuchsia/tools/build/ninjago/ninjalog for the log format.

        # ninja log v5
        <start>	<end>	<restat>	<target>	<cmdhash>

    (separated by tabs)
    """
    for line in log:
        if line.startswith("#"):
            continue
        parts = line.strip().split("\t")
        if len(parts) != 5:
            # Tab in the filename??
            logging.error("Failed to parse: '%s'", line)
            continue
        start, end, restat, target, cmdhash = parts
        yield int(start), int(end), int(restat), target, cmdhash


def calculate_build_durations(
    entries: Iterable[Tuple[int, int, int, str, str]],
    build_dir: Optional[str] = None,
) -> Dict[str, int]:
    """Calculate build durations for each entry, summing together any duplicate filenames."""
    durations: Dict[str, int] = {}

    for start, end, _restat, target, _cmdhash in entries:
        # If a build directory is given, rewrite any absolute paths to be relative to the build
        # directory. Nominally, Ninja logs should only reference paths in the build directory, but
        # I've seen cases where absolute paths (in the build directory) sneak in.
        if build_dir and target.startswith("/"):
            target = os.path.relpath(target, build_dir)
        duration = end - start
        duration = duration / 1000  # ms -> s
        if target in durations:
            durations[target] += duration
        else:
            durations[target] = duration

    return durations


def output_du_format(output: io.TextIOWrapper, entries: Dict[str, int]):
    """Output entries in a du-like format."""
    for target, duration in entries.items():
        output.write(f"{duration}\t{target}\n")


def main(args):
    entries = parse_ninja_log(args.input)
    entries = calculate_build_durations(entries, args.build_dir)
    output_du_format(args.output, entries)


if __name__ == "__main__":
    args = parse_args()
    fmt = "%(asctime)s %(module)s %(levelname)s: %(message)s"
    logging.basicConfig(
        format=fmt,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=args.log_level,
        stream=sys.stderr,
    )
    # Color log output if possible, because I'm a sucker
    try:
        import coloredlogs

        coloredlogs.install(fmt=fmt, level=args.log_level, datefmt="%Y-%m-%dT%H:%M:%S%z")
    except ImportError:
        pass
    main(args)
