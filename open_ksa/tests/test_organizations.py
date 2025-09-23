import unittest
from unittest.mock import patch, MagicMock
import requests
import os
from open_ksa.organizations import organizations


class TestOrganizations(unittest.TestCase):

    @patch("open_ksa.organizations.requests.get")
    def test_organizations_no_parameters(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "org1",
                    "name": "Organization 1",
                    "publisherID": "pub1",
                    "slug": "org-1",
                    "numberOfDatasets": 10,
                },
                {
                    "id": "org2",
                    "name": "Organization 2",
                    "publisherID": "pub2",
                    "slug": "org-2",
                    "numberOfDatasets": 20,
                },
                {
                    "id": "org3",
                    "name": "Organization 3",
                    "publisherID": "pub3",
                    "slug": "org-3",
                    "numberOfDatasets": 30,
                },
                {
                    "id": "org4",
                    "name": "Organization 4",
                    "publisherID": "pub4",
                    "slug": "org-4",
                    "numberOfDatasets": 40,
                },
                {
                    "id": "org5",
                    "name": "Organization 5",
                    "publisherID": "pub5",
                    "slug": "org-5",
                    "numberOfDatasets": 50,
                },
                {
                    "id": "org6",
                    "name": "Organization 6",
                    "publisherID": "pub6",
                    "slug": "org-6",
                    "numberOfDatasets": 60,
                },
                {
                    "id": "org7",
                    "name": "Organization 7",
                    "publisherID": "pub7",
                    "slug": "org-7",
                    "numberOfDatasets": 70,
                },
                {
                    "id": "org8",
                    "name": "Organization 8",
                    "publisherID": "pub8",
                    "slug": "org-8",
                    "numberOfDatasets": 80,
                },
                {
                    "id": "org9",
                    "name": "Organization 9",
                    "publisherID": "pub9",
                    "slug": "org-9",
                    "numberOfDatasets": 90,
                },
                {
                    "id": "org10",
                    "name": "Organization 10",
                    "publisherID": "pub10",
                    "slug": "org-10",
                    "numberOfDatasets": 100,
                },
                {
                    "id": "org11",
                    "name": "Organization 11",
                    "publisherID": "pub11",
                    "slug": "org-11",
                    "numberOfDatasets": 110,
                },
            ]
        }
        mock_get.return_value = mock_response

        # Call the organizations function without parameters
        result = organizations()

        # Assertions: ensure call made with expected params and required headers
        assert mock_get.call_count == 1
        called_args, called_kwargs = mock_get.call_args
        assert called_args[0] == "https://open.data.gov.sa/api/organizations"
        assert called_kwargs.get("params") == {
            "size": 400,
            "page": 0,
            "sort": "datasetsCount,DESC",
        }
        headers = called_kwargs.get("headers", {})
        required = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://open.data.gov.sa/",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "open.data.gov.sa",
            "sec-gpc": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        for k, v in required.items():
            self.assertIn(k, headers)
            self.assertEqual(headers[k], v)

        # Check if the result contains the expected data
        self.assertEqual(len(result["content"]), 11)
        self.assertEqual(result["content"][0]["name"], "Organization 1")

    @patch("open_ksa.organizations.requests.get")
    def test_organizations_with_parameters(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "org1",
                    "name": "Organization 1",
                    "publisherID": "pub1",
                    "slug": "pub-slug",
                    "numberOfDatasets": 100,
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the organizations function with parameters
        result = organizations(size=1, page=0, sort="datasetsCount,DESC")

        # Assertions: ensure call made with expected params and required headers
        assert mock_get.call_count == 1
        called_args, called_kwargs = mock_get.call_args
        assert called_args[0] == "https://open.data.gov.sa/api/organizations"
        assert called_kwargs.get("params") == {
            "size": 1,
            "page": 0,
            "sort": "datasetsCount,DESC",
        }
        headers = called_kwargs.get("headers", {})
        required = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://open.data.gov.sa/",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "open.data.gov.sa",
            "sec-gpc": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        for k, v in required.items():
            self.assertIn(k, headers)
            self.assertEqual(headers[k], v)

        # Check if the result contains the expected data
        self.assertEqual(len(result["content"]), 1)
        self.assertEqual(result["content"][0]["name"], "Organization 1")

    @patch("open_ksa.organizations.requests.get")
    def test_organizations_json_decode_error(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
            "Expecting value", "", 0
        )
        mock_get.return_value = mock_response

        # Call the organizations function
        result = organizations()

        # Assertions: ensure call made with expected params and required headers
        assert mock_get.call_count == 1
        called_args, called_kwargs = mock_get.call_args
        assert called_args[0] == "https://open.data.gov.sa/api/organizations"
        assert called_kwargs.get("params") == {
            "size": 400,
            "page": 0,
            "sort": "datasetsCount,DESC",
        }
        headers = called_kwargs.get("headers", {})
        required = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://open.data.gov.sa/",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "open.data.gov.sa",
            "sec-gpc": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        for k, v in required.items():
            self.assertIn(k, headers)
            self.assertEqual(headers[k], v)

        # Check if the result is None due to JSON decode error
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
