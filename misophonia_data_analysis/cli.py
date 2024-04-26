r"""Title: Process Sound Task Raw Data From Qualtrics

Utilize this script to process raw data from 'pre' and 'post' sound tasks...
'pre' refers to data acquired from the initial sound task
'post' refers to data acquired from the follow-up sound task

'Pre' Setup:
------
1. Ensure that the raw data file is in the correct location:
- The raw data file should be named as 'miso_raw_{subject_number}.csv'
- The raw data file should be placed in the 'input_data/raw_data' folder

2. Ensure that the mapping data file is in the correct location:
- The mapping data file should be named as 'miso_mapping_{subject_number}.csv'
- The mapping data file should be placed in the 'input_data/mapping' folder

3. Ensure that the output_data folder exists in the root directory


'Post' Setup:
------
1. Ensure that 'pre' data analysis has already been run (output files generated).
- This should ensure that the mapping data file is available for the 'post' data analysis

2. Ensure that the raw data file is in the correct location:
- The raw data file should be named as 'miso_raw_post_{subject_number}.csv'
- The raw data file should be placed in the 'input_data/raw_post_data' folder

3. Ensure that the output_data folder exists in the root directory

Examples
--------
run_miso -s 1001 -t pre
run_miso -s 1001 -t post
run_miso -s 1023 -t pre
run_miso -s 1001 -t post

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

    required_args.add_argument(
        "-t",
        help="Type of processing: 'pre' for initial sound task or 'post' for follow-up task",
        type=str,
        required=True,
        dest="type_processing"
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
    type_processing = args.type_processing
    raw_data_path = f"../../input_data/raw_data/miso_raw_{subjN}.csv"
    mapping_data_path = f"../../input_data/mapping/miso_mapping_{subjN}.csv"

    post_data_path = f"../../input_data/raw_post_data/miso_raw_post_{subjN}.csv"
    #post_data_path = f"../../input_data/raw_post_data/miso_raw_post_25.csv"

    post_mapping_data_path = f"../../output_data/subject_{subjN}/subject_{subjN}_follow_up_mapping.csv"
    #post_mapping_data_path = f"../../output_data/subject_25/subject_25_follow_up_mapping.csv"


    # Check if the subject_number is an integer
    try:
        args.subject_number = int(args.subject_number)
    except ValueError:
        print("Subject ID must be an integer")
        sys.exit(1)

    if type_processing == 'pre':
        #make sure file exists in the right location
        # Check if the raw data file exists at the given path
        if not os.path.exists(raw_data_path):
            raw_data_path = raw_data_path[3:]

        if not os.path.exists(raw_data_path):
            print(f"Error: The 'pre' raw data file does not exist at {raw_data_path}", file=sys.stderr)
            sys.exit(1)  # Exit the program with an error code

        if not os.path.exists(mapping_data_path):
            mapping_data_path = mapping_data_path[3:]

        # Check if the mapping data file exists at the given path
        if not os.path.exists(mapping_data_path):
            print(f"Error: The 'pre' mapping data file does not exist at {mapping_data_path}", file=sys.stderr)
            sys.exit(1)  # Exit the program with an error code

        # If the code execution reaches this point, it means both files exist and the program can proceed
        SoundDataAnalysis.proc_data(subjN, raw_data_path, mapping_data_path, type_processing)

    elif type_processing == 'post':
        #make sure file exists in the right location
        # Check if the raw data file exists at the given path
        if not os.path.exists(post_data_path):
            post_data_path = post_data_path[3:]

        if not os.path.exists(post_data_path):
            print(f"Error: The post raw data file does not exist at {post_data_path}", file=sys.stderr)
            sys.exit(1)
        
        if not os.path.exists(post_mapping_data_path):
            post_mapping_data_path = post_mapping_data_path[3:]

        # Check if the mapping data file exists at the given path
        if not os.path.exists(post_mapping_data_path):
            print(f"Error: The post mapping data file does not exist at {post_mapping_data_path}. Please make sure to run 'pre' data processing first.", file=sys.stderr)
            sys.exit(1)
        
        # If the code execution reaches this point, it means both files exist and the program can proceed
        SoundDataAnalysis.proc_data(subjN, post_data_path, post_mapping_data_path, type_processing)
    
    else:
        print("Invalid type of processing. Please enter 'pre' or 'post'")
        sys.exit(1)

if __name__ == "__main__":
    main()

# %%