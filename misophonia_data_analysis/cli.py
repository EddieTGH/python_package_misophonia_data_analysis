r"""Title: Process Data

Examples
--------
python process_data.py -s 100123
"""

# %%
import os
import sys
import time
import textwrap
import platform
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter
import SoundDataAnalysis

# %%
def _get_args():
    """Get and parse arguments."""
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--raw-data-path",
        type=str,
        default="Raw Data/miso raw data 10.csv",
        help=textwrap.dedent(
            """\
            (default : %(default)s)
            """
        ),
    )

    parser.add_argument(
        "--mapping-data-path",
        type=str,
        default="Mapping/Misophonia Mapping Sounds 2.csv",
        help=textwrap.dedent(
            """\
            (default : %(default)s)
            """
        ),
    )

    required_args = parser.add_argument_group("Required Arguments")
    required_args.add_argument(
        "-s",
        help="Subject ID to submit for raw data processing",
        type=str,
        required=True,
        dest="subject_number"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    return parser


# %%
def main():
    """Orient to user input and trigger workflow."""

    # Capture CLI arguments
    args = _get_args().parse_args()
    subjN = args.subject_number
    raw_data_path = args.raw_data_path
    mapping_data_path = args.mapping_data_path

    SoundDataAnalysis.proc_data(subjN, raw_data_path, mapping_data_path)

    #make sure file exists in the right location, make sure the subject number is available


if __name__ == "__main__":
    main()

# %%