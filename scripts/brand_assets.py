"""Generate Microsoft Store images from the exact reviewed conch icon in this repo."""
from pathlib import Path
import hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
ICON=ROOT/'branding'/'keyswebit.ico'
EXPECTED_SHA256='b4a111e9a6eec2d03b552ebc54061b93bccb4c24847c0ad26667106aab944fd7'
raw=ICON.read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA256, 'Branded icon changed; review before updating checksum'
im=Image.open(ICON).convert('RGBA')
a=ROOT/'branding'/'store';a.mkdir(exist_ok=True)
for name,dim in [('StoreLogo.png',50),('Square44x44Logo.png',44),('Square150x150Logo.png',150),('Square310x310Logo.png',310)]:
    im.resize((dim,dim),Image.Resampling.LANCZOS).save(a/name)
print('Generated Store imagery from pinned official conch icon.')
