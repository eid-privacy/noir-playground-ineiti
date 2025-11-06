#!/usr/bin/env python3
"""
Create and sign a credential with issuer's private key.
"""

import hashlib
import json
import common
from datetime import datetime
from ecdsa.util import sigencode_string
import os


def create_credential(first_name, last_name, date_of_birth):
    """Create a credential structure."""
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    birth_timestamp = int(birth_date.timestamp())

    return {
        "first_name": first_name,
        "last_name": last_name,
        "birth_timestamp": birth_timestamp,
    }


def sign_store_fixed(dirname, label, credential, private_key_obj):
    """Create a representation of the fields with fixed-size widths, sign it, and store it
    under the label in dirname."""
    first_name_fixed = credential["first_name"].ljust(32, " ")[:32]
    last_name_fixed = credential["last_name"].ljust(32, " ")[:32]
    birth_timestamp_str = str(credential["birth_timestamp"]).rjust(10, "0")

    credential_string = first_name_fixed + last_name_fixed + birth_timestamp_str
    signature = private_key_obj.sign(
        credential_string.encode("utf-8"),
        hashfunc=hashlib.sha256,
    )

    print(f"Signed and storing {label}")
    with open(os.path.join(dirname, f"credential_fixed_{label}.json"), "w") as f:
        json.dump(
            {
                "credential_string": credential_string,
                # "message_hash": message_hash,
                "signature": signature.hex(),
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    KEY_DIR = common.parse_args("Create credentials.")
    keys = common.load_issuer_keys(KEY_DIR)["private_key_obj"]

    # Create sample credentials
    alice = create_credential(
        first_name="Alice",
        last_name="Smith",
        date_of_birth="2000-05-15",
    )
    bob = create_credential(
        first_name="Bob",
        last_name="Berg",
        date_of_birth="2010-05-15",
    )

    sign_store_fixed(KEY_DIR, "alice", alice, keys)
    sign_store_fixed(KEY_DIR, "bob", bob, keys)
