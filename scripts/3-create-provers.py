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
            # cred_bytes = cred["credential_string"].encode("utf-8")
            # print(f"Hash is: {hashlib.sha256(cred_bytes).hexdigest()}")
            # ok = pubkey.verify(
            #     bytes.fromhex(cred["signature"]),
            #     cred_bytes,
            #     hashfunc=hashlib.sha256,
            # )
            # print(f"Verifying {cred['credential_string'][0:5]}: {ok}")
            credentials_fixed.append(cred)

    circuits_fixed = [
        d for d in glob.glob(os.path.join(CIRCUIT_DIR, "*_fixed_*")) if os.path.isdir(d)
    ]
    time_now = int(datetime(2025, 11, 6, 18, 20).timestamp())
    if circuits_fixed:
        prover_fixed(time_now, pubkey_issuer_xy, credentials_fixed, circuits_fixed)
