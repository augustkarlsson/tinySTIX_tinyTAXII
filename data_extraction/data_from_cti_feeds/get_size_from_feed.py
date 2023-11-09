import requests
from bs4 import BeautifulSoup


def main(url):
    # Send an HTTP request to the URL
    response = requests.get(url)

    sizes = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        print(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table element
        table = soup.find('table')
        
        # Find all rows (tr elements) in the table body
        rows = table.find_all('tr')

        # Iterate through the rows and extract the value from the fourth th element
        for row in rows:
            # Find all th elements in the row
            th_elements = row.find_all('td')
            
            # Check if there is a fourth th element (zero-based index)
            if len(th_elements) > 3:
                fourth_value = th_elements[3].text.strip()
                if th_elements[1].text.strip() in ["manifest.json", "hashes.csv"]:
                    print("Skipped", th_elements[1].text.strip(), "with size:", fourth_value)
                else:
                    try:
                        if fourth_value[-1:].isdigit():
                            fourth_value_float = float(fourth_value)
                        else:
                            fourth_value_float = float(fourth_value[:-1])
                        
                        if (fourth_value[-1:] == "K"):
                            fourth_value_float *= 1000
                        elif (fourth_value[-1:] == "M"):
                            fourth_value_float *= 1000000

                        sizes.append(int(fourth_value_float))
                    except ValueError:
                        pass



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

    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)

if __name__ == "__main__":
    urls = ['https://www.circl.lu/doc/misp/feed-osint/','https://urlhaus.abuse.ch/downloads/misp/','https://threatfox.abuse.ch/downloads/misp/']
    for url in urls:
        main(url)