
# Ollama Invoice Annotator

## Overview

The Ollama Invoice Annotator is a Python script designed to automate the process of annotating invoices. Utilizing powerful libraries such as Pandas for data manipulation, PIL for image processing, and PyPDF2 for PDF manipulation, this script simplifies the extraction, processing, and annotation of invoice data. Additionally, it leverages the Ollama API for enhanced invoice processing capabilities.

## Features

- **Regex-based Value Extraction**: Utilizes regular expressions to accurately extract necessary information from invoice texts.
- **PDF and Image Processing**: Reads and processes invoices in both PDF and image formats, ensuring versatility in handling various invoice formats.
- **Data Manipulation and Analysis**: Employs Pandas for efficient data manipulation and analysis, facilitating easy handling of invoice data.
- **Logging**: Incorporates logging for easy tracking of the script's execution process and debugging.

## Requirements

- Python 3.x
- Pandas
- PIL
- PyPDF2
- Any other dependencies required by the Ollama API client

## Installation

1. Ensure Python 3.x is installed on your system.
2. Install the required Python packages:

   ```
   pip install pandas pillow PyPDF2
   ```

3. Follow the installation and setup instructions for the Ollama API client as specified in its documentation.

## Usage

1. Place your invoices in the designated input directory.
2. Execute the script from your command line:

   ```
   python ollama_inovice_annotator.py
   ```

3. Processed and annotated invoices will be available in the specified output directory.

## Contributing

Contributions to the Ollama Invoice Annotator are welcome. Please ensure to follow best practices for code contributions and adhere to the project's code of conduct.

## License

Specify the license under which this script is released.
