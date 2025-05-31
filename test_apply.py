#!/usr/bin/env python3
import unittest
import subprocess
import os
import tempfile
import shutil
import sys
import argparse

# Get the directory containing this test script (__file__ is the path to the current script)
TEST_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Assume apply.py is in the same directory as this test script
# Construct an absolute path to apply.py
UPDATER_SCRIPT_PATH = os.path.join(TEST_SCRIPT_DIR, "apply.py")

# Optional: If you prefer to run 'python /path/to/apply.py'
# This can be more robust on systems where direct execution via shebang might be tricky
# or if apply.py isn't marked executable.
# PYTHON_EXECUTABLE = sys.executable
# COMMAND_TO_RUN_APPLY_PY = [PYTHON_EXECUTABLE, UPDATER_SCRIPT_PATH]


class TestApplyScript(unittest.TestCase): # Renamed class for clarity

    def setUp(self):
        # Define the parent directory for test outputs
        parent_test_dir = "/tmp/test_apply"
        # Ensure the parent directory exists
        os.makedirs(parent_test_dir, exist_ok=True)

        # Get the current test method name (e.g., "test_single_file_creation")
        test_method_name = self.id().split('.')[-1]
        
        # Construct the path for the test-specific directory
        self.test_dir = os.path.join(parent_test_dir, test_method_name)

        # If the directory already exists (e.g., from a previous failed run), remove it
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Create the test-specific directory
        os.makedirs(self.test_dir)
        
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        if not getattr(self, 'keep_directory', False): # Check a flag set by __main__
            shutil.rmtree(self.test_dir)
        else:
            print(f"Keeping test directory: {self.test_dir}")

    def run_updater_with_input(self, input_text):
        # Use the absolute path UPDATER_SCRIPT_PATH
        command_to_run = [UPDATER_SCRIPT_PATH]
        # Or if you chose the PYTHON_EXECUTABLE method:
        # command_to_run = COMMAND_TO_RUN_APPLY_PY

        # Ensure apply.py is executable if running directly
        # This check might be redundant if you handle it in if __name__ == "__main__"
        # but can be a safeguard.
        if command_to_run[0] == UPDATER_SCRIPT_PATH and not os.access(UPDATER_SCRIPT_PATH, os.X_OK) and os.name != 'nt':
             try:
                os.chmod(UPDATER_SCRIPT_PATH, 0o755)
                print(f"Made {UPDATER_SCRIPT_PATH} executable from test runner.")
             except OSError as e:
                print(f"Warning: Could not make {UPDATER_SCRIPT_PATH} executable from test runner: {e}. Test might fail if it's not already executable.")


        process = subprocess.Popen(
            command_to_run,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate(input=input_text)
        return stdout, stderr, process.returncode

    def test_single_file_creation(self):
        input_text = """
        Some preamble.
        ```
        // my_app/module1.py
        print("Hello from module1")
        # A comment
        ```
        Some postamble.
        """
        stdout, stderr, returncode = self.run_updater_with_input(input_text)

        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("my_app/module1.py"), "File was not created")

        with open("my_app/module1.py", 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, '        print("Hello from module1")\n        # A comment')

    def test_multiple_files_and_overwrite(self):
        input_text1 = """
        ```
        // app/core/config.py
        API_KEY = "initial_key"
        ```
        ```
        // data/user_data.txt
        User1: Alice
        User2: Bob
        ```
        """
        stdout1, stderr1, returncode1 = self.run_updater_with_input(input_text1)
        self.assertEqual(returncode1, 0, f"Script (run1) exited with error: {stderr1}\nStdout: {stdout1}")

        self.assertTrue(os.path.exists("app/core/config.py"))
        self.assertTrue(os.path.exists("data/user_data.txt"))
        with open("app/core/config.py", 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), '        API_KEY = "initial_key"')

        input_text2 = """
        ```
        // app/core/config.py
        API_KEY = "updated_key"
        DEBUG_MODE = True
        ```
        ```
        // app/utils/helpers.js
        function greet() { console.log("Hi"); }
        ```
        """
        stdout2, stderr2, returncode2 = self.run_updater_with_input(input_text2)
        self.assertEqual(returncode2, 0, f"Script (run2) exited with error: {stderr2}\nStdout: {stdout2}")

        self.assertTrue(os.path.exists("app/core/config.py"))
        self.assertTrue(os.path.exists("app/utils/helpers.js"))
        self.assertTrue(os.path.exists("data/user_data.txt"))

        with open("app/core/config.py", 'r', encoding='utf-8') as f:
            expected_content = '        API_KEY = "updated_key"\n        DEBUG_MODE = True'
            self.assertEqual(f.read(), expected_content)
        with open("app/utils/helpers.js", 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), '        function greet() { console.log("Hi"); }')

    def test_no_valid_blocks(self):
        input_text = "Just some plain text without code blocks."
        stdout, stderr, returncode = self.run_updater_with_input(input_text)
        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertIn("No valid code blocks found.", stdout)
        self.assertEqual(len(os.listdir(".")), 0, "Files were created unexpectedly")


    def test_file_in_root(self):
        input_text = """
        ```
        // root_file.txt
        This is a file in the root.
        ```
        """
        stdout, stderr, returncode = self.run_updater_with_input(input_text)
        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("root_file.txt"))
        with open("root_file.txt", 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "        This is a file in the root.")

    def test_empty_content(self):
        input_text = """
        ```
        // empty_content_file.py

        ```
        """
        stdout, stderr, returncode = self.run_updater_with_input(input_text)
        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("empty_content_file.py"))
        with open("empty_content_file.py", 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "        ")

    def test_content_with_leading_trailing_newlines_in_block(self):
        input_text = """
        ```
        // newlines_test.txt

        Line 1

        Line 2

        ```
        """
        stdout, stderr, returncode = self.run_updater_with_input(input_text)
        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("newlines_test.txt"))
        with open("newlines_test.txt", 'r', encoding='utf-8') as f:
            # Expected: initial 8-space line, then content lines, then final 8-space line (captured before its \n)
            # "        \n"  (from first blank line in input_text block)
            # "        Line 1\n"
            # "        \n"  (from second blank line)
            # "        Line 2\n"
            # "        "     (from third blank line, its \n is consumed by regex pattern)
            self.assertEqual(f.read(), "        \n        Line 1\n        \n        Line 2\n        ")

    def test_indented_python_nested_function(self):
        input_text = (
            f'\n'
            f'        ```\n'
            f'        // my_module/nested_func.py\n'
            f'            def outer_function():\n'
            f'                print("Outer function")\n'
            f'\n'
            f'                def inner_function():\n'
            f'                    print("Inner function, indented")\n'
            f'                \n'
            f'                inner_function()\n'
            f'            \n'
            f'            outer_function()\n'
            f'        ```\n'
            f'        '
        )
        stdout, stderr, returncode = self.run_updater_with_input(input_text)
        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("my_module/nested_func.py"), "File was not created")

        expected_content = """            def outer_function():
                print("Outer function")

                def inner_function():
                    print("Inner function, indented")
                
                inner_function()
            
            outer_function()"""
        with open("my_module/nested_func.py", 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, expected_content)

    def test_file_path_with_hash_comment(self):
        input_text = """
        Some preamble.
        ```
        # my_app/module_hash.py
        print("Hello from module_hash")
        ```
        Some postamble.
        """
        stdout, stderr, returncode = self.run_updater_with_input(input_text)

        self.assertEqual(returncode, 0, f"Script exited with error: {stderr}\nStdout: {stdout}")
        self.assertTrue(os.path.exists("my_app/module_hash.py"), "File was not created")

        with open("my_app/module_hash.py", 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, '        print("Hello from module_hash")')


if __name__ == "__main__":
    # Ensure apply.py is executable. UPDATER_SCRIPT_PATH is an absolute path.
    if not os.access(UPDATER_SCRIPT_PATH, os.X_OK) and os.name != 'nt':
        try:
            print(f"Attempting to make {UPDATER_SCRIPT_PATH} executable...")
            os.chmod(UPDATER_SCRIPT_PATH, 0o755)
            print(f"Successfully made {UPDATER_SCRIPT_PATH} executable.")
        except OSError as e:
            print(f"Warning: Could not make {UPDATER_SCRIPT_PATH} executable: {e}")
            print(f"If tests fail due to permission errors, please ensure '{UPDATER_SCRIPT_PATH}' is executable,")
            print(f"or modify 'command_to_run' in 'run_updater_with_input' to use [sys.executable, '{UPDATER_SCRIPT_PATH}'].")
    elif os.name == 'nt':
        print(f"On Windows. Assuming '{UPDATER_SCRIPT_PATH}' is executable via Python association.")
    else:
        print(f"{UPDATER_SCRIPT_PATH} is already executable or not on a POSIX system requiring explicit chmod here.")

    parser = argparse.ArgumentParser(description="Run tests for apply.py")
    parser.add_argument(
        '--keep',
        action='store_true',
        help="Keep the temporary test directory after tests are run for inspection."
    )
    # Parse known args, leave the rest for unittest
    args, unknown = parser.parse_known_args()

    # Pass the 'keep' flag to the test class instances if needed.
    # One way is to set a class attribute or pass it through TestLoader.
    # For simplicity here, we'll rely on a global-like access or pass it if TestLoader was used.
    # A more robust way would be to customize the TestLoader or TestSuite.
    # However, for this specific case, we can make the TestApplyScript aware of it.
    # We will set an attribute on the class itself, which instances can check in tearDown.
    if args.keep:
        TestApplyScript.keep_directory = True


    # unittest.main() processes sys.argv by default.
    # We need to pass only the unittest-specific arguments to it.
    # sys.argv[0] is the script name, followed by unittest arguments.
    unittest_argv = [sys.argv[0]] + unknown
    unittest.main(argv=unittest_argv)
