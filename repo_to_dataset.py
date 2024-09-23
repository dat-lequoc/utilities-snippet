import os
import argparse
import time
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import tiktoken
from tqdm import tqdm
from collections import Counter

def should_ignore(path, is_dir=False):
    ignore_list = [
        '.git', '__pycache__', 'node_modules', 'venv', 'env',
        'build', 'dist', 'target', 'bin', 'obj',
        '.idea', '.vscode', '.gradle'
    ]
    ignore_extensions = [
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.class',
        '.md', '.markdown', '.yaml', '.yml', '.json', '.xml',
        '.log', '.lock', '.cfg', '.ini', '.toml', '.parquet',
        '.webm', '.png', '.gif', '.jpg', '.jpeg', '.bmp', '.tiff',
        '.mp3', '.mp4', '.avi', '.mov', '.flv', '.wav',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.exe', '.bin', '.iso',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.svg', '.ico', '.ttf', '.woff', '.woff2',
        '.min.js', '.min.css',
        '.cjs', '.example', '.hbs', 
        '.map', '.otf', '.snap', '.svelte', '.template',
        '.tpl', '.txt', '.webp'
    ]
    
    name = os.path.basename(path)
    
    if is_dir:
        return name in ignore_list
    else:
        file_extension = os.path.splitext(name)[1].lower()
        return name in ignore_list or file_extension in ignore_extensions

def count_lines_and_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        lines = content.split('\n')
        
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(content)
    
    return len(lines), len(tokens)

def process_directory(path):
    results = []
    file_data = []
    all_extensions = set()
    total_files = 0

    # First, count the total number of files (excluding ignored directories)
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), is_dir=True)]
        total_files += len([f for f in files if not should_ignore(os.path.join(root, f))])

    # Now process the files with a progress bar
    with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to ignore specified directories
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), is_dir=True)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path):
                    file_extension = os.path.splitext(file)[1].lower()
                    all_extensions.add(file_extension)
                    
                    line_count, token_count = count_lines_and_tokens(file_path)
                    
                    if line_count >= 100:
                        content = read_file_content(file_path)
                        results.append((file_path, content))

                    file_data.append({
                        'file_path': file_path,
                        'line_count': line_count,
                        'token_count': token_count
                    })

                    pbar.update(1)

    df = pd.DataFrame(file_data)
    
    # Calculate statistics
    total_lines = df['line_count'].sum()
    total_tokens = df['token_count'].sum()
    included_files = len(results)
    max_lines = df['line_count'].max()
    max_tokens = df['token_count'].max()
    file_with_max_lines = df.loc[df['line_count'].idxmax(), 'file_path']
    file_with_max_tokens = df.loc[df['token_count'].idxmax(), 'file_path']

    # Calculate distributions
    size_distribution = pd.cut(df['line_count'], 
                               bins=[0, 100, 500, 1000, np.inf], 
                               labels=['<100 lines', '100-499 lines', '500-999 lines', '1000+ lines'])
    token_distribution = pd.cut(df['token_count'], 
                                bins=[0, 1000, 5000, 10000, np.inf], 
                                labels=['<1000 tokens', '1000-4999 tokens', '5000-9999 tokens', '10000+ tokens'])

    size_dist_dict = size_distribution.value_counts().to_dict()
    token_dist_dict = token_distribution.value_counts().to_dict()

    return (results, total_files, total_lines, total_tokens, included_files, 
            max_lines, max_tokens, file_with_max_lines, file_with_max_tokens, 
            size_dist_dict, token_dist_dict, all_extensions, df)

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def save_to_parquet(results, output_file):
    df = pd.DataFrame(results, columns=['File Name', 'Content'])
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_file)

def sample_dataset(df, sample_sizes):
    bins = {
        '<100 lines': (0, 100),
        '100-499 lines': (100, 500),
        '500-999 lines': (500, 1000),
        '1000+ lines': (1000, np.inf)
    }
    
    sampled_dfs = []
    for bin_name, size in sample_sizes.items():
        if size > 0:
            lower, upper = bins[bin_name]
            bin_df = df[(df['line_count'] >= lower) & (df['line_count'] < upper)]
            if len(bin_df) > 0:
                if len(bin_df) > size:
                    sampled_dfs.append(bin_df.sample(size))
                else:
                    sampled_dfs.append(bin_df)
                print(f"Sampled {len(sampled_dfs[-1])} files from {bin_name} (requested: {size})")
            else:
                print(f"No files found in the {bin_name} range")
    
    if not sampled_dfs:
        print("No samples were selected. Please check your sampling parameters and the content of your dataset.")
        return None
    
    return pd.concat(sampled_dfs, ignore_index=True)

def print_sample_statistics(sampled_df):
    print("\nSampled Dataset Statistics:")
    print(f"Total files in sample: {len(sampled_df)}")
    print(f"Total lines in sample: {sampled_df['line_count'].sum()}")
    print(f"Total tokens in sample: {sampled_df['token_count'].sum()}")
    
    extensions = Counter(sampled_df['file_path'].apply(lambda x: os.path.splitext(x)[1].lower()))
    print("\nFile Extensions in Sample:")
    for ext, count in extensions.most_common():
        print(f"  {ext}: {count}")
    
    size_distribution = pd.cut(sampled_df['line_count'], 
                               bins=[0, 100, 500, 1000, np.inf], 
                               labels=['<100 lines', '100-499 lines', '500-999 lines', '1000+ lines'])
    print("\nSize Distribution in Sample:")
    for category, count in size_distribution.value_counts().items():
        print(f"  {category}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Recursively read files, sample, and save to Parquet file.')
    parser.add_argument('path', help='Path to the directory to process')
    parser.add_argument('--output', default='output.parquet', help='Output file name (default: output.parquet)')
    parser.add_argument('--sample-lt-100', type=int, default=50, help='Number of samples for files with <100 lines')
    parser.add_argument('--sample-100-499', type=int, default=150, help='Number of samples for files with 100-499 lines')
    parser.add_argument('--sample-500-999', type=int, default=0, help='Number of samples for files with 500-999 lines')
    parser.add_argument('--sample-1000-plus', type=int, default=0, help='Number of samples for files with 1000+ lines')
    args = parser.parse_args()

    start_time = time.time()
    (results, total_files, total_lines, total_tokens, included_files, 
     max_lines, max_tokens, file_with_max_lines, file_with_max_tokens, 
     size_distribution, token_distribution, all_extensions, df) = process_directory(args.path)

    sample_sizes = {
        '<100 lines': args.sample_lt_100,
        '100-499 lines': args.sample_100_499,
        '500-999 lines': args.sample_500_999,
        '1000+ lines': args.sample_1000_plus
    }

    sampled_df = sample_dataset(df, sample_sizes)
    if sampled_df is not None and not sampled_df.empty:
        sampled_results = [(row['file_path'], read_file_content(row['file_path'])) for _, row in sampled_df.iterrows()]
        save_to_parquet(sampled_results, args.output)
        end_time = time.time()

        print(f"\nResults saved to {args.output}")
        print("\nOriginal Dataset Statistics:")
        print(f"Total files processed: {total_files}")
        print(f"Total lines processed: {total_lines}")
        print(f"Total tokens processed: {total_tokens}")
        print(f"Files included in output: {included_files}")
        print(f"Files ignored: {total_files - included_files}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"\nHighest number of lines in a file: {max_lines}")
        print(f"File with the most lines: {file_with_max_lines}")
        print(f"Maximum number of tokens in a file: {max_tokens}")
        print(f"File with the most tokens: {file_with_max_tokens}")
        print("\nFile Size Distribution:")
        for category, count in size_distribution.items():
            print(f"  {category}: {count}")
        print("\nToken Distribution:")
        for category, count in token_distribution.items():
            print(f"  {category}: {count}")
        print("\nDistinct File Extensions:")
        for ext in sorted(all_extensions):
            print(f"  {ext}")

        print_sample_statistics(sampled_df)
    else:
        print("\nNo samples were selected. The output file was not created.")
        print("Please check your sampling parameters and the content of your dataset.")

if __name__ == "__main__":
    main()
