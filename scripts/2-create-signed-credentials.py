#!/usr/bin/env python3
"""
Create and sign a credential with issuer's private key.
"""

import hashlib
import json
import random
import common
from datetime import datetime
import os


def create_credential(first_name, last_name, date_of_birth, keys_device):
    """Create a credential structure.
    It also generates a fixed challenge supposed to be given by the verifier.
    Then it adds the signature of the device key on this challenge.
    """
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    birth_timestamp = int(birth_date.timestamp())

    return {
        "first_name": first_name,
        "last_name": last_name,
        "birth_timestamp": birth_timestamp,
        "device_key_x": keys_device["public_key_x"],
        "device_key_y": keys_device["public_key_y"],
    }


def sign_store_fixed(dirname, label, credential, key_private_issuer):
    """Create a representation of the fields with fixed-size widths, sign it, and store it
    under the label in dirname."""
    first_name_fixed = credential["first_name"].ljust(32, " ")[:32]
    last_name_fixed = credential["last_name"].ljust(32, " ")[:32]
    birth_timestamp_str = str(credential["birth_timestamp"]).rjust(10, "0")

    credential_string = first_name_fixed + last_name_fixed + birth_timestamp_str
    signature = key_private_issuer.sign_recoverable(credential_string.encode("utf-8"))[
        :64
    ]

    filename = f"credential_fixed_{label}.json"
    with open(os.path.join(dirname, filename), "w") as f:
        json.dump(
            {
                "credential_string": credential_string,
                # "message_hash": message_hash,
                "signature_issuer": f"0x{signature.hex()}",
            },
            f,
            indent=2,
        )
    print(f"Signed and stored {filename}...")


def sign_store_fixed_device(
    dirname, label, credential, key_private_issuer, keys_device
):
    """Create a representation of the fields with fixed-size widths, sign it, and store it
    under the label in dirname."""
    first_name_fixed = credential["first_name"].ljust(32, " ")[:32]
    last_name_fixed = credential["last_name"].ljust(32, " ")[:32]
    birth_timestamp_str = str(credential["birth_timestamp"]).rjust(10, "0")
    device_key_x = str(credential["device_key_x"]).rjust(64, "0")
    device_key_y = str(credential["device_key_y"]).rjust(64, "0")

    credential_string = (
        first_name_fixed
        + last_name_fixed
        + birth_timestamp_str
        + device_key_x
        + device_key_y
    )
    print("Credential string length:", len(credential_string))
    signature_issuer = key_private_issuer.sign_recoverable(
        credential_string.encode("utf-8")
    )[:64]
    challenge = random.randbytes(32)
    challenge_hash = hashlib.sha256(challenge).digest()
    signature_device = keys_device["private_key_obj"].sign_recoverable(challenge)[:64]

    filename = f"credential_device_fixed_{label}.json"
    with open(os.path.join(dirname, filename), "w") as f:
        json.dump(
            {
                "credential_string": credential_string,
                "signature_issuer": f"0x{signature_issuer.hex()}",
                "challenge": f"0x{challenge.hex()}",
                "challenge_hash": f"0x{challenge_hash.hex()}",
                "signature_device": f"0x{signature_device.hex()}",
            },
            f,
            indent=2,
        )
    print(f"Signed and stored {filename}...")


if __name__ == "__main__":
    KEY_DIR = common.parse_args("Create credentials.")
    key_private_issuer = common.load_issuer_keys(KEY_DIR)["private_key_obj"]
    keys_device_alice = common.load_device_keys(KEY_DIR, "alice")
    keys_device_bob = common.load_device_keys(KEY_DIR, "bob")

    # Create sample credentials
    alice = create_credential(
        first_name="Alice",
        last_name="Smith",
        date_of_birth="2000-05-15",
        keys_device=keys_device_alice,
    )
    bob = create_credential(
        first_name="Bob",
        last_name="Berg",
        date_of_birth="2010-05-15",
        keys_device=keys_device_bob,
    )

    sign_store_fixed(KEY_DIR, "alice", alice, key_private_issuer)
    sign_store_fixed(KEY_DIR, "bob", bob, key_private_issuer)
    sign_store_fixed_device(
        KEY_DIR, "alice", alice, key_private_issuer, keys_device_alice
    )
    sign_store_fixed_device(KEY_DIR, "bob", bob, key_private_issuer, keys_device_bob)
