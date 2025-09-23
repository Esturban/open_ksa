# examples/scripts/3_get_dataset_resources.py

from open_ksa import get_dataset_resources, get_org_resources


def test_get_dataset_resources():
    # Define the dataset ID to test
    org_id = "a9e617ff-d918-4f4d-8be1-c42b733b1143"  # King Saud University
    resources = get_org_resources(org_id=org_id)
    # Here, we grab all of the different dataset_ids
    dataset_ids = resources["dataset_ids"]
    # Here, we grab the organization ID as well. But we can use the same organization ID from the ks value
    # we named it ks for 'King Saud University'
    organization_id = resources["organization_id"]

    get_dataset_resources(
        dataset_ids=dataset_ids[0:10],
        output_dir=f"opendata/{resources['organization_name'].strip().replace(' ', '_').lower()}",
        allowed_exts=["csv"],
        verbose=False,
        show_progress=True,
    )


if __name__ == "__main__":
    test_get_dataset_resources()
