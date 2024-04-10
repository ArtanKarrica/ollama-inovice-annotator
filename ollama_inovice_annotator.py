import re
import pandas as pd
import json
import os
import glob
import logging
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfFileReader
from ollama import generate  # Import the Ollama API client

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_value(pattern, text, default=None):
    """ Helper function to extract value using regex or return a default value. """
    match = pattern.search(text)
    return match.group(1).strip() if match else default

def parse_full_response(full_response):
    try:
        response_json = json.loads(full_response)

        total_amount = response_json.get("total_amount_due", "0").replace(" CHF", "").replace(',', '.')
        currency = response_json.get("currency_type", "CHF")
        description = response_json.get("transaction_description", "Unknown")
        invoice_date = response_json.get("invoice_receipt_creation_date", "Date not fully visible")
        is_invoice_receipt = 'Yes' if response_json.get("verification_of_document_type", "No") == "Yes" else 'No'
        confidence = response_json.get("confidence_in_accuracy", "Unknown")

        return total_amount, currency, description, invoice_date, is_invoice_receipt, confidence
    except Exception as e:
        logging.error(f"Error parsing response: {e}")
        return 'Error', 'Error', 'Error', 'Error', 'Error', 'Error'


def load_or_create_dataframe(filename):
    try:
        if os.path.isfile(filename):
            df = pd.read_csv(filename)
            if 'image_file' not in df.columns:
                df['image_file'] = pd.Series(dtype=str)
            df.set_index('image_file', inplace=True)
        else:
            df = pd.DataFrame(columns=['image_file', 'description', 'total_amount', 'currency', 'invoice_date', 'is_invoice_receipt', 'confidence'])
            df.set_index('image_file', inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error loading or creating DataFrame: {e}")
        return pd.DataFrame(columns=['image_file', 'description', 'total_amount', 'currency', 'invoice_date', 'is_invoice_receipt', 'confidence'])


df = load_or_create_dataframe('image_descriptions.csv')

def get_png_files(folder_path):
    return glob.glob(f"{folder_path}/*.png")

image_files = get_png_files("./images")
image_files.sort()

def process_image(image_file):
    print(f"\nProcessing {image_file}\n")
    try:
        image_bytes_list = []

        if image_file.lower().endswith('.pdf'):
            with open(image_file, "rb") as f:
                pdf = PdfFileReader(f)
                for page_num in range(pdf.numPages):
                    page = pdf.getPage(page_num)
                    pdf_writer = PyPDF2.PdfFileWriter()
                    pdf_writer.addPage(page)

                    with BytesIO() as pdf_buffer:
                        pdf_writer.write(pdf_buffer)
                        pdf_buffer.seek(0)
                        with Image.open(pdf_buffer) as img:
                            with BytesIO() as image_buffer:
                                img.save(image_buffer, format='PNG')
                                image_bytes = image_buffer.getvalue()
                                image_bytes_list.append(image_bytes)
        else:
            with Image.open(image_file) as img:
                with BytesIO() as buffer:
                    img.save(buffer, format='PNG')
                    image_bytes = buffer.getvalue()
                    image_bytes_list.append(image_bytes)

        full_response = ''
        confidence_prompt = 'Provide a confidence percentage (0-100%) regarding the accuracy of the summarized details.'
        analysis_prompt = (
            'Extract and analyze the text from the provided invoice/receipt image and respond in JSON format. '
            'Ensure accuracy and structure the response as follows:\n\n'
            '{\n'
            '  "total_amount_due": "[Specify the total amount with decimal places and currency, e.g., 50.00 CHF]",\n'
            '  "currency_type": "[Insert the currency code, e.g., CHF, USD, EUR]",\n'
            '  "transaction_description": "[Insert a brief summary of the expense type, e.g., Lunch, Flight, Dinner, etc.]",\n'
            '  "invoice_receipt_creation_date": "[State the date as MM/DD/YYYY]",\n'
            '  "verification_of_document_type": "[State Yes or No]",\n'
            '  "confidence_in_accuracy": "[Insert your confidence level as a percentage, e.g., 95%]"\n'
            '}\n\n'
        )

        for image_bytes in image_bytes_list:
            for response in generate(model='llava:13b-v1.6',
                                     prompt=analysis_prompt + confidence_prompt,
                                     images=[image_bytes],
                                     format='json',
                                     stream=True):
                print(response['response'], end='', flush=True)
                full_response += response['response']

        return parse_full_response(full_response)
    except Exception as e:
        logging.error(f"Error processing image {image_file}: {e}")
        return None, None, None, None, None, None

for image_file in image_files:
    if image_file not in df.index:
        total_amount, currency, description, invoice_date, is_invoice_receipt, confidence = process_image(image_file)
        logging.info(f"Extracted Data - Total amount: {total_amount}, Currency: {currency}, Description: {description}, Invoice date: {invoice_date}, Is invoice/receipt: {is_invoice_receipt}, Confidence: {confidence}")
        if description and description != 'Error':
            df.loc[image_file] = [description, total_amount, currency, invoice_date, is_invoice_receipt, confidence]

df.to_csv('image_descriptions.csv')

