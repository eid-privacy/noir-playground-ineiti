import argparse
import os
from coincurve import PrivateKey
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


def load_keys(dirname, filename):
    """Load issuer keys from JSON file."""
    try:
        with open(os.path.join(dirname, filename), "r") as f:
            keys = json.load(f)

        private_key_bytes = bytes.fromhex(keys["private_key"])
        keys["private_key_obj"] = PrivateKey(private_key_bytes)
        keys["public_key_obj"] = keys["private_key_obj"].public_key

        return keys

    except FileNotFoundError:
        print(f"❌ Error: {filename} not found. Run 1-create-keys.py first.")
        exit(1)

def load_issuer_keys(dirname):
    """Load issuer keys from JSON file."""
    return load_keys(dirname, "keys_issuer.json")

def load_device_keys(dirname, label):
    """Load device keys from JSON file."""
    return load_keys(dirname, f"keys_device_{label}.json")
