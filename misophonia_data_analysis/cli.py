r"""Title: Process Sound Task Raw Data From Qualtrics (for BIAC/munin)

Utilize this script to process raw data from intake and follow up sound tasks...
'intake' refers to data acquired from the initial sound task
'fu_1month' refers to data acquired from the 1 month follow-up sound task
'fu_3month' refers to data acquired from the 3 month follow-up sound task

'Intake' Setup:
------
1. Ensure that the raw data file is in the correct location:
- The Qualtrics intake raw data file should be named as 'raw_qualtrics_intake_{subjN}.csv'
- The Qualtrics intake raw data file should be placed in the 'data/task_sound/raw_intake' folder

2. Ensure that the mapping data file is in the correct location:
- The mapping intake data file should be named as 'mapping_intake_{subjN}.csv'
- The mapping intake data file should be placed in the 'data/task_sound/mapping_intake' folder


'fu_1month' Setup:
------
1. Ensure that intake data analysis has already been run (output files generated).
- This should ensure that the mapping data file is available for the follow up data analysis
- The mapping data file should be found in the 'data/task_sound/mapping_fu' folder
- The mapping data file should be named as 'subject_{subjN}_follow_up_mapping.csv'

2. Ensure that the Qualtrics fu raw data file is in the correct location:
- The Qualtrics fu raw data file should be named as 'raw_qualtrics_fu_1-month_{subjN}.csv'
- The Qualtrics fu raw data file should be placed in the 'data/task_sound/raw_fu_1-month' folder


'fu_3month' Setup:
------
1. Ensure that intake data analysis has already been run (output files generated).
- This should ensure that the mapping data file is available for the follow up data analysis
- The mapping data file should be found in the 'data/task_sound/mapping_fu' folder
- The mapping data file should be named as 'subject_{subjN}_follow_up_mapping.csv'

2. Ensure that the Qualtrics fu raw data file is in the correct location:
- The Qualtrics fu raw data file should be named as 'raw_qualtrics_fu_3-month_{subjN}.csv'
- The Qualtrics fu raw data file should be placed in the 'data/task_sound/raw_fu_3-month' folder

Examples
--------
python cli.py -s 1001 -t intake
python cli.py -s 1001 -t fu_1month
python cli.py -s 1001 -t fu_3month
python cli.py -s 1023 -t intake
python cli.py -s 1001 -t fu_1month
python cli.py -s 1001 -t fu_3month

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
        help="Type of processing: 'intake' for initial sound task or 'fu_1month' or 'fu_3month for follow-up task",
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

    task_sound_dir = "/mnt/munin/Neacsiu/MISOSTIM.01/Data/task_sound"
    raw_intake = task_sound_dir + f"/raw_intake/raw_qualtrics_intake_{subjN}.csv"
    mapping_intake = task_sound_dir + f"/mapping_intake/mapping_intake_{subjN}.csv"
    #raw_data_path = f"../../input_data/raw_data/miso_raw_{subjN}.csv"
    #mapping_data_path = f"../../input_data/mapping/miso_mapping_{subjN}.csv"

    raw_fu_1month = task_sound_dir + f"/raw_fu_1-month/raw_qualtrics_fu_1-month_{subjN}.csv"
    raw_fu_3month = task_sound_dir + f"/raw_fu_3-month/raw_qualtrics_fu_3-month_{subjN}.csv"
    mapping_fu = task_sound_dir + f"/mapping_fu/mapping_fu_{subjN}.csv"
    #post_data_path = f"../../input_data/raw_post_data/miso_raw_post_{subjN}.csv"
    #post_mapping_data_path = f"../../output_data/subject_{subjN}/subject_{subjN}_follow_up_mapping.csv"


    # Check if the subject_number is an integer
    try:
        args.subject_number = int(args.subject_number)
    except ValueError:
        print("Subject ID must be an integer")
        sys.exit(1)

    if type_processing == 'intake':
        #make sure file exists in the right location
        # Check if the raw data file exists at the given path
        if not os.path.exists(raw_intake):
            raw_intake = raw_intake[3:]

        if not os.path.exists(raw_intake):
            print(f"Error: The 'intake' raw data file does not exist at {raw_intake}", file=sys.stderr)
            sys.exit(1)  # Exit the program with an error code

        if not os.path.exists(mapping_intake):
            mapping_intake = mapping_intake[3:]

        # Check if the mapping data file exists at the given path
        if not os.path.exists(mapping_intake):
            print(f"Error: The 'intake' mapping data file does not exist at {mapping_intake}", file=sys.stderr)
            sys.exit(1)  # Exit the program with an error code

        # If the code execution reaches this point, it means both files exist and the program can proceed
        SoundDataAnalysis.proc_intake(subjN, raw_intake, mapping_intake)

    elif type_processing == 'fu_1month':
        #make sure file exists in the right location
        # Check if the raw data file exists at the given path
        if not os.path.exists(raw_fu_1month):
            raw_fu_1month = raw_fu_1month[3:]

        if not os.path.exists(raw_fu_1month):
            print(f"Error: The 1 month follow up Qualtrics raw data does not exist at {raw_fu_1month}", file=sys.stderr)
            sys.exit(1)
        
        if not os.path.exists(mapping_fu):
            mapping_fu = mapping_fu[3:]

        # Check if the mapping data file exists at the given path
        if not os.path.exists(mapping_fu):
            print(f"Error: The follow up mapping data file does not exist at {mapping_fu}. Please make sure to run intake data processing first.", file=sys.stderr)
            sys.exit(1)
        
        # If the code execution reaches this point, it means both files exist and the program can proceed
        SoundDataAnalysis.proc_fu_1month(subjN, raw_fu_1month, mapping_fu)
    
    elif type_processing == 'fu_3month':
        #make sure file exists in the right location
        # Check if the raw data file exists at the given path
        if not os.path.exists(raw_fu_3month):
            raw_fu_3month = raw_fu_3month[3:]

        if not os.path.exists(raw_fu_3month):
            print(f"Error: The 3 month follow up Qualtrics raw data does not exist at {raw_fu_3month}", file=sys.stderr)
            sys.exit(1)
        
        if not os.path.exists(mapping_fu):
            mapping_fu = mapping_fu[3:]

        # Check if the mapping data file exists at the given path
        if not os.path.exists(mapping_fu):
            print(f"Error: The follow up mapping data file does not exist at {mapping_fu}. Please make sure to run intake data processing first.", file=sys.stderr)
            sys.exit(1)
        
        # If the code execution reaches this point, it means both files exist and the program can proceed
        SoundDataAnalysis.proc_fu_3month(subjN, raw_fu_3month, mapping_fu)

    else:
        print("Invalid type of processing. Please enter 'intake', 'fu_1month' or 'fu_3month'.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# %%