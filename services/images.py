import hashlib
import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000

def validate_image(data: bytes):
    if not data or len(data) > MAX_BYTES:
        raise ValueError("ไฟล์ต้องมีข้อมูลและมีขนาดไม่เกิน 10 MB")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as probe:
                if probe.format not in ('JPEG', 'PNG'):
                    raise ValueError('รองรับเฉพาะไฟล์ JPG และ PNG จริงเท่านั้น')
                if probe.width * probe.height > MAX_PIXELS or min(probe.size) < 32:
                    raise ValueError('ภาพต้องกว้างและสูงอย่างน้อย 32 px และไม่เกิน 20 ล้านพิกเซล')
                probe.verify()
            with Image.open(io.BytesIO(data)) as source:
                image = ImageOps.exif_transpose(source).convert('RGB')
                image.thumbnail((1600, 1600))
                image.load()
        return image, hashlib.sha256(data).hexdigest()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError('อ่านภาพไม่ได้ ไฟล์อาจเสียหรือใหญ่เกินกำหนด') from exc
