import argparse
import glob
import multiprocessing
import os
import shutil
import subprocess
import tempfile

from .comment_pattern import code_comment_patterns, document_comment_patterns


def is_sed_available():
    try:
        subprocess.run(
            ["sed", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        return False


def filter_files(include_patterns, exclude_patterns):
    included_files = [
        f
        for pattern in include_patterns
        for f in glob.glob(pattern, recursive=True)
        if not os.path.isdir(f)
    ]
    excluded_files = [
        f
        for pattern in exclude_patterns
        for f in glob.glob(pattern, recursive=True)
        if not os.path.isdir(f)
    ]
    files_to_process = [f for f in included_files if f not in excluded_files]
    return files_to_process


def process_file(file_path, sed_commands, output_queue):
    file_content = f"---start of file: {file_path}---\n"
    if sed_commands:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            tmp_file_name = tmp_file.name
            shutil.copy(file_path, tmp_file_name)
            for sed_command in sed_commands:
                subprocess.run(["sed", "-i", sed_command, tmp_file_name], check=True)
            with open(tmp_file_name, "r") as content_file:
                file_content += content_file.read()
            os.remove(tmp_file_name)
    else:
        with open(file_path, "r") as content_file:
            file_content += content_file.read()
    file_content+=f"---end of file: {file_path}---\n\n"

    output_queue.put(file_content)


def generate_sed_commands(file_path, no_code_comment, no_doc_comment, file_sed_rules):
    sed_commands = []

    file_ext = os.path.splitext(file_path)[1][1:]
    if no_code_comment:
        sed_commands.extend(filter(None, [code_comment_patterns.get(file_ext)]))
    if no_doc_comment:
        sed_commands.extend(filter(None, [document_comment_patterns.get(file_ext)]))

    sed_commands.extend(
        sed_command
        for file_regex, sed_command in file_sed_rules
        if file_path in glob.glob(file_regex)
    )

    return sed_commands


def concatenate_files(
    include_patterns,
    exclude_patterns,
    output_file,
    file_sed_rules,
    no_code_comment,
    no_doc_comment,
):
    if not is_sed_available():
        print("sed is not available in the system path.")
        return

    output_file = os.path.abspath(output_file)
    files_to_process = filter_files(
        [item[0] for item in include_patterns], [item[0] for item in exclude_patterns]
    )

    output_queue = multiprocessing.Manager().Queue()
    processes = []

    for file_path in files_to_process:
        sed_commands = generate_sed_commands(
            file_path, no_code_comment, no_doc_comment, file_sed_rules
        )

        p = multiprocessing.Process(
            target=process_file, args=(file_path, sed_commands, output_queue)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    with open(output_file, "w") as outfile:
        while not output_queue.empty():
            file_content = output_queue.get()
            outfile.write(file_content)


def main():
    parser = argparse.ArgumentParser(
        description="Concatenates specified files, optionally applying sed transformations or removing comments.",
        epilog='''Example usage:
python script.py -i '**/*.py' -e 'test_*.py' -ncc -frg '.py' 's/print/logging.info/' output.txt''',
    )
    parser.add_argument(
        "-i",
        "--include",
        nargs=1,
        action="append",
        required=True,
        help="Include files matching this pattern. Can be used multiple times for different patterns.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        nargs=1,
        action="append",
        help="Exclude files matching this pattern. Can be used multiple times for different patterns.",
    )
    parser.add_argument(
        "-fs",
        "--file-sed",
        nargs=2,
        action="append",
        help="Apply a sed command to files matching a regex. Format: '<regex>' '<sed command>'.",
    )
    parser.add_argument(
        "-ncc",
        "--no-code-comment",
        action="store_true",
        help="Automatically remove comments from common code files.",
    )
    parser.add_argument(
        "-ndc",
        "--no-doc-comment",
        action="store_true",
        help="Automatically remove comments from common documentation files.",
    )
    parser.add_argument("output_file", help="The final concatenated output file.")

    args = parser.parse_args()

    concatenate_files(
        args.include,
        args.exclude or [],
        args.output_file,
        args.file_sed or [],
        args.no_code_comment,
        args.no_doc_comment,
    )


if __name__ == "__main__":
    main()
