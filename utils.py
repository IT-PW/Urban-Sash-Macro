import os
import re

def categorize_files(files):
    frame_skipped = []
    invalid_files = []
    existing_sh = []
    valid_files = []

    for file_path in files:
        base_name = os.path.basename(file_path)
        job_id, ext = os.path.splitext(base_name)

        if not ext.lower() == '.txt':
            continue

        if re.search(r"-\d+\.txt$", base_name):
            frame_skipped.append(job_id)
            continue

        if "-SH" in job_id or base_name.endswith(".ORI"):
            invalid_files.append(base_name)
            continue

        output_dir = os.path.dirname(os.path.dirname(file_path))
        expected_sash_path = os.path.join(output_dir, f"{job_id}-SH.txt")
        if os.path.exists(expected_sash_path):
            existing_sh.append(job_id)

        valid_files.append(file_path)

    return frame_skipped, invalid_files, existing_sh, valid_files
