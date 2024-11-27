import subprocess
import re
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os

# Function to retrieve serial numbers from system_profiler
def get_airpods_serial():
    try:
        output = subprocess.check_output(["system_profiler", "SPBluetoothDataType"], text=True)
        airpods_info = re.search(r"(AirPods.*?:.*?)\n\n", output, re.S)
        if airpods_info:
            airpods_data = airpods_info.group(1)
            print(airpods_data)  # Debug: Print AirPods-specific section

            serials = {
                "case": re.search(r"Serial Number: (\w+)", airpods_data),
                "left": re.search(r"Serial Number \(Left\): (\w+)", airpods_data),
                "right": re.search(r"Serial Number \(Right\): (\w+)", airpods_data),
            }
            return {key: match.group(1) if match else "Not Found" for key, match in serials.items()}

        return {"case": "Not Found", "left": "Not Found", "right": "Not Found"}
    except Exception as e:
        print(f"Error retrieving serial numbers: {e}")
        return {"case": "Not Found", "left": "Not Found", "right": "Not Found"}

def generate_barcode_with_label(serial_number, label_text, output_dir="barcodes"):
    try:
        # Define the target dimensions for the label in pixels (300 DPI)
        mm_to_inches = 0.0393701
        dpi = 300  # Standard DPI for barcode printing
        width_px = int(80 * mm_to_inches * dpi)  # 80mm width
        height_px = int(50 * mm_to_inches * dpi)  # 50mm height

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory created: {output_dir}")

        # Set the path for the barcode image
        barcode_path = os.path.join(output_dir, f"{serial_number}_barcode")
        print(f"Expected barcode path: {barcode_path}")

        # Generate the barcode image
        writer_options = {
            "module_width": 0.2,  # Thinner lines
            "module_height": 15.0,  # Adjust height
            "quiet_zone": 6.5,  # Space around barcode
        }
        barcode = Code128(serial_number, writer=ImageWriter())
        barcode.save(barcode_path, options=writer_options)

        # Check if the file was created
        barcode_path_with_extension = f"{barcode_path}.png"
        if not os.path.exists(barcode_path_with_extension):
            raise FileNotFoundError(f"Expected file not found: {barcode_path_with_extension}")

        print(f"Barcode saved at: {barcode_path_with_extension}")

        # Open the generated barcode image
        barcode_img = Image.open(barcode_path_with_extension)

        # Create a new image with the target dimensions
        result_img = Image.new("RGB", (width_px, height_px), "white")

        # Resize the barcode to fit within the label (maintain aspect ratio)
        barcode_img_width, barcode_img_height = barcode_img.size
        max_width = width_px - 100  # Leave padding
        max_height = height_px - 150  # Leave space for text
        scale = min(max_width / barcode_img_width, max_height / barcode_img_height)
        resized_barcode = barcode_img.resize(
            (int(barcode_img_width * scale), int(barcode_img_height * scale)), Image.Resampling.NEAREST
        )

        # Center the barcode on the label
        barcode_x = (width_px - resized_barcode.size[0]) // 2
        barcode_y = 80  # Add space at the top for the label text
        result_img.paste(resized_barcode, (barcode_x, barcode_y))

        # Draw text labels (Model and Serial Number)
        draw = ImageDraw.Draw(result_img)
        try:
            font = ImageFont.truetype("Arial.ttf", 32)  # Font size for better readability
        except IOError:
            font = ImageFont.load_default()

        # Draw the label text at the top
        label_text_y = 20
        bbox_label = draw.textbbox((0, 0), label_text, font=font)
        label_width = bbox_label[2] - bbox_label[0]
        label_position = ((width_px - label_width) // 2, label_text_y)
        draw.text(label_position, label_text, fill="black", font=font)

        # Draw the serial number below the barcode
        serial_text = f"SN: {serial_number}"
        serial_text_y = barcode_y + resized_barcode.size[1] + 20
        bbox_serial = draw.textbbox((0, 0), serial_text, font=font)
        serial_width = bbox_serial[2] - bbox_serial[0]
        serial_position = ((width_px - serial_width) // 2, serial_text_y)
        draw.text(serial_position, serial_text, fill="black", font=font)

        # Rotate the final image by 90 degrees
        rotated_result_img = result_img.rotate(90, expand=True)

        # Save the final labeled barcode image
        output_path = os.path.join(output_dir, f"{serial_number}_labeled.png")
        rotated_result_img.save(output_path, format="PNG", dpi=(dpi, dpi))  # Ensure high DPI
        print(f"Barcode with label for '{serial_number}' saved at: {output_path}")

        # Remove the intermediate barcode image
        os.remove(barcode_path_with_extension)

        return output_path

    except Exception as e:
        print(f"An error occurred while generating the barcode: {e}")
        return None



def remove_original_barcode(barcode_path):
    """Remove the temporary barcode image."""
    try:
        original_barcode_path = f"{barcode_path}.png"
        if os.path.exists(original_barcode_path):
            os.remove(original_barcode_path)
    except Exception as e:
        print(f"Error removing original barcode: {e}")

# Function to send barcodes directly to the printer
def print_barcodes_directly(barcode_paths):
    try:
        for barcode_path in barcode_paths:
            print(f"Sending {barcode_path} to the printer...")
            subprocess.run([
                "lp",
                "-o", "media=Custom.80x50mm",
                "-o", "orientation-requested=4",
                barcode_path
            ], check=True)
        print("All barcodes have been sent to the printer.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to print {barcode_path}: {e}")
    except Exception as e:
        print(f"An error occurred during printing: {e}")

# Main function
def main():
    airpods_serials = get_airpods_serial()
    print(f"AirPods Serial Numbers: {airpods_serials}")

    components = {
        "case": "AirPods Pro - Case",
        "left": "AirPods Pro - Left Earpiece",
        "right": "AirPods Pro - Right Earpiece"
    }

    barcode_paths = []
    for key, name in components.items():
        serial_number = airpods_serials.get(key, "Not Found")
        if serial_number != "Not Found":
            label_text = f"{name}"  # Only display component name (no serial number)
            print(f"Generating barcode for {name}")
            barcode_path = generate_barcode_with_label(serial_number, label_text)
            if barcode_path:
                barcode_paths.append(barcode_path)
        else:
            print(f"Serial number for {name} not found, skipping.")

    if barcode_paths:
        print("Sending barcodes directly to the printer...")
        print_barcodes_directly(barcode_paths)
    else:
        print("No barcodes to print.")

if __name__ == "__main__":
    main()
