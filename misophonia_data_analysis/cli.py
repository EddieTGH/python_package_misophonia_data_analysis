r"""Title: Process Sound Task Raw Data From Qualtrics

Examples
--------
run_miso -s 1001
run_miso -s 1023
run_miso --raw-data-path ../../input_data/raw_data/miso_raw_data_9.csv -s 1001
run_miso --mapping-data-path ../../input_data/mapping/miso_mapping_sounds_1.csv -s 1001
run_miso --raw-data-path ../../input_data/raw_data/miso_raw_data_9.csv --mapping-data-path ../../input_data/mapping/miso_mapping_sounds_1.csv -s 1001

"""

# %%
import os
import sys
import time
import textwrap
import platform
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter

try:
    from misophonia_data_analysis import SoundDataAnalysis
    import misophonia_data_analysis._version as ver
except ImportError:
    import SoundDataAnalysis
    import misophonia_data_analysis._version as ver
    
# %%
def _get_args():
    """Get and parse arguments."""
    ver_info = f"\nVersion : {ver.__version__}\n\n"
    parser = ArgumentParser(
        description=ver_info + __doc__,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--raw-data-path",
        type=str,
        default="../../input_data/raw_data/miso_raw_data_13.csv",
        help=textwrap.dedent(
            """\
            (default : %(default)s)
            """
        ),
    )

    parser.add_argument(
        "--mapping-data-path",
        type=str,
        default="../../input_data/mapping/miso_mapping_sounds_2.csv",
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