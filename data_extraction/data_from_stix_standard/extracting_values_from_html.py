from bs4 import BeautifulSoup
import json
import re

def find_h1_with_text(soup):


    target_text = "10 STIX Vocabularies"

    h1_elements = soup.find_all('h1')
    for h1_element in h1_elements:
        span_element = h1_element.find('span', text=lambda text: target_text in text)
        if span_element:
            return h1_element

    return None


def extract_span_text(soup, html_data):
    span_tags = soup.find_all('span')
    
    # Extract text from each span tag
    span_text = [span.get_text() for span in span_tags]

    return span_text

def extract_type_values(soup):
    p_tags = soup.find_all('p')
    values = []
    for p in p_tags:
        spans = p.find_all("span")
        if spans[0].get_text().lower() == "type name:":
            values.append(spans[-1].get_text())
    temp = {}
    # Iterate over the list and assign incrementing integer values
    for i, value in enumerate(values, start=0):
        temp[value] = i
    return temp

def extract_vocabulary_values(soup, h1_tag):

    # Find all h2 headers that contain "vocabulary" or "enumeration" and appear after the h1

    h2_tables = {}
    h2_tables["type"] = extract_type_values(soup)

    if h1_tag:
        for h2_tag in h1_tag.find_next_siblings("h2"):
            if "vocabulary" in h2_tag.text.lower() or "enumeration" in h2_tag.text.lower():
                p = h2_tag.find_next_sibling("p")
                typename= p.find_all("span")
                if len(typename) != 3:
                    p = p.find_next_sibling("p")
                    typename= p.find_all("span")
                typename = typename[-1].get_text()
                print("TYPENAME", typename)

                table_tag = h2_tag.find_next_sibling("table")
                if table_tag:
                    rows = table_tag.find_all("tr")
                    spans = rows[1].find_all("span")
                    span_text = [span.get_text() for span in spans]

                    filtered_list = []
                    for item in span_text:
                        item = item.strip(",u'\xa0'()").strip()
                        if item:
                            filtered_list.append(item)
                    print("header: ", h2_tag.text.lower().replace("\n", " "))
                    print(filtered_list, "\n")

                    temp = {}
                    # Iterate over the list and assign incrementing integer values
                    for i, value in enumerate(filtered_list, start=0):
                        temp[value] = i
                    h2_tables[typename] = temp
                    temp = {}
                    
    return h2_tables


def extract_property_words_from_html(soup, h1_tag):
    
    # Find all h2 headers that contain "vocabulary" or "enumeration" and appear after the h1
    h2_tables = {}
    if h1_tag:
        for h2_tag in h1_tag.find_next_siblings("h2"):
            if "vocabulary" in h2_tag.text.lower() or "enumeration" in h2_tag.text.lower():
                table_tag = h2_tag.find_next_sibling("table")
                if table_tag:
                    rows = table_tag.find_all("tr")
                    for row in rows:
                        header_cell = row.find("td")
                        # if header_cell and "Vocabulary Summary" in header_cell.text:
                        #if "Vocabulary Summary" in header_cell.find("p").text:
                        new_text = header_cell.find("p").text.replace("\n", "")
                        new_text = re.sub(r'\s+', ' ', new_text)
                        if ("Vocabulary Summary" in new_text) or ("Enumeration Summary" in new_text):
                            print(new_text)
                            values = header_cell.find_all("td")[1:]
                            h2_tables[h2_tag.text.strip()] = [value.text.strip() for value in values]
                            #h2_tables[h2_tag.text.strip()] = [value.text.strip() for value in values]

    # Print the values
    print(h2_tables)
    for header, values in h2_tables.items():
        print(f"{header} Vocabularies Summary:")
        if values:
            print(values)
            print("\n")
        else:
            print("No Vocabularies Summary found.\n")

# def find_string_in_html(soup, target_string):
#     results = soup.find_all(string=target_string)
#     return results
def find_string_and_extract_row_data(soup, target_string):
    results = soup.find_all(lambda tag: tag.name=='td' and target_string.lower() in tag.text.lower())

    extracted_data = []
    for result in results:
        row = result.find_parent('tr')
        if row:
            first_cell = row.find('td')
            if first_cell:
                extracted_data.append(first_cell.text.strip().split()[0])
    # Remove duplicates by converting the list to a set and then back to a list
    extracted_data = list(set(extracted_data))

    return extracted_data
    
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
soup = BeautifulSoup(html_content, 'html.parser')
h1_tag = find_h1_with_text(soup)
#property_words = extract_property_words_from_html(soup, h1_tag)

vals = extract_vocabulary_values(soup, h1_tag)

print(json.dumps(vals, indent=3))


key_vocab_mapping = {}
for key in vals.keys():
    if key != "type":
        res = find_string_and_extract_row_data(soup, key)
        for r in res:
            key_vocab_mapping[r] = key
    else:
        key_vocab_mapping["type"] = "type"

print(key_vocab_mapping)
new_mapping = key_vocab_mapping
for key, val in key_vocab_mapping.items():
    new_mapping[key] = vals[val]

print("\n")
print(json.dumps(new_mapping, indent=4))

with open("values.json", 'w') as f:
        json.dump(new_mapping, f, indent=3)