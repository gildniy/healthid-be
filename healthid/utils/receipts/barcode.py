import cloudinary
import barcode
from barcode.writer import ImageWriter
from random import randint


def generate_barcode(receipt, receipt_model):
    """
    generates a barcode for a receipt

    Args:
        receipt(obj): receipt whose barcode is being created for
        receipt_model: model of receipt

    Returns:
        string: url for barcode created
    """
    barcode_number = randint(100000000000, 999999999999)
    image = barcode.get_barcode_class('upca')
    receipt_instance = receipt_model.objects.filter(
        scanned_number=barcode_number)
    if receipt_instance.exists():
        return generate_barcode(receipt, receipt_model)
    barcode_image = image(str(barcode_number), writer=ImageWriter())
    filename = barcode_image.save('receipt')
    image_url = cloudinary.uploader.upload(filename).get('url')
    receipt.scanned_number = barcode_number
    return image_url


def generate_receipt_number(receipt, receipt_model):
    """
    generates a unique number for a receipt

    Args:
        receipt(obj): receipt whose reciept no is being created for
        receipt_model: model of receipt

    Returns:
        string: unique characters for receipt
    """
    receipt_no = f'RN{randint(100, 999)}-{receipt.sale.id}'
    receipts = receipt_model.objects.filter(receipt_no=receipt_no)
    if receipts.exists():
        return generate_receipt_number(receipt, receipt_model)
    return receipt_no
