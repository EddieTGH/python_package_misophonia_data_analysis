r"""Title: Process Sound Task Raw Data From Qualtrics

Setup:
------
1. Ensure that the raw data file is in the correct location:
- The raw data file should be named as 'miso_raw_{subject_number}.csv'
- The raw data file should be placed in the 'input_data/raw_data' folder

2. Ensure that the mapping data file is in the correct location:
- The mapping data file should be named as 'miso_mapping_{subject_number}.csv'
- The mapping data file should be placed in the 'input_data/mapping' folder

3. Ensure that the output_data folder exists in the root directory

Examples
--------
run_miso -s 1001
run_miso -s 1023

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
    import _version as ver
    
# %%
def _get_args():
    """Get and parse arguments."""
    ver_info = f"\nVersion : {ver.__version__}\n\n"
    parser = ArgumentParser(
        description=ver_info + __doc__,
        formatter_class=RawTextHelpFormatter,
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
    raw_data_path = f"../../input_data/raw_data/miso_raw_{subjN}.csv"
    mapping_data_path = f"../../input_data/mapping/miso_mapping_{subjN}.csv"

    # Check if the subject_number is an integer
    try:
        args.subject_number = int(args.subject_number)
    except ValueError:
        print("Subject ID must be an integer")
        sys.exit(1)


    #make sure file exists in the right location
    # Check if the raw data file exists at the given path
    if not os.path.exists(raw_data_path):
        raw_data_path = raw_data_path[3:]

    if not os.path.exists(raw_data_path):
        print(f"Error: The raw data file does not exist at {raw_data_path}", file=sys.stderr)
        sys.exit(1)  # Exit the program with an error code

    if not os.path.exists(mapping_data_path):
        mapping_data_path = mapping_data_path[3:]
        
    # Check if the mapping data file exists at the given path
    if not os.path.exists(mapping_data_path):
        print(f"Error: The mapping data file does not exist at {mapping_data_path}", file=sys.stderr)
        sys.exit(1)  # Exit the program with an error code

    # If the code execution reaches this point, it means both files exist and the program can proceed
    SoundDataAnalysis.proc_data(subjN, raw_data_path, mapping_data_path)

if __name__ == "__main__":
    main()

# %%