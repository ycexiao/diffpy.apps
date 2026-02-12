import argparse

from diffpy.apps.version import __version__  # noqa


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy.apps",
        description=(
            "User applications to help with tasks using diffpy packages\n\n"
            "For more information, visit: "
            "https://github.com/diffpy/diffpy.apps/"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the program's version number and exit",
    )

    args = parser.parse_args()

    if args.version:
        print(f"diffpy.apps {__version__}")
    else:
        # Default behavior when no arguments are given
        parser.print_help()


if __name__ == "__main__":
    main()
