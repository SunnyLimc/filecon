import queue

import pytest

import filecon


@pytest.mark.parametrize(
    "ext, expect",
    [
        ("rs", filecon.comment_pattern.__slash_like),
        ("yml", filecon.comment_pattern.__hash_like),
    ],
)
def test_ext_pattern_match(ext, expect):
    assert (
        filecon.code_comment_patterns.get(ext) == expect
        or filecon.document_comment_patterns.get(ext) == expect
    )


@pytest.mark.parametrize(
    "inc, exc, expect",
    [
        (
            [f"files/{n}" for n in ["**/*"]],
            [f"files/{n}" for n in ["**/ex/1.js"]],
            [f"files/{n}" for n in ["1.yaml", "2.ts", "in/1.toml"]],
        ),
    ],
)
def test_filter_file(inc, exc, expect):
    assert filecon.filter_files(inc, exc) == expect


@pytest.mark.parametrize(
    "path, sed, ok_path",
    [
        ("files/2.ts", filecon.code_comment_patterns.get("ts"), "files_ok/2.ts"),
    ],
)
def test_file_processing(path, sed, ok_path):
    test_queue = queue.Queue()
    filecon.process_file(path, [sed], test_queue)
    with open(ok_path, "r") as ok:
        assert [item.strip("\n") for item in list(test_queue.queue)] == [ok.read()]


@pytest.mark.parametrize(
    "f_path, ncc, ndc, f_rule, expect",
    [
        (
            "2.ts",
            1,  # ncc
            0,  # ndc
            (["**/*.yaml", "^\s*#"],),
            [
                filecon.code_comment_patterns.get("ts"),
            ],
        ),
        (
            "files/1.yaml",
            1,  # ncc
            0,  # ndc
            (
                [
                    "**/*.yaml",
                    "^\s*#",
                ],
            ),
            [r"^\s*#"],
        ),
    ],
)
def test_sed_generator(f_path, ncc, ndc, f_rule, expect):
    assert filecon.generate_sed_commands(f_path, ncc, ndc, f_rule) == expect
