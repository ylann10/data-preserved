#!/usr/bin/python3
# encoding: utf-8

import argparse
import re
import sys
from os.path import basename, join, exists, dirname

import cv2
from PIL import Image
from pytesseract import image_to_data, pytesseract

# --- Constants ---

TESSERACT_WIN_64 = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_WIN_86 = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

# Regex patterns for sensitive data
# Source for mail pattern: https://emailregex.com/
PATTERN_MAIL = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
PATTERN_PHONE = r"""(?:\+33|0)\d(?:\.|\s)?\d{2}(?:\.|\s)?\d{2}(?:\.|\s)?\d{2}(?:\.|\s)?\d{2}"""
PATTERN_IP_V4 = r"""((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(?::(?:[0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?"""
PATTERN_IP_V6 = r"""(?:(?:(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))|\[(?:(?:(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))\](?::(?:[0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?"""

# Tesseract data columns
LEFT, TOP, WIDTH, HEIGHT = 6, 7, 8, 9

# --- Functions ---

def get_arguments():
    """Parses and returns command-line arguments."""
    parser = argparse.ArgumentParser(description="Hide sensitive information in images.")
    parser.add_argument("path", metavar="FILE", type=str, help="Image path to anonymize.")
    parser.add_argument("-b", "--bin", metavar="", type=str, default=None, help="Tesseract binary path.")
    parser.add_argument("-p", "--phone", action="store_true", default=False, help="Anonymize phone numbers.")
    parser.add_argument("-m", "--mail", action="store_true", default=False, help="Anonymize email addresses.")
    parser.add_argument("-4", "--ipv4", action="store_true", default=False, help="Anonymize IPv4 addresses.")
    parser.add_argument("-6", "--ipv6", action="store_true", default=False, help="Anonymize IPv6 addresses.")
    parser.add_argument("-a", "--all", action="store_true", default=False, help="Anonymize all information.")
    parser.add_argument("-s", "--strings", type=str, default=None, help="Anonymize a comma-separated list of strings.")
    parser.add_argument("-o", "--output", metavar="DIR", type=str, default=None, help="Output directory.")
    return parser.parse_args()

def initialize_tesseract(tesseract_path):
    """Initializes Tesseract OCR."""
    if tesseract_path and exists(tesseract_path):
        pytesseract.tesseract_cmd = tesseract_path
    elif exists(TESSERACT_WIN_64):
        pytesseract.tesseract_cmd = TESSERACT_WIN_64
    elif exists(TESSERACT_WIN_86):
        pytesseract.tesseract_cmd = TESSERACT_WIN_86
    else:
        sys.exit("Tesseract is not installed or its path is not specified. Please install it or use the -b/--bin option.")

def find_sensitive_data_positions(image_path, args):
    """
    Analyzes an image to find the positions of sensitive data.
    Returns a list of tuples, where each tuple represents a bounding box (x, y, w, h).
    """
    positions = []
    data = image_to_data(Image.open(image_path), output_type='dict')

    patterns = []
    if args.mail or args.all:
        patterns.append(PATTERN_MAIL)
    if args.ipv6 or args.all:
        patterns.append(PATTERN_IP_V6)
    if args.ipv4 or args.all:
        patterns.append(PATTERN_IP_V4)
    if args.phone or args.all:
        patterns.append(PATTERN_PHONE)

    custom_strings = []
    if args.strings:
        custom_strings = [s.strip() for s in args.strings.split(',')]

    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if not text:
            continue

        # Check for custom strings
        if text in custom_strings:
            try:
                x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])
                positions.append((x, y, w, h))
                continue  # Move to the next word
            except (ValueError, KeyError):
                continue

        # Check for regex patterns
        matched_by_pattern = False
        for pattern in patterns:
            if re.match(pattern, text):
                try:
                    x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])
                    positions.append((x, y, w, h))
                    matched_by_pattern = True
                    break  # Move to the next pattern
                except (ValueError, KeyError):
                    continue
        if matched_by_pattern:
            continue

    return positions

def blur_image_regions(image_path, positions):
    """
    Applies a Gaussian blur to the specified regions of an image.
    Returns the modified image.
    """
    img = cv2.imread(image_path)
    for x, y, w, h in positions:
        roi = img[y:y+h, x:x+w]
        # Use a kernel size proportional to the ROI size for better results
        kernel_w = w // 2 if w // 2 % 2 != 0 else w // 2 + 1
        kernel_h = h // 2 if h // 2 % 2 != 0 else h // 2 + 1
        blurred_roi = cv2.GaussianBlur(roi, (kernel_w, kernel_h), 0)
        img[y:y+h, x:x+w] = blurred_roi
    return img

def save_image(image, original_path, output_dir):
    """Saves the image to the specified output directory or to the original directory."""
    name, ext = basename(original_path).rsplit('.', 1)

    if output_dir:
        output_path = join(output_dir, f"{name}.{ext}")
    else:
        output_path = join(dirname(original_path), f"{name}.blurred.{ext}")

    cv2.imwrite(output_path, image)
    print(f"Blurred image saved to: {output_path}")

def main():
    """Main function to run the image anonymization script."""
    args = get_arguments()
    initialize_tesseract(args.bin)

    if not exists(args.path):
        sys.exit(f"Error: The file '{args.path}' does not exist.")

    positions = find_sensitive_data_positions(args.path, args)

    if not positions:
        print("No sensitive information found to blur.")
        return

    blurred_image = blur_image_regions(args.path, positions)
    save_image(blurred_image, args.path, args.output)

if __name__ == "__main__":
    main()
