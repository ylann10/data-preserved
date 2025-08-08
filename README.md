# Data-Preserved

Data-Preserved is a Python script that allows you to blur sensitive information in images. It uses Tesseract for OCR to detect text and OpenCV to apply a blur effect on the detected sensitive data.

## Features

-   Detects and blurs:
    -   Email addresses
    -   Phone numbers
    -   IPv4 addresses
    -   IPv6 addresses
-   Command-line interface for easy use.
-   Option to specify the output directory for the blurred images.

## Project Structure
```
.
├── requirements.txt
├── src
│   └── main.py
└── README.md
```

## Prerequisites

Before you begin, ensure you have met the following requirements:

*   **Python 3.7+**
*   **Tesseract OCR**:
    You need to install Tesseract on your system. Please follow the instructions for your operating system.

    -   **Debian/Ubuntu**:
        ```bash
        sudo apt-get install tesseract-ocr
        ```
    -   **macOS**:
        ```bash
        brew install tesseract
        ```
    -   **Windows**:
        Download and install it from the [official Tesseract at UB Mannheim page](https://github.com/UB-Mannheim/tesseract/wiki).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/data-preserved.git
    cd data-preserved
    ```

2.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use Data-Preserved, run the `main.py` script from the `src` directory.

```bash
python src/main.py [IMAGE_PATH] [OPTIONS]
```

### Options

```
usage: main.py [-h] [-b BIN] [-p] [-m] [-4] [-6] [-a] [-s STRINGS] [-o DIR] FILE

Hide sensitive information in images.

positional arguments:
  FILE                  Image path to anonymize.

options:
  -h, --help            show this help message and exit
  -b BIN, --bin BIN     Tesseract binary path.
  -p, --phone           Anonymize phone numbers.
  -m, --mail            Anonymize email addresses.
  -4, --ipv4            Anonymize IPv4 addresses.
  -6, --ipv6            Anonymize IPv6 addresses.
  -a, --all             Anonymize all information.
  -s STRINGS, --strings STRINGS
                        Anonymize a comma-separated list of strings.
  -o DIR, --output DIR  Output directory.
```

### Examples

To blur all sensitive information from an image and save it in the `output` directory:
```bash
python src/main.py path/to/your/image.png --all --output output
```

To blur specific strings from an image:
```bash
python src/main.py path/to/your/image.png --strings "Source,Texas,Mailgun" --output output
```
This will create a new blurred image in the `output` directory.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or issues, please open an issue or create a pull request.
