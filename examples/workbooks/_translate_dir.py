from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os
import concurrent.futures
import pandas as pd
import re
import time
load_dotenv()
start_time = time.time()
print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=api_key)
# print(f"Using API key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
def list_files(base_dir, exts='.csv'):
    files_list = []
    # Walk through the directory
    for root, dirs, files in os.walk(base_dir):
        # Skip directories that contain 'data_dictionary' in their path
        if 'data_dictionary' in root.split(os.sep):
            continue
        for file in files:
            if any(file.endswith(ext) for ext in exts):
                # Append the full path of the csv file to the list
                files_list.append(os.path.join(root, file))
    return files_list

def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))

def split_and_save_csv(df, base_output_path, chunk_size=1000):
    """
    Split a DataFrame into chunks and save each as a separate CSV file.
    
    If the DataFrame has <= chunk_size rows, saves as a single file without suffix.
    If > chunk_size rows, splits into multiple files with _1, _2, etc. suffix before extension.
    Each chunk includes the header row.
    
    Args:
        df: pandas DataFrame to split and save
        base_output_path: Base path for output file (e.g., '/path/to/file.csv')
        chunk_size: Maximum rows per chunk (default: 1000)
    
    Returns:
        int: Number of files created
    """
    num_rows = len(df)
    
    # If DataFrame is small enough, save normally without suffix
    if num_rows <= chunk_size:
        df.to_csv(base_output_path, index=False)
        return 1
    
    # Split into chunks
    base_name, ext = os.path.splitext(base_output_path)
    num_chunks = (num_rows + chunk_size - 1) // chunk_size  # Ceiling division
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, num_rows)
        chunk = df.iloc[start_idx:end_idx]
        
        # Create output path with _n suffix
        chunk_path = f"{base_name}_{i + 1}{ext}"
        print(f"Saving chunk {i + 1} of {num_chunks} to {chunk_path}")
        chunk.to_csv(chunk_path, index=False)
    
    return num_chunks

def translate_text(text):
    if not text or not isinstance(text, str):
        return text
    
    model = os.getenv("OR_MODEL", "gpt-5-mini")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert translating arabic to english. You receive a string in arabic and you will only return the english translation of the string."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Rate limit error after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            print(f"Error translating text: {e}")
            raise

def translate_single_file(file_path, base_directory, verbose=None):
    """
    Translate a single file and return status.
    Returns: (success: bool, filename: str, error_msg: str or None)
    """
    filename = os.path.basename(file_path)
    
    # Check if already translated
    output_path = base_directory+'/en/'+filename
    if os.path.exists(output_path):
        # print(f"Skipping already translated file: {filename}")
        return (True, filename, None)
    
    try:
        # Determine the file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        print(f"Processing file: {filename}")
        
        if file_extension == '.csv':
            # Load the CSV file into a DataFrame with error handling for encoding issues
            df = None
            for encoding in ['utf-8', 'ISO-8859-1', 'cp1256']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding,low_memory=False)
                    break  # Exit the loop if reading is successful
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue  # Try the next encoding if there's an error
            
            if df is None:
                raise RuntimeError(f"Failed to read CSV file with any encoding: {file_path}")
            
            # Remove completely empty rows
            df.dropna(how='all', inplace=True)
        elif file_extension == '.json':
            # Load the JSON file into a DataFrame
            try:
                df = pd.read_json(file_path)
            except ValueError as e:
                if verbose: print(f"Error reading JSON file {file_path}: {e}")
                return (False, filename, str(e))
        else:
            if verbose: print(f"Unsupported file extension: {file_extension}")
            return (False, filename, f"Unsupported file extension: {file_extension}")
        
        # Translate columns
        df.columns = [translate_text(col) for col in df.columns]
        
        # Detect string value columns and translate the values
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: translate_text(x) if isinstance(x, str) and is_arabic(x) else x)
        
        # Split and save CSV (splits if > 1000 rows)
        num_files = split_and_save_csv(df, output_path, chunk_size=1000)
        
        if num_files > 1:
            print(f"Successfully translated and split into {num_files} parts: {filename}")
        else:
            print(f"Successfully translated: {filename}")
        return (True, filename, None)
        
    except Exception as e:
        error_msg = f"Error processing {filename}: {str(e)}"
        print(error_msg)
        return (False, filename, str(e))

def translate_files(file_paths, base_directory, verbose=None):
    """Translate multiple files in parallel using ThreadPoolExecutor."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all translation tasks
        future_to_file = {
            executor.submit(translate_single_file, file_path, base_directory, verbose): file_path 
            for file_path in file_paths
        }
        
        # Track results
        successes = []
        failures = []
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                success, filename, error_msg = future.result()
                if success:
                    successes.append(filename)
                else:
                    failures.append((filename, error_msg))
            except Exception as e:
                filename = os.path.basename(file_path)
                failures.append((filename, str(e)))
                print(f"Unexpected error with {filename}: {e}")
        
        # Print summary
        print(f"\n=== Translation Summary ===")
        print(f"Successfully translated: {len(successes)} files")
        print(f"Failed: {len(failures)} files")
        if failures:
            print(f"\nFailed files:")
            for filename, error in failures:
                print(f"  - {filename}: {error}")



base_directories = [
    # 'examples/workbooks/opendata/ministry_of_health',
    # 'examples/workbooks/opendata/ministry_of_foreign_affairs',
    # 'examples/workbooks/opendata/ministry_of_investment',
    'examples/workbooks/opendata/ministry_of_finance',
    'examples/workbooks/opendata/ministry_of_human_resources_and_social_development',
    'examples/workbooks/opendata/ministry_of_transport',
    'examples/workbooks/opendata/ministry_of_education',
    'examples/workbooks/opendata/ministry_of_environment,_water_and_agriculture',
    'examples/workbooks/opendata/ministry_of_energy',
    'examples/workbooks/opendata/ministry_of_justice',
    'examples/workbooks/opendata/ministry_of_interior',
    'examples/workbooks/opendata/ministry_of_labor_and_social_development_-_ministry_of_planning_and_development-information_center',
    'examples/workbooks/opendata/ministry_of_culture',
    'examples/workbooks/opendata/ministry_of_sport',
    'examples/workbooks/opendata/ministry_of_media',
    'examples/workbooks/opendata/ministry_of_sports',
    'examples/workbooks/opendata/ministry_of_economy_and_planning',
    'examples/workbooks/opendata/ministry_of_tourism'
    
]
for base_directory in base_directories:
    file_paths = list_files(base_directory,exts = "*.csv")
    if not os.path.exists(base_directory+'/en'):
        os.makedirs(base_directory+'/en')
    #Remove non-csv files from the file_paths list
    file_paths = [file for file in file_paths if file.endswith('.csv')]
    # Define a regular expression to filter the file paths that should be excluded
    regex = r'competition data|Social Security Branches and Offices'
    file_paths = [file for file in file_paths if not re.search(regex, file)]
    translate_files(file_paths, base_directory)
end_time = time.time()
#Show the end time in a human readable format
print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
print(f"Time taken: {end_time - start_time:.2f} seconds")