# examples/scripts/2_get_dataset_resource.py

from open_ksa import get_dataset_resource


def test_get_dataset_resource():
    # Define the dataset ID to test
    dataset_id = "e63563d0-3312-48f3-8786-7c3e2af61fe7"

    # Call the function with the test dataset ID
    get_dataset_resource(dataset_id, verbose=True)


if __name__ == "__main__":
    test_get_dataset_resource()
