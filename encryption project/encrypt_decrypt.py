from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import numpy as np
import os, pathlib

# ---------- Core functions ----------

def encrypt_image(img_path: str, key: bytes) -> str:
    """Encrypt an image, return the path of the encrypted file."""
    img = Image.open(img_path).convert("RGB")
    flat_data = np.asarray(img).tobytes()

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(flat_data, AES.block_size))

    out_file = pathlib.Path(img_path).with_suffix(".enc").name
    with open(out_file, "wb") as f:
        f.write(cipher.iv + ciphertext)

    print(f"✅ Encrypted → {out_file}")
    return out_file, img.size, img.height      # keep shape info

def decrypt_image(enc_file: str, key: bytes, shape: tuple,
                  out_path: str = "decrypted_image.png") -> str:
    """Decrypt and rebuild image, return the path of the decrypted image."""
    with open(enc_file, "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

    arr = np.frombuffer(decrypted, dtype=np.uint8).reshape(shape)
    Image.fromarray(arr).save(out_path)
    print(f"✅ Decrypted → {out_path}")
    return out_path

def compare_images(path1: str, path2: str) -> None:
    """Byte‑level comparison of two files."""
    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        bytes1, bytes2 = f1.read(), f2.read()

    if bytes1 == bytes2:
        print("🎉 Files are IDENTICAL – encryption/decryption works!")
    else:
        print("⚠️  Files differ – something’s wrong.")

# ---------- Demo run ----------

if __name__ == "__main__":
    KEY = get_random_bytes(16)                 # 128‑bit AES key
    ORIGINAL = "test_image.png"                # supply your own image here

    enc_path, (width, _), height = encrypt_image(ORIGINAL, KEY)
    shape = (height, width, 3)                 # rows, cols, channels (3)

    dec_path = decrypt_image(enc_path, KEY, shape)
    compare_images(ORIGINAL, dec_path)

    # Optional: try decrypting with a wrong key to see failure
    wrong_key = get_random_bytes(16)
    decrypt_image(enc_path, wrong_key, shape, "wrong_output.png")
