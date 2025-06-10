import unittest
from unittest.mock import patch, mock_open, call
from apply import extract_and_write_code_blocks

class TestExtractAndWriteCodeBlocks(unittest.TestCase):

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_single_valid_block_python_comment(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```python\n"
            "// path/to/file.py\n"
            "print(\"Hello\")\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file.py"
        expected_content = "print(\"Hello\")"

        mock_print.assert_any_call("Found 1 code block(s). Processing...")
        mock_print.assert_any_call(f"  Processing: {expected_filepath}")
        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with(expected_content)
        mock_print.assert_any_call(f"    Successfully wrote to {expected_filepath}")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_single_valid_block_hash_comment(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```bash\n"
            "# path/to/script.sh\n"
            "echo \"Hello\"\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/script.sh"
        expected_content = "echo \"Hello\""

        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with(expected_content)

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_single_valid_block_sql_comment(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```sql\n"
            "-- path/to/query.sql\n"
            "SELECT 1;\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/query.sql"
        expected_content = "SELECT 1;"

        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with(expected_content)

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_multiple_valid_blocks(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```python\n"
            "// path/to/file1.py\n"
            "print(1)\n"
            "```\n"
            "Some text in between\n"
            "```\n"
            "// another/file2.txt\n"
            "content2\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_print.assert_any_call("Found 2 code block(s). Processing...")
        mock_os_makedirs.assert_any_call("path/to", exist_ok=True)
        mock_os_makedirs.assert_any_call("another", exist_ok=True)
        self.assertEqual(mock_os_makedirs.call_count, 2)

        mock_file_open.assert_any_call("path/to/file1.py", 'w', encoding='utf-8')
        mock_file_open.assert_any_call("another/file2.txt", 'w', encoding='utf-8')
        self.assertEqual(mock_file_open.call_count, 2)

        handle_write_calls = mock_file_open().write.call_args_list
        self.assertIn(call("print(1)"), handle_write_calls)
        self.assertIn(call("content2"), handle_write_calls)

        mock_print.assert_any_call("    Successfully wrote to path/to/file1.py")
        mock_print.assert_any_call("    Successfully wrote to another/file2.txt")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_no_code_blocks_found(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = "This is just some text, no code blocks here."
        extract_and_write_code_blocks(input_text)

        mock_print.assert_called_once_with("No valid code blocks found.")
        mock_os_makedirs.assert_not_called()
        mock_file_open.assert_not_called()

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_empty_filepath_skipped(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// \n"
            "content\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_print.assert_any_call("Found 1 code block(s). Processing...")
        mock_print.assert_any_call("Warning: Found a code block with an empty filepath. Skipping.")
        mock_os_makedirs.assert_not_called()
        mock_file_open.assert_not_called()

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_path_normalization_windows_style(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// path\\to\\file.txt\n"
            "content\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file.txt"
        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with("content")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_top_level_file_no_directory_creation(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// top_level_file.txt\n"
            "Top level content\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_os_makedirs.assert_not_called()
        mock_file_open.assert_called_once_with("top_level_file.txt", 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with("Top level content")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_content_with_various_whitespaces(self, mock_file_open, mock_os_makedirs, mock_print):
        expected_content = (
            "  leading spaces\n"
            "middle line\n"
            "trailing spaces  \n"
            "\n"
            "  \t  tabs and spaces"
        )
        input_text = (
            "```\n"
            "// dir/complex_content.txt\n"
            f"{expected_content}\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_os_makedirs.assert_called_once_with("dir", exist_ok=True)
        mock_file_open.assert_called_once_with("dir/complex_content.txt", 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with(expected_content)

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_filepath_with_spaces_in_comment_line_handled_by_regex_and_strip(self, mock_file_open, mock_os_makedirs,
mock_print):
        input_text = (
            "```\n"
            "//   path/with/spaces.txt   \n"
            "content\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/with/spaces.txt"
        mock_os_makedirs.assert_called_once_with("path/with", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')

    @patch('builtins.print')
    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    @patch('builtins.open', new_callable=mock_open)
    def test_os_error_on_makedirs(self, mock_file_open, mock_os_makedirs_raising_error, mock_print):
        input_text = (
            "```\n"
            "// new_dir/file.txt\n"
            "content\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "new_dir/file.txt"
        mock_os_makedirs_raising_error.assert_called_once_with("new_dir", exist_ok=True)

        error_message_found = any(
            f"Error writing to {expected_filepath}: Permission denied" in args[0]
            for args, _ in mock_print.call_args_list if args
        )
        self.assertTrue(error_message_found, "Error message for makedirs failure not printed.")
        mock_file_open.assert_not_called()

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_os_error_on_file_write(self, mock_file_open, mock_os_makedirs, mock_print):
        mock_file_open.return_value.write.side_effect = OSError("Disk full")
        input_text = (
            "```\n"
            "// path/to/another.txt\n"
            "important data\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/another.txt"
        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with("important data")

        error_message_found = any(
            f"Error writing to {expected_filepath}: Disk full" in args[0]
            for args, _ in mock_print.call_args_list if args
        )
        self.assertTrue(error_message_found, "Error message for file write failure not printed.")

        success_message_found = any(
            f"Successfully wrote to {expected_filepath}" in args[0]
            for args, _ in mock_print.call_args_list if args
        )
        self.assertFalse(success_message_found, "Success message printed despite write error.")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_mixed_valid_and_empty_filepath_block(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// valid/file.txt\n"
            "valid content\n"
            "```\n"
            "```\n"
            "// \n"
            "ignored content\n"
            "```\n"
            "```python\n"
            "// another/valid.py\n"
            "pass\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_print.assert_any_call("Found 3 code block(s). Processing...")
        mock_print.assert_any_call("Warning: Found a code block with an empty filepath. Skipping.")

        self.assertEqual(mock_os_makedirs.call_count, 2)
        mock_os_makedirs.assert_any_call("valid", exist_ok=True)
        mock_os_makedirs.assert_any_call("another", exist_ok=True)

        self.assertEqual(mock_file_open.call_count, 2)
        mock_file_open.assert_any_call("valid/file.txt", 'w', encoding='utf-8')
        mock_file_open.assert_any_call("another/valid.py", 'w', encoding='utf-8')

        handle_write_calls = mock_file_open().write.call_args_list
        self.assertIn(call("valid content"), handle_write_calls)
        self.assertIn(call("pass"), handle_write_calls)
        self.assertNotIn(call("ignored content"), handle_write_calls)

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_block_with_empty_content(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// path/empty_file.txt\n"
            "\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/empty_file.txt"
        mock_os_makedirs.assert_called_once_with("path", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with("") # Empty content

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_content_containing_backticks_and_nested_fences(self, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// path/to/file_with_backticks.md\n"
            "This is a markdown file.\n"
            "It can contain `inline code` and also fenced code blocks:\n"
            "```python\n"
            "print('nested')\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file_with_backticks.md"
        expected_content = (
            "This is a markdown file.\n"
            "It can contain `inline code` and also fenced code blocks:\n"
            "```python\n"
            "print('nested')"
        )
        mock_os_makedirs.assert_called_once_with("path/to", exist_ok=True)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with(expected_content)

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_unexpected_error_on_file_write(self, mock_file_open, mock_os_makedirs, mock_print):
        mock_file_open.return_value.write.side_effect = Exception("Unexpected cosmic ray")
        input_text = (
            "```\n"
            "// path/to/surprise.txt\n"
            "surprise data\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)
        expected_filepath = "path/to/surprise.txt"

        error_message_found = any(
            f"An unexpected error occurred with {expected_filepath}: Unexpected cosmic ray" in args[0]
            for args, _ in mock_print.call_args_list if args
        )
        self.assertTrue(error_message_found, "Unexpected error message not printed.")

    # SEARCH/REPLACE TESTS
    @patch('builtins.print')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="original line1\nsearch content\noriginal line2")
    def test_search_replace_block_success(self, mock_file_open, mock_exists, mock_print):
        input_text = (
            "```python:path/to/file.py\n"
            "<<<<<<< SEARCH\n"
            "search content\n"
            "=======\n"
            "replace content\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file.py"
        mock_print.assert_any_call("Found 1 code block(s). Processing...")
        mock_print.assert_any_call(f"  Processing: {expected_filepath}")
        mock_print.assert_any_call("    [SEARCH/REPLACE mode]")

        # Should have read the existing file
        mock_file_open.assert_any_call(expected_filepath, 'r', encoding='utf-8')

        # Should have written the updated content
        mock_file_open.assert_any_call(expected_filepath, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with("original line1\nreplace content\noriginal line2")

        mock_print.assert_any_call("    Successfully updated path/to/file.py with replacements.")

    @patch('builtins.print')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_search_replace_block_file_not_found(self, mock_file_open, mock_exists, mock_print):
        input_text = (
            "```python:path/to/missing.py\n"
            "<<<<<<< SEARCH\n"
            "search content\n"
            "=======\n"
            "replace content\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/missing.py"
        mock_print.assert_any_call("    [SEARCH/REPLACE mode]")
        mock_print.assert_any_call(f"    Error: File not found for SEARCH/REPLACE block: {expected_filepath}")
        mock_file_open.assert_not_called()

    @patch('builtins.print')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="original content")
    def test_search_replace_block_pattern_not_found(self, mock_file_open, mock_exists, mock_print):
        input_text = (
            "```python:path/to/file.py\n"
            "<<<<<<< SEARCH\n"
            "missing pattern\n"
            "=======\n"
            "replace content\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file.py"
        mock_print.assert_any_call("    [SEARCH/REPLACE mode]")
        mock_print.assert_any_call(f"    Warning: Search pattern not found in {expected_filepath}. No changes made.")
        mock_file_open().write.assert_not_called()

    @patch('builtins.print')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=OSError("Read error"))
    def test_search_replace_block_os_error(self, mock_file_open, mock_exists, mock_print):
        input_text = (
            "```python:path/to/file.py\n"
            "<<<<<<< SEARCH\n"
            "search content\n"
            "=======\n"
            "replace content\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file.py"
        mock_print.assert_any_call(f"    Error reading/writing {expected_filepath}: Read error")

    @patch('builtins.print')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="line1\nline2\nline3")
    def test_search_replace_multiline_content(self, mock_file_open, mock_exists, mock_print):
        input_text = (
            "```python:path/to/file.py\n"
            "<<<<<<< SEARCH\n"
            "line1\n"
            "line2\n"
            "=======\n"
            "new line1\n"
            "new line2\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        mock_file_open().write.assert_called_once_with("new line1\nnew line2\nline3")

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', side_effect=lambda path: path == "existing.py")
    def test_mixed_write_and_search_replace_blocks(self, mock_exists, mock_file_open, mock_os_makedirs, mock_print):
        input_text = (
            "```\n"
            "// new_file.txt\n"
            "new content\n"
            "```\n"
            "```python:existing.py\n"
            "<<<<<<< SEARCH\n"
            "old\n"
            "=======\n"
            "new\n"
            ">>>>>>> REPLACE\n"
            "```"
        )

        # Setup mock for reading existing.py
        read_handles = {
            "existing.py": mock_open(read_data="line1\nold\nline3").return_value
        }

        # Setup mock for writing files
        write_handles = {}

        def open_side_effect(path, mode, *args, **kwargs):
            if mode == 'r':
                return read_handles.get(path, mock_open.return_value)
            elif mode == 'w':
                handle = mock_open.return_value
                write_handles[path] = handle
                return handle

        mock_file_open.side_effect = open_side_effect

        extract_and_write_code_blocks(input_text)

        mock_print.assert_any_call("Found 2 code block(s). Processing...")
        mock_print.assert_any_call("  Processing: new_file.txt")
        mock_print.assert_any_call("    Successfully wrote to new_file.txt")
        mock_print.assert_any_call("  Processing: existing.py")
        mock_print.assert_any_call("    [SEARCH/REPLACE mode]")
        mock_print.assert_any_call("    Successfully updated existing.py with replacements.")

        # Verify writes
        write_calls = mock_file_open.return_value.write.call_args_list
        self.assertEqual(len(write_calls), 2)
        self.assertEqual(write_calls[0][0][0], "new content")  # new_file.txt
        self.assertEqual(write_calls[1][0][0], "line1\nnew\nline3")  # existing.py

if __name__ == '__main__':
    unittest.main()
