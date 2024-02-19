import sys
import os
import logging

from pathlib import Path

from . import (
    builder,
    cli,  # noqa: F401 this is imported for side effects
    const,
    model,
    plugins,
    pods,  # noqa: F401 this is imported for side effects
    shell,
    vt100,
)


def ensure(version: tuple[int, int, int]):
    if (
        const.VERSION[0] == version[0]
        and const.VERSION[1] == version[1]
        and const.VERSION[2] >= version[2]
    ):
        return

    raise RuntimeError(
        f"Expected cutekit version {version[0]}.{version[1]}.{version[2]} but found {const.VERSION_STR}"
    )


class logger:
    class LoggerArgs:
        verbose: bool = cli.arg(None, "verbose", "Enable verbose logging")

    @staticmethod
    def setup(args: LoggerArgs):
        if args.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format=f"{vt100.CYAN}%(asctime)s{vt100.RESET} {vt100.YELLOW}%(levelname)s{vt100.RESET} %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            projectRoot = model.Project.topmost()
            logFile = const.GLOBAL_LOG_FILE
            if projectRoot is not None:
                logFile = os.path.join(projectRoot.dirname(), const.PROJECT_LOG_FILE)

            shell.mkdir(os.path.dirname(logFile))

            logging.basicConfig(
                level=logging.INFO,
                filename=logFile,
                filemode="w",
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )


class RootArgs(
    plugins.PluginsArgs,
    pods.PodSetupArgs,
    logger.LoggerArgs,
):
    pass


@cli.command(None, "/", const.DESCRIPTION)
def _(args: RootArgs):
    const.setup()
    logger.setup(args)
    plugins.setup(args)
    pods.setup(args)


@cli.command("u", "usage", "Show usage information")
def _():
    print(f"Usage: {const.ARGV0} {cli._root.usage()}")


@cli.command("v", "version", "Show current version")
def _():
    print(f"CuteKit v{const.VERSION_STR}")


def main() -> int:
    try:
        shell.mkdir(const.GLOBAL_CK_DIR)
        extra = os.environ.get("CK_EXTRA_ARGS", None)
        args = [const.ARGV0] + (extra.split(" ") if extra else []) + sys.argv[1:]
        cli._root.eval(args)
        return 0

    except RuntimeError as e:
        logging.exception(e)
        vt100.error(str(e))
        return 1

    except KeyboardInterrupt:
        print()
        return 1
