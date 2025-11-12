#!/usr/bin/env python3

import hashlib
import json
import toml
from datetime import datetime
import os
import common
import glob


def prover_fixed(time_now, pubkey_issuer, credentials, dirnames):
    for dir in dirnames:
        for i, cred in enumerate(credentials):
            print(f"Storing to {dir}/Prover_{i}: {cred['credential_string'][0:5]}")
            with open(os.path.join(dir, f"Prover_{i}.toml"), "w") as f:
                toml.dump(
                    {
                        "current_date": time_now,
                        "pubkey_issuer_x": pubkey_issuer[0],
                        "pubkey_issuer_y": pubkey_issuer[1],
                        "credential_raw": cred["credential_string"].encode("utf-8"),
                        "signature": bytes.fromhex(cred["signature"]),
                    },
                    f,
                )


def verify_credential(cred):
    cred_bytes = cred["credential_string"].encode("utf-8")
    message_hash = hashlib.sha256(cred_bytes).digest()
    signature_bytes = bytes.fromhex(cred["signature"])
    print(f"Credential: {cred['credential_string'][0:5]}...")
    print(f"  Hash: {message_hash.hex()}")

    # Verify signature cryptographically
    r = int.from_bytes(signature_bytes[:32], "big")
    s = int.from_bytes(signature_bytes[32:], "big")

    # Convert compact signature (r||s) to DER format for verification
    def encode_der_integer(value):
        """Encode an integer as DER format"""
        value_bytes = value.to_bytes(32, "big").lstrip(b"\x00") or b"\x00"
        if value_bytes[0] & 0x80:  # High bit set, need padding
            value_bytes = b"\x00" + value_bytes
        return bytes([0x02, len(value_bytes)]) + value_bytes

    r_der = encode_der_integer(r)
    s_der = encode_der_integer(s)
    der_sig = bytes([0x30, len(r_der) + len(s_der)]) + r_der + s_der

    try:
        pubkey.verify(der_sig, message_hash, hasher=None)
        print("  Signature verification: PASSED")
    except Exception as e:
        print(f"  Signature verification: FAILED ({e})")


if __name__ == "__main__":
    print("Creating various credentials and sign them...")
    [KEY_DIR, CIRCUIT_DIR] = common.parse_args("Create credentials.", True)
    keys = common.load_issuer_keys(KEY_DIR)
    pubkey_issuer_xy = [
        bytes.fromhex(keys["public_key_x"]),
        bytes.fromhex(keys["public_key_y"]),
    ]
    pubkey = keys["public_key_obj"]
    print(keys["public_key_x"])
    print(keys["public_key_y"])

    pattern = os.path.join(KEY_DIR, "credential_fixed_*.json")
    credentials_fixed = []
    for cred_path in sorted(glob.glob(pattern)):
        with open(cred_path, "r", encoding="utf-8") as f:
            cred = json.loads(f.read())
            credentials_fixed.append(cred)
            # verify_credential(cred)

    circuits_fixed = [
        d for d in glob.glob(os.path.join(CIRCUIT_DIR, "*_fixed_*")) if os.path.isdir(d)
    ]
    time_now = int(datetime(2025, 11, 6, 18, 20).timestamp())
    if circuits_fixed:
        prover_fixed(time_now, pubkey_issuer_xy, credentials_fixed, circuits_fixed)
