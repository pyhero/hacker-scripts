import io
import gzip
import json
import base64
import qrcode
import qrcode.image.svg


class QRCode(object):
    def __init__(
            self, data,
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,
            fit=False, method=None,
            compress_switch=False,
            print_switch=False
        ):
        """
        Desc: no exception logger
        Args:
            data: json data.
            version: An integer from 1 to 40 that controls the size of the QR Code (the smallest, version 1, is a 21x21 matrix).
                Set to None and use the fit parameter when making the code to determine this automatically.
            error_correction: The error_correction parameter controls the error correction used for the QR Code.
                The following four constants are made available on the qrcode package:
                ERROR_CORRECT_L: About 7% or less errors can be corrected.
                ERROR_CORRECT_M (default): About 15% or less errors can be corrected.
                ERROR_CORRECT_Q: About 25% or less errors can be corrected.
                ERROR_CORRECT_H. About 30% or less errors can be corrected.
            box_size: The box_size parameter controls how many pixels each “box” of the QR code is.
            border: The border parameter controls how many boxes thick the border should be (the default is 4, which is the minimum according to the specs).
            fit: Set version to None and use the fit parameter when making the code to determine size automatically.
            method: SVG method
                basic: Simple factory, just a set of rects.
                fragment: Fragment factory (also just a set of rects)
                other: Combined path factory, fixes white space that may occur when zooming

        Returns: None
        """

        self.data = data
        self.version = version
        self.error_correction = error_correction
        self.box_size = box_size
        self.border = border
        self.fit = fit
        self.method = method
        self.compress_switch = compress_switch
        self.print_switch = print_switch

        self.qr = self.__init_qrcode()

    def compress(self, data):
        if type(data) != str:
            data = json.dumps(data)

        _compressed_data = gzip.compress(data.encode(encoding='utf-8'))
        _base64_data = base64.b64encode(_compressed_data).decode('utf-8')

        return _base64_data
    
    def decompress(self, compressed_data):
        _base64_data = base64.b64decode(compressed_data)
        decompressed_data = gzip.decompress(_base64_data).decode(encoding='utf-8')

        return decompressed_data

    def __init_qrcode(self):
        qr = qrcode.QRCode(
            version=self.version if not self.fit else None,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )

        qr.clear()

        data = self.compress(self.data) if self.compress_switch else self.data

        qr.add_data(data)
        qr.make(fit=self.fit)

        return qr

    def get_well_matched_version_number(self):
        return self.qr.version

    def creat_qrcode_txt(self, save_path='/tmp/qrcode.txt'):
        f = io.StringIO()
        self.qr.print_ascii(out=f)
        f.seek(0)
        qrcode_txt = f.read()
        
        with open(save_path, 'w', encoding='utf-8') as ff:
            ff.write(qrcode_txt)

        return save_path

    def create_qrcode_png(self, save_path='/tmp/qrcode.png'):
        img = self.qr.make_image(fill_color="black", back_color="white")

        img.save(save_path)

        return save_path


if __name__ == "__main__":
    data = {"name": "Panda", "sex": "male", "age": 17, "job": "Engineer"}
    qr = QRCode(data, fit=True, compress_switch=True)

    # create qrcode
    print(qr.creat_qrcode_txt())
    print(qr.create_qrcode_png())

    # version size
    print(qr.get_well_matched_version_number())
