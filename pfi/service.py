import hashlib
from io import BytesIO
import frappe
import qrcode


@frappe.whitelist(allow_guest=True)
def generate_barcode(item_code, barcode_type="Code128", width=0.4, height=None, scale=None):
    # Write to a file-like object:
    # Or to an actual file:
    from barcode import Code128
    from barcode.writer import SVGWriter
    filename = hashlib.md5(item_code.encode()).hexdigest()
    if barcode_type == "Code128":
        options = {
            'module_width': width,  # Lebar setiap modul (garis)
            'quiet_zone': 10       # Jarak kosong di sekitar barcode
        }
        with open("{}/public/files/barcode/{}.svg".format(frappe.local.site,filename), "wb") as f:
            Code128(str(item_code), writer=SVGWriter()).write(f, options)
            # return """<img src="http://localhost:8006/files/barcode/{}.svg" alt="barcode" style="width:100%;height:100%;">""".format(filename)
            return "/files/barcode/{}.svg".format(filename)
    else:
        raise Exception("Barcode type not supported")

def generate_qr_code(item_code):
    qr = qrcode.QRCode(
        version=1,  # Versi QR Code (1-40), semakin besar semakin besar ukuran QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Tingkat koreksi kesalahan
        box_size=10,  # Ukuran setiap "box" (piksel) dalam QR Code
        border=1,  # Ukuran margin (border) dalam "box" (piksel)
    )

    qr.add_data(item_code)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    filename = hashlib.md5(item_code.encode()).hexdigest()
    img.save("{}/public/files/barcode/{}.png".format(frappe.local.site,filename))
    return "/files/barcode/{}.png".format(filename)
    # return """<img src="/files/barcode/{}.png" alt="barcode" style="width:100%;height:100%;">""".format(filename)

@frappe.whitelist()


def generate_barcode_svg(item_code, barcode_type="Code128", width=0.2, scale=1.0):
    import re
    from io import BytesIO
    from barcode import Code128
    from barcode.writer import SVGWriter
    
    if barcode_type != "Code128":
        raise Exception("Only Code128 is currently supported")

    options = {
        "module_width": width,
        "quiet_zone": 1,
        "write_text": True,
        "text_distance": 2,
        "module_height": 5,
        "font_size": 7
    }

    buffer = BytesIO()
    Code128(str(item_code), writer=SVGWriter()).write(buffer, options)
    svg_data = buffer.getvalue().decode("utf-8")
    buffer.close()

    # Remove XML header
    if svg_data.startswith("<?xml"):
        svg_data = svg_data.split("?>", 1)[1].strip()

    # Extract original width and height from <svg ...>
    match = re.search(r'<svg[^>]*width="([\d.]+)(mm|px)?"[^>]*height="([\d.]+)(mm|px)?"', svg_data)
    if not match:
        raise Exception("Could not find SVG width/height")

    original_width = float(match.group(1))
    original_height = float(match.group(3))

    scaled_width = original_width * scale
    scaled_height = original_height * scale

    # Inject new width/height + viewBox
    svg_data = re.sub(
        r'<svg[^>]*>',
        f'<svg width="{scaled_width}mm" height="{scaled_height}mm" viewBox="0 0 {original_width} {original_height}">',
        svg_data,
        count=1
    )

    # Optional: scale internal <g> for clarity (or skip if viewBox is enough)
    # svg_data = svg_data.replace("<g", f'<g transform="scale({scale})"', 1)

    return svg_data
