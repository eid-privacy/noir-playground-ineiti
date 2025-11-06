#!/usr/bin/env python3
"""
Generate secp256k1 ECDSA key pair for credential issuer.
Outputs the keys in formats suitable for Noir circuit inputs.
"""

from common import parse_args
from ecdsa import SigningKey, SECP256k1
import os


def generate_issuer_keys():
    """Generate a new secp256k1 key pair for the issuer."""
    # Generate random private key
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()

    # Get raw private key bytes (32 bytes)
    private_key_bytes = private_key.to_string()

    # Get public key coordinates (32 bytes each for x and y)
    public_key_point = public_key.pubkey.point
    x_coord = public_key_point.x().to_bytes(32, byteorder="big")
    y_coord = public_key_point.y().to_bytes(32, byteorder="big")

    return {
        "private_key": private_key_bytes.hex(),
        "public_key_x": x_coord.hex(),
        "public_key_y": y_coord.hex(),
        "private_key_obj": private_key,  # For signing operations
        "public_key_obj": public_key,  # For verification operations
    }


def save_keys_to_file(keys, filename="issuer_keys.json"):
    """Save keys to JSON file (excluding the key objects)."""
    import json

    key_data = {
        "private_key": keys["private_key"],
        "public_key_x": keys["public_key_x"],
        "public_key_y": keys["public_key_y"],
    }

    with open(filename, "w") as f:
        json.dump(key_data, f, indent=2)

    print(f"Keys saved to {filename}")


if __name__ == "__main__":
    KEY_DIR = parse_args("Generate secp256k1 issuer key pair.")
    os.makedirs(KEY_DIR, exist_ok=True)

    print("Generating secp256k1 issuer key pair...")

    keys = generate_issuer_keys()
    save_keys_to_file(keys, os.path.join(KEY_DIR, "issuer_keys.json"))
