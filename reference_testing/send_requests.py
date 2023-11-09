import requests

# URL of the Flask server's /access_resource endpoint
#Remove https if http
server_url = "https://[::1]:9002/access_resource"
responses = 0
while True:
    #Remove verify if HTTP
    response = requests.get(server_url, verify=False)

    if response.status_code == 200:
        responses += 1
        resource_data = response.content
        print(responses)
        print(resource_data)

        # if 'resource' in resource_data:
        #     resource = resource_data['resource']
        #     print(f"Received resource: {resource}")
        # else:
        #     print("No more resources available. Exiting.")
        #     break
        
    else:
        print(f"Error: {response.status_code}")
        break
