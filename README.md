## Open Data - Kingdom of Saudi Arabia  
 
> This repository contains scripts to download datasets from the Open Data portal of the Kingdom of Saudi Arabia (KSA). The main script downloads all datasets for a given organization ID and saves them locally.  


### Directory Structure  

```{bash}
.
├── README.md
├── download_all_org.py
├── opendata (optional - parameter in file)
├── requirements.txt
├── src
│   ├── download_file.py
│   ├── get_dataset_resources.py
│   └── get_org_resources.py
└── system-drawing.excalidraw

```

### How It Works

1. **SSL Adapter**: A custom SSL adapter is created to handle HTTPS requests.
2. **Session Setup**: A session is created and the custom SSL adapter is mounted.
3. **Resource Extraction**: The organization ID and dataset IDs are extracted using the [`get_org_resources`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2FEVA%2FDownloads%2FWCD%2Fexercises%2Fopen-data-ksa%2Fdownload_all_org.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A17%2C%22character%22%3A16%7D%7D%5D%2C%2258b1143f-d36b-4590-bec8-13913091c2ea%22%5D "Go to definition") module.
4. **Directory Creation**: A directory named after the organization ID is created.
5. **Data Download**: All data resources for the organization are downloaded using the [`get_dataset_resources`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2FEVA%2FDownloads%2FWCD%2Fexercises%2Fopen-data-ksa%2Fdownload_all_org.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A17%2C%22character%22%3A35%7D%7D%5D%2C%2258b1143f-d36b-4590-bec8-13913091c2ea%22%5D "Go to definition") module.

## Process Flow

```dot
digraph G {
    rankdir=LR;
    node [shape=box];

    A [label="Start"];
    B [label="Create SSL Adapter"];
    C [label="Setup Session"];
    D [label="Extract Resources"];
    E [label="Create Directory"];
    F [label="Download Data"];
    G [label="End"];

    A -> B -> C -> D -> E -> F -> G;
}
```