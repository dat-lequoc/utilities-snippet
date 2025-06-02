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
            "```\n"
            "End of content.\n"
            "```"
        )
        extract_and_write_code_blocks(input_text)

        expected_filepath = "path/to/file_with_backticks.md"
        expected_content = (
            "This is a markdown file.\n"
            "It can contain `inline code` and also fenced code blocks:\n"
            "```python\n"
            "print('nested')\n"
            "```\n"
            "End of content."
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

if __name__ == '__main__':
    unittest.main()
