import requests
import json


class TestDataGenAPI:
    def process_response(self,response):
        if response.status_code == 200:
            # Process the response data
            data = response.json()
            print("Data:", data)
        else:
            # If there was an error, print the error message returned by the API
            error_message = response.json()["error"]
            print("Error:", error_message)

    def test_load_data(self, url):
        print(url+"/load_data")
        response = requests.post(url+"/load_data",data={"file_paths": r"C:\MK_share\new graph docs\chatgpt.pdf"})
        self.process_response(response)

    def test_build_golden_data(self, url):
        response = requests.post(url + "/build_ground_truth_data", data={"file_paths": r"C:\MK_share\new graph docs\chatgpt.pdf"})
        self.process_response(response)

    def test_generate_bot_response(self, url):
        self.process_response(requests.get(url + "/generate_bot_responses"))

    def test_evaluate_bot_response(self, url):
        self.process_response(requests.get(url + "/evaluate_responses_with_golden_data"))

    def test_context(self, url):
        self.process_response(requests.get(url+"/get_context"))


if __name__ == "__main__":
    # Replace with the API endpoint URL
    base_api_url = 'http://127.0.0.1:5000/data-gen'
    tdg = TestDataGenAPI()
    # tdg.test_load_data(base_api_url)
    # tdg.test_build_golden_data(base_api_url)
    # tdg.test_generate_bot_response(base_api_url)
    # tdg.test_evaluate_bot_response(base_api_url)

    requests.get(base_api_url)


