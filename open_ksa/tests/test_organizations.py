import unittest
from unittest.mock import patch, MagicMock
import requests
import os
from open_ksa.organizations import organizations

class TestOrganizations(unittest.TestCase):

    @patch('open_ksa.organizations.requests.get')
    def test_organizations_no_parameters(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': [
                {'id': 'org1', 'name': 'Organization 1'},
                {'id': 'org2', 'name': 'Organization 2'},
                {'id': 'org3', 'name': 'Organization 3'},
                {'id': 'org4', 'name': 'Organization 4'},
                {'id': 'org5', 'name': 'Organization 5'},
                {'id': 'org6', 'name': 'Organization 6'},
                {'id': 'org7', 'name': 'Organization 7'},
                {'id': 'org8', 'name': 'Organization 8'},
                {'id': 'org9', 'name': 'Organization 9'},
                {'id': 'org10', 'name': 'Organization 10'},
                {'id': 'org11', 'name': 'Organization 11'}
            ]
        }
        mock_get.return_value = mock_response

        # Call the organizations function without parameters
        result = organizations()

        # Assertions
        mock_get.assert_called_once_with(
            'https://open.data.gov.sa/api/organizations',
            params={'size': 400, 'page': 0, 'sort': 'datasetsCount,DESC'},
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': 'https://open.data.gov.sa/',
                'Accept-Language': 'en-US,en;q=0.9',
                'Host': 'open.data.gov.sa',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Check if the result contains the expected data
        self.assertEqual(len(result['content']), 11)
        self.assertEqual(result['content'][0]['name'], 'Organization 1')
    @patch('open_ksa.organizations.requests.get')
    def test_organizations_with_parameters(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': [
                {'id': 'org1', 'name': 'Organization 1'}
            ]
        }
        mock_get.return_value = mock_response

        # Call the organizations function with parameters
        result = organizations(size=1, page=0, sort='datasetsCount,DESC')

        # Assertions
        mock_get.assert_called_once_with(
            'https://open.data.gov.sa/api/organizations',
            params={'size': 1, 'page': 0, 'sort': 'datasetsCount,DESC'},
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': 'https://open.data.gov.sa/',
                'Accept-Language': 'en-US,en;q=0.9',
                'Host': 'open.data.gov.sa',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Check if the result contains the expected data
        self.assertEqual(len(result['content']), 1)
        self.assertEqual(result['content'][0]['name'], 'Organization 1')
        
    @patch('open_ksa.organizations.requests.get')
    def test_organizations_json_decode_error(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_response

        # Call the organizations function
        result = organizations()

        # Assertions
        mock_get.assert_called_once_with(
            'https://open.data.gov.sa/api/organizations',
            params={'size': 400, 'page': 0, 'sort': 'datasetsCount,DESC'},
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': 'https://open.data.gov.sa/',
                'Accept-Language': 'en-US,en;q=0.9',
                'Host': 'open.data.gov.sa',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Check if the result is None due to JSON decode error
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()