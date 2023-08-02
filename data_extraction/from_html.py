from bs4 import BeautifulSoup
import re
from bs4 import Tag
import json
from collections import Counter, OrderedDict

def extract_text_from_tr(tr_element):
    # Check if the input is a valid <tr> element
    if not isinstance(tr_element, Tag) or tr_element.name != "tr":
        raise ValueError("Invalid input. The input must be a valid <tr> element.")

    # Find the <p> tag inside the <tr>
    p_element = tr_element.find("p")

    # Extract text from all <span> tags inside the <p> tag
    text_list = [span.get_text() for span in p_element.find_all("span")]

    cleaned_strings = [s for s in text_list if ' ' not in s]

    #cleaned_strings = [string.replace(',', '').replace('\n', '') for string in text_list]
    cleaned_strings = [string.replace(',', '').replace('\n', '') for string in cleaned_strings if string.strip()]
    cleaned_strings = [string.strip() for string in cleaned_strings if string.strip()]
    # Concatenate the text and return
    #print("Text list", text_list)
    #print("cleaned list", cleaned_strings)





    return cleaned_strings


def extract_property_words_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all h3 elements
    header_rows = soup.find_all("h3")

    # Regular expression to match the pattern "1.2.3 Properties"
    pattern = r"\d+\.\d+\.\d+\s+Properties"


    # List to store the matching h3 elements along with their tables and following <tr> tags
    matching_headers_with_tables_and_tr = []

    # Iterate through each h3 element and check if the text matches the regex pattern
    for header_row in header_rows:
        text = header_row.get_text()
        if re.search(pattern, text):
            # Find the table associated with the current h3 element
            table = header_row.find_next_sibling("table")
            if table:
                # Find all <p> tags that contain the word "Properties"
                properties_p_list = table.find_all("p", text=re.compile(r"Properties"))
                if properties_p_list:
                    for properties_p in properties_p_list:
                        # Find the following <tr> element
                        tr = properties_p.find_next("tr")
                        if tr:
                            matching_headers_with_tables_and_tr.append((text, properties_p, tr))


    all_properties = []
    # Print the matching h3 elements along with their tables and following <tr> tags
    if matching_headers_with_tables_and_tr:
        for header, properties_p, tr in matching_headers_with_tables_and_tr:
            #print("Matching h3 element:", header)
            print("Matching subheader: ", re.sub(r'\s+', ' ', properties_p.get_text().replace("\n", " ")))
            properties = extract_text_from_tr(tr)
            print(properties, "\n")
            all_properties.extend(properties)
    else:
        print("No match found.")

    return all_properties

def create_dictionary_from_list(input_list):
    # Create the dictionary using dictionary comprehension
    my_dict = {item: index + 1 for index, item in enumerate(input_list)}
    return my_dict

def write_dict_to_file(file_path, my_dict):
    with open(file_path, 'w') as file:
        json.dump(my_dict, file, indent=2)

def sort_by_frequency(lst):
    # Count the occurrences of each string in the list
    counts = Counter(lst)
    
    # Sort the strings by frequency in reverse order and lexicographic order
    sorted_strings = sorted(lst, key=lambda x: (counts[x], x), reverse=True)
    
    # Use an OrderedDict to remove duplicates while preserving the order
    ordered_dict = OrderedDict()
    
    # Initialize a counter for the values
    value_counter = 1
    
    for item in sorted_strings:
        # Add the item to the OrderedDict if it's not already present
        if item not in ordered_dict:
            ordered_dict[item] = value_counter
            value_counter += 1
    # Convert the OrderedDict to a regular dictionary
    regular_dict = dict(ordered_dict)
    
    return regular_dict


    
# Specify the file path of the HTML file
html_file_path = 'stix-v2.1-os.html'

# Read the HTML content from the file with different encodings
encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
html_content = None

for encoding in encodings_to_try:
    try:
        with open(html_file_path, 'r', encoding=encoding) as html_file:
            html_content = html_file.read()
            print(encoding)
        break
    except UnicodeDecodeError:
        continue

if html_content is None:
    raise Exception("Unable to read the HTML file with any of the specified encodings.")

# Extract property words from the HTML
property_words = extract_property_words_from_html(html_content)
print(property_words, "\n")
property_words = sort_by_frequency(property_words)
print(property_words, "\n")

write_dict_to_file("properties.json",property_words)
