import argparse
import os
from ecdsa import SigningKey, SECP256k1
import json


def parse_args(description, circuit=False):
    parser = argparse.ArgumentParser(description)
    parser.add_argument(
        "key_dir", nargs="?", help="Destination directory to save issuer keys"
    )
    if circuit:
        parser.add_argument("circuit_dir", nargs="?", help="Circuit directory")

    args = parser.parse_args()
    if args.key_dir is None:
        print("Need to give a valid directory to save issuer keys")
        exit(1)

    if circuit:
        return [os.path.abspath(args.key_dir), os.path.abspath(args.circuit_dir)]
    else:
        return os.path.abspath(args.key_dir)


def load_issuer_keys(dirname):
    """Load issuer keys from JSON file."""
    try:
        with open(os.path.join(dirname, "issuer_keys.json"), "r") as f:
            keys = json.load(f)

        private_key_bytes = bytes.fromhex(keys["private_key"])
        keys["private_key_obj"] = SigningKey.from_string(
            private_key_bytes, curve=SECP256k1
        )
        keys["public_key_obj"] = keys["private_key_obj"].get_verifying_key()

        return keys

    except FileNotFoundError:
        print("❌ Error: issuer_keys.json not found. Run generate_keys.py first.")
        exit(1)
