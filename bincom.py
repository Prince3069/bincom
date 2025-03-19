import collections
import statistics
import random
import psycopg2
from typing import List, Dict, Union, Optional

# Data from the table
color_data = {
    'MONDAY': ['GREEN', 'YELLOW', 'GREEN', 'BROWN', 'BLUE', 'PINK', 'BLUE', 'YELLOW', 'ORANGE', 
               'CREAM', 'ORANGE', 'RED', 'WHITE', 'BLUE', 'WHITE', 'BLUE', 'BLUE', 'BLUE', 'GREEN'],
    
    'TUESDAY': ['ARSH', 'BROWN', 'GREEN', 'BROWN', 'BLUE', 'BLUE', 'BLEW', 'PINK', 'PINK', 
                'ORANGE', 'ORANGE', 'RED', 'WHITE', 'BLUE', 'WHITE', 'WHITE', 'BLUE', 'BLUE', 'BLUE'],
    
    'WEDNESDAY': ['GREEN', 'YELLOW', 'GREEN', 'BROWN', 'BLUE', 'PINK', 'RED', 'YELLOW', 'ORANGE', 
                  'RED', 'ORANGE', 'RED', 'BLUE', 'BLUE', 'WHITE', 'BLUE', 'BLUE', 'WHITE', 'WHITE'],
    
    'THURSDAY': ['BLUE', 'BLUE', 'GREEN', 'WHITE', 'BLUE', 'BROWN', 'PINK', 'YELLOW', 'ORANGE', 
                'CREAM', 'ORANGE', 'RED', 'WHITE', 'BLUE', 'WHITE', 'BLUE', 'BLUE', 'BLUE', 'GREEN'],
    
    'FRIDAY': ['GREEN', 'WHITE', 'GREEN', 'BROWN', 'BLUE', 'BLUE', 'BLACK', 'WHITE', 'ORANGE', 
              'RED', 'RED', 'RED', 'WHITE', 'BLUE', 'WHITE', 'BLUE', 'BLUE', 'BLUE', 'WHITE']
}

# Standardize color names (fix typos)
def standardize_colors(data: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Standardize color names by fixing typos."""
    standardized_data = {}
    for day, colors in data.items():
        standardized_colors = []
        for color in colors:
            # Fix known typos
            if color == 'ARSH':
                standardized_colors.append('HARSH')  # Assuming ARSH is a typo for HARSH
            elif color == 'BLEW':
                standardized_colors.append('BLUE')  # BLEW is likely BLUE
            else:
                standardized_colors.append(color)
        standardized_data[day] = standardized_colors
    return standardized_data

# Flatten the color list for overall analysis
def get_all_colors(data: Dict[str, List[str]]) -> List[str]:
    """Get all colors from all days."""
    all_colors = []
    for day, colors in data.items():
        all_colors.extend(colors)
    return all_colors

# 1. Calculate the mean color (most frequent color)
def get_mean_color(colors: List[str]) -> str:
    """Get the mean color (most frequent color)."""
    counter = collections.Counter(colors)
    return counter.most_common(1)[0][0]

# 2. Find the color most worn throughout the week
def get_most_worn_color(colors: List[str]) -> str:
    """Find the color most worn throughout the week."""
    return get_mean_color(colors)  # Same as mean color

# 3. Find the median color
def get_median_color(colors: List[str]) -> str:
    """Find the median color."""
    sorted_colors = sorted(colors)
    return statistics.median(sorted_colors)

# 4. Calculate the variance of the colors
def get_color_variance(colors: List[str]) -> Dict[str, int]:
    """Calculate the variance of the colors."""
    counter = collections.Counter(colors)
    total_count = len(colors)
    variance = {}
    
    # Calculate relative frequencies
    frequencies = {color: count / total_count for color, count in counter.items()}
    
    # Calculate mean frequency
    mean_frequency = 1 / len(counter)
    
    # Calculate variance
    variance_value = sum((freq - mean_frequency) ** 2 for freq in frequencies.values()) / len(frequencies)
    
    return {
        "total_colors": len(counter),
        "variance": variance_value
    }

# 5. Calculate the probability of choosing red
def get_red_probability(colors: List[str]) -> float:
    """Calculate the probability that the color is red."""
    total_colors = len(colors)
    red_count = colors.count('RED')
    return red_count / total_colors

# 6. Save colors and frequencies to PostgreSQL
def save_to_postgresql(colors: List[str]) -> None:
    """Save the colors and their frequencies to PostgreSQL database."""
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="your_database",
            user="your_username",
            password="your_password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS color_frequencies (
                color VARCHAR(50) PRIMARY KEY,
                frequency INTEGER
            )
        """)
        
        # Insert data
        counter = collections.Counter(colors)
        for color, frequency in counter.items():
            cursor.execute(
                "INSERT INTO color_frequencies (color, frequency) VALUES (%s, %s) ON CONFLICT (color) DO UPDATE SET frequency = %s",
                (color, frequency, frequency)
            )
        
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Data saved to PostgreSQL successfully.")
    except Exception as e:
        print(f"Database error: {e}")

# 7. BONUS: Recursive search algorithm
def recursive_search(arr: List[int], target: int, start: int = 0, end: Optional[int] = None) -> int:
    """
    Recursive binary search algorithm to find a number in a sorted list.
    Returns the index of the number if found, -1 otherwise.
    """
    if end is None:
        end = len(arr) - 1
        
    # Base case: element not found
    if start > end:
        return -1
    
    # Find middle index
    mid = (start + end) // 2
    
    # Check if middle element is the target
    if arr[mid] == target:
        return mid
    
    # If target is less than middle element, search left half
    if arr[mid] > target:
        return recursive_search(arr, target, start, mid - 1)
    
    # If target is greater than middle element, search right half
    return recursive_search(arr, target, mid + 1, end)

# 8. Generate random 4-digit binary number and convert to base 10
def generate_binary_and_convert() -> Dict[str, Union[str, int]]:
    """Generate random 4 digits of 0s and 1s and convert to base 10."""
    # Generate 4 random binary digits
    binary_digits = [random.choice(['0', '1']) for _ in range(4)]
    binary_string = ''.join(binary_digits)
    
    # Convert to base 10
    decimal_value = int(binary_string, 2)
    
    return {
        "binary": binary_string,
        "decimal": decimal_value
    }

# 9. Calculate sum of first 50 Fibonacci numbers
def fibonacci_sum(n: int = 50) -> int:
    """Calculate the sum of first n Fibonacci numbers."""
    if n <= 0:
        return 0
    
    fib = [0, 1]
    for i in range(2, n+1):
        fib.append(fib[i-1] + fib[i-2])
    
    return sum(fib[:n+1])

# Process the binary sequence problem from the question
def process_binary_sequence(input_sequence: str) -> str:
    """
    Process the binary sequence according to the rule:
    For every 1s that appear 3 times consecutively, the output will be 1,
    otherwise the output will be 0.
    """
    output = []
    for i in range(len(input_sequence)):
        # Check if current position starts a sequence of three 1s
        if (i + 2 < len(input_sequence) and 
            input_sequence[i] == '1' and 
            input_sequence[i+1] == '1' and 
            input_sequence[i+2] == '1'):
            output.append('1')
        else:
            output.append('0')
    
    return ''.join(output)

def main():
    # Standardize color data
    standardized_data = standardize_colors(color_data)
    all_colors = get_all_colors(standardized_data)
    
    # 1. Mean color
    mean_color = get_mean_color(all_colors)
    print(f"1. Mean color: {mean_color}")
    
    # 2. Most worn color throughout the week
    most_worn_color = get_most_worn_color(all_colors)
    print(f"2. Most worn color throughout the week: {most_worn_color}")
    
    # 3. Median color
    median_color = get_median_color(all_colors)
    print(f"3. Median color: {median_color}")
    
    # 4. BONUS: Variance of colors
    variance_info = get_color_variance(all_colors)
    print(f"4. BONUS - Variance of colors: {variance_info['variance']}")
    
    # 5. BONUS: Probability of choosing red
    red_probability = get_red_probability(all_colors)
    print(f"5. BONUS - Probability of choosing red: {red_probability:.4f}")
    
    # 6. Save to PostgreSQL (commented out to avoid execution)
    print("6. Save to PostgreSQL functionality is implemented but commented out to avoid execution.")
    # save_to_postgresql(all_colors)
    
    # 7. BONUS: Recursive search demonstration
    sorted_list = [1, 3, 5, 7, 9, 11, 13, 15]
    target = 7
    result = recursive_search(sorted_list, target)
    print(f"7. BONUS - Recursive search for {target} in {sorted_list}: found at index {result}")
    
    # 8. Generate random binary and convert to decimal
    binary_decimal = generate_binary_and_convert()
    print(f"8. Random binary: {binary_decimal['binary']}, decimal: {binary_decimal['decimal']}")
    
    # 9. Sum of first 50 Fibonacci numbers
    fib_sum = fibonacci_sum(50)
    print(f"9. Sum of first 50 Fibonacci numbers: {fib_sum}")
    
    # Process the binary sequence problem
    input_seq = "0101101011101011011101101000111"
    output_seq = process_binary_sequence(input_seq)
    print(f"Binary sequence processing:\nInput:  {input_seq}\nOutput: {output_seq}")

if __name__ == "__main__":
    main()