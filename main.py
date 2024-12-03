import os
import subprocess

import piexif
from PIL import Image

exif_tags_to_remove = {
    "0th": ["Software", "DateTime"],
    "Exif": [
        "DateTimeOriginal",
        "DateTimeDigitized",
        "OffsetTime",
        "OffsetTimeOriginal",
        "OffsetTimeDigitized",
        "SubSecTimeOriginal",
        "SubSecTimeDigitized",
    ],
}

iptc_tags_to_store = [
    "Keywords",
    "Object Name",
    "Caption-Abstract",
]


def list_metadata(jpeg_file, prefix):
    metadata = [prefix + " " + jpeg_file]

    # Read EXIF metadata
    try:
        img = Image.open(jpeg_file)
        exif_bytes = img.info.get("exif", None)
        if exif_bytes:
            try:
                exif_data = piexif.load(exif_bytes)
                for ifd_name in exif_data:
                    if exif_data[ifd_name]:
                        metadata.append(f"EXIF.{ifd_name}:")
                        for tag, value in exif_data[ifd_name].items():
                            try:
                                tag_name = piexif.TAGS[ifd_name][tag]["name"]
                                metadata.append(f"  {tag_name}: {value}")
                            except KeyError:
                                metadata.append(f"  Unknown Tag {tag}: {value}")
            except Exception as e:
                pass
        else:
            metadata.append("No EXIF metadata found.")
    except Exception as e:
        metadata.append(f"Error reading EXIF metadata: {e}")

    # Read IPTC metadata using exiftool
    try:
        command = ["exiftool", "-IPTC:all", jpeg_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            metadata.append("IPTC:")
            for line in result.stdout.splitlines():
                metadata.append(f"  {line}")
    except Exception as e:
        metadata.append(f"No IPTC metadata: {e}")

    return "\n".join(metadata)


# Function to remove unwanted EXIF tags
def extract_iptc_tags(lines) -> dict:
    result = {}
    for line in lines:
        for tag in iptc_tags_to_store:
            if line.startswith(tag):
                result[tag] = line.split(":")[1].strip()
    return result


def scan_iptc(jpeg_file) -> dict[str, str]:
    # Read IPTC metadata using exiftool
    try:
        command = ["exiftool", "-IPTC:all", jpeg_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            return extract_iptc_tags(lines)
    except Exception as e:
        raise RuntimeError(f"Error reading IPTC metadata: {e}")


def clean_exif_tags(exif_data):
    for ifd, tags in exif_tags_to_remove.items():
        if ifd in exif_data:
            for tag, tag_name in piexif.TAGS[ifd].items():
                if tag_name["name"] in tags:
                    exif_data[ifd].pop(tag, None)
    return exif_data


def clean_exif(input_file, output_file):
    img = Image.open(input_file)
    exif_bytes = img.info.get("exif", None)
    if exif_bytes:
        exif_data = piexif.load(exif_bytes)
        clean_exif_data = clean_exif_tags(exif_data)
        new_exif_bytes = piexif.dump(clean_exif_data)
        img.save(output_file, "jpeg", exif=new_exif_bytes)


# Function to process and clean metadata
def process_file(input_file, output_directory):
    print(f"0️⃣ Processing file: {input_file}")
    # Create output file path
    # print(list_metadata(input_file, "1️⃣ INPUT FILE"))
    iptc_tags = scan_iptc(input_file)
    print(f"2️⃣ Extracted IPTC tags: {iptc_tags}")

    # Clean EXIF metadata
    file_name = os.path.basename(input_file)
    output_file = os.path.join(output_directory, file_name)
    clean_exif(input_file, output_file)
    # print(list_metadata(output_file, "3️⃣️⃣️ OUTPUT FILE"))


# Function to process all JPEG files in a directory
def process_directory(input_directory, output_directory):
    if not os.path.isdir(input_directory):
        print(f"Error: '{input_directory}' is not a valid directory.")
        return
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for root, dirs, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                input_file = os.path.join(root, file)
                process_file(input_file, output_directory)


if __name__ == "__main__":
    # Configure your input and output directories here
    inputDirectory = "/Users/pere/Downloads/exported"  # Change this path as needed
    outputDirectory = "/Users/pere/Downloads/processed"  # Change this path as needed

    process_directory(inputDirectory, outputDirectory)
