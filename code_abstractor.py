import sys
from tree_sitter import Language, Parser
import os
import warnings

# Suppress the FutureWarning from tree-sitter
warnings.filterwarnings('ignore', category=FutureWarning)

def build_tree_sitter():
    # Build tree-sitter grammar if not already built
    if not os.path.exists("build/my-languages.so"):
        os.system("git clone https://github.com/tree-sitter/tree-sitter-python")
        Language.build_library(
            "build/my-languages.so",
            ["tree-sitter-python"]
        )

def get_python_parser():
    PY_LANGUAGE = Language("build/my-languages.so", "python")
    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    return parser

def get_function_params(node, source_bytes):
    params = []
    parameters = node.child_by_field_name("parameters")
    if parameters:
        for param in parameters.children:
            if param.type != "," and param.type != "(" and param.type != ")":
                param_text = param.text.decode('utf8')
                params.append(param_text)
    return ", ".join(params)

def get_decorators(node):
    decorators = []
    for child in node.children:
        if child.type == "decorator":
            decorator_text = child.text.decode('utf8')
            decorators.append(decorator_text)
    return decorators

def get_docstring(node, source_bytes):
    # Look for docstring in the first expression statement of the body
    body = node.child_by_field_name("body")
    if body and body.children:
        first_child = body.children[1] if len(body.children) > 1 else None
        if first_child and first_child.type == "expression_statement":
            expr = first_child.children[0]
            if expr.type == "string":
                return expr.text.decode('utf8').strip('"""').strip("'''")
    return None

def get_class_methods(node, source_bytes, depth=0, result=None):
    if result is None:
        result = []
    
    # Handle class definitions
    if node.type == "class_definition":
        class_name = node.child_by_field_name("name").text.decode('utf8')
        # Get inheritance info
        bases = node.child_by_field_name("superclasses")
        base_classes = ""
        if bases:
            base_text = bases.text.decode('utf8')
            # Remove any existing parentheses from the base text
            base_text = base_text.strip('()')
            base_classes = f"({base_text})"
        indent = "│" + "    " * depth
        result.append(f"{indent}class {class_name}{base_classes}:")

        # Get class docstring
        docstring = get_docstring(node, source_bytes)
        if docstring:
            indent = "│" + "    " * (depth + 1)
            result.append(f'{indent}"""{docstring}"""')
        
        # Look for class variables (simple assignments)
        class_vars = []
        for child in node.children:
            if child.type == "block":
                for block_child in child.children:
                    if block_child.type == "expression_statement":
                        expr = block_child.children[0]
                        if expr.type == "assignment":
                            var_name = expr.child_by_field_name("left").text.decode('utf8')
                            indent = "│" + "    " * (depth + 1)
                            class_vars.append(f"{indent}{var_name} = None")
        
        # Add class variables if any were found
        if class_vars:
            result.extend(class_vars)
            result.append("⋮...")
        
        # Process methods within the class
        for child in node.children:
            get_class_methods(child, source_bytes, depth + 1, result)
    
    # Handle function definitions
    elif node.type == "function_definition":
        func_name = node.child_by_field_name("name").text.decode('utf8')
        params = get_function_params(node, source_bytes)
        indent = "│" + "    " * depth
        result.append(f"{indent}def {func_name}({params}):")
        result.append("⋮...")
    
    # Recursively process all children
    for child in node.children:
        get_class_methods(child, source_bytes, depth, result)
    
    return result

def process_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            source_bytes = f.read()
        
        parser = get_python_parser()
        tree = parser.parse(source_bytes)
        
        print(f"{file_path}:")
        print("⋮...")
        
        # Process the abstract syntax tree
        structure = get_class_methods(tree.root_node, source_bytes)
        
        # Print the structure with proper formatting
        last_line = None
        for line in structure:
            # Don't print consecutive ⋮... lines
            if line == "⋮..." and last_line == "⋮...":
                continue
            print(line)
            last_line = line
        
        print()  # Empty line between files
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python code_abstractor.py <python_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    # Ensure tree-sitter is properly set up
    build_tree_sitter()
    
    # Process the file
    process_file(file_path)

if __name__ == "__main__":
    main() 