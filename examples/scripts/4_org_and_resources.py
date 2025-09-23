# -*- coding: utf-8 -*-
#
# Downloading all of the datasets of a single organization ID, if applicable from the opendata portal from KSA
# An organization's full list of resources is retrieved
# Then, we go through all resources to collect the downloadURL links
# Once all downloadURL's are collected, an array is made and a loop goes through each download URL
# Downloads all of the files to a folder called 'opendata/{organizationid}'
# Not, some datasets are still broken, but some decent coverage


# Here you can import all of the corresponding functions from the workbook
import open_ksa as ok


# An example on how to use the search function
def main():
    orgs = ok.organizations()

    # Note: Orgs as a value has the export of the full JSON taken from the API

    # Here, we grab the first value which is the value of the organization ID from the API
    # Depending on the parameters, we can specify the return of the response
    ks = orgs["content"][3]["publisherID"]
    # We have now gotten the publisher ID programmatically. If you change the ID to a string of your choosing or decide to
    # change the search, you can change the orgs['content'][0]['publisherID'] to match your search and the index 0 to N to
    # to match the organization you want
    resources = ok.get_org_resources(org_id=ks)
    # Here, we grab all of the different dataset_ids
    dataset_ids = resources["dataset_ids"]
    # Here, we grab the organization ID as well. But we can use the same organization ID from the ks value
    # we named it ks for 'King Saud University'
    organization_id = resources["organization_id"]

    # Create a directory named after the organization ID
    # Get all of the data resources for the organization
    ok.get_dataset_resources(
        dataset_ids=dataset_ids,
        # You can update the dataset resource location to change the output directory
        # Note: you may have to make the directory
        output_dir=f"opendata/{resources['organization_name'].strip().replace(' ', '_').lower()}",
    )
    return None


if __name__ == "__main__":
    main()
