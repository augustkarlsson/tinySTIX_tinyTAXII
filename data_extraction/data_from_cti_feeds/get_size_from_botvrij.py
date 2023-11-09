import requests
from bs4 import BeautifulSoup

def main(url):
    # Send an HTTP request to the URL
    response = requests.get(url)

    sizes = []
    print(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_tag = soup.find('pre')


        if pre_tag:
            # Split the content of <pre> tag by newline character
            pre_content = pre_tag.get_text().split('\n')
            #print(pre_content)
            # Iterate through the lines in the content
            for line in pre_content:
                # Extract the values following <a> tags
                parts = line.split()
                if len(parts) == 4:
                    if parts[0] in ["manifest.json", "hashes.csv"]:
                        print("Skipped", parts[0], "with size:", parts[3])
                    else:
                        size = parts[3]
                        size_int = int(size)
                        sizes.append(size_int)

            # Print the extracted sizes
        #print("Sizes extracted from the page:", sizes)


        sorted_list = sorted(sizes)
        #print(sorted_list)
        print("Smallest data: ",sorted_list[0])
        print("Largest data: ",sorted_list[-1])


        # Calculate the median
        n = len(sorted_list)
        if n % 2 == 1:
            # Odd number of elements
            median = sorted_list[n // 2]
        else:
            # Even number of elements
            middle1 = sorted_list[n // 2 - 1]
            middle2 = sorted_list[n // 2]
            median = (middle1 + middle2) / 2

        # Print the median
        print("Median:", median)

        # Initialize a counter
        count = 0

        # Iterate through the sorted list
        for value in sorted_list:
            if value < 2000:
                count += 1
            else:
                # Since the list is sorted, if we encounter a value >= 2000,
                # we can break the loop because all subsequent values will also be >= 2000.
                break

        # Print the count of items with values less than 2000
        print("Number of items with values less than 2000:", count)
        print("Number of items ", n, "\n\n")
        # You can perform further calculations on 'sizes' if needed.

    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)

if __name__ == "__main__":
    urls = ['https://www.botvrij.eu/data/feed-osint/']
    for url in urls:
        main(url)
