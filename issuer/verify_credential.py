#!/usr/bin/env python3
"""
Credential verification script for circom playground.
Verifies credentials signed by the issuer.
"""

import os
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

def load_public_keys():
    """Load all public cryptographic material from ./creds directory."""
    print("Loading public cryptographic material...")

    # Load issuer public key
    with open("./creds/issuer_public_key.pem", "rb") as f:
        issuer_public_key = serialization.load_pem_public_key(f.read())

    # Load device public keys
    device_public_keys = {}
    i = 0
    while True:
        device_key_path = f"./creds/device_{i}_public_key.pem"
        if not os.path.exists(device_key_path):
            break

        with open(device_key_path, "rb") as f:
            device_public_keys[i] = serialization.load_pem_public_key(f.read())
        i += 1

    print(f"Loaded issuer key and {len(device_public_keys)} device keys")
    return issuer_public_key, device_public_keys

def verify_json_credential(filename):
    """Verify a JSON credential signature."""
    print(f"Verifying JSON credential: {filename}")

    # Load public keys
    issuer_public_key, _ = load_public_keys()

    # Read JSON credential
    with open(filename, 'r') as f:
        credential = json.load(f)

    # Extract signature
    signature_hex = credential.pop('signature')
    signature = bytes.fromhex(signature_hex)

    # Create credential bytes for verification (same as creation)
    credential_bytes = json.dumps(credential, sort_keys=True).encode()

    # Verify signature
    try:
        issuer_public_key.verify(signature, credential_bytes, ec.ECDSA(hashes.SHA256()))
        print(f"✓ JSON credential signature is VALID")
        return True
    except Exception as e:
        print(f"✗ JSON credential signature is INVALID: {e}")
        return False

def verify_binary_credential(filename):
    """Verify a binary credential signature."""
    print(f"Verifying binary credential: {filename}")

    # Load public keys
    issuer_public_key, _ = load_public_keys()

    # Read binary credential
    with open(filename, 'rb') as f:
        credential_data = f.read()

    # Parse binary credential structure (241 bytes total)
    # firstname: 32 bytes, lastname: 32 bytes, date_of_birth: 8 bytes,
    # salt: 32 bytes, device_key: 65 bytes, end_of_validity: 8 bytes,
    # signature: 64 bytes

    if len(credential_data) != 241:
        print(f"✗ Invalid binary credential length: {len(credential_data)} (expected 241)")
        return False

    # Extract signature (last 64 bytes)
    signature_bytes = credential_data[-64:]
    credential_without_sig = credential_data[:-64]

    # Convert signature from r,s format to DER format
    r = int.from_bytes(signature_bytes[:32], 'big')
    s = int.from_bytes(signature_bytes[32:], 'big')
    signature = encode_dss_signature(r, s)

    # Verify signature
    try:
        issuer_public_key.verify(signature, credential_without_sig, ec.ECDSA(hashes.SHA256()))
        print(f"✓ Binary credential signature is VALID")
        return True
    except Exception as e:
        print(f"✗ Binary credential signature is INVALID: {e}")
        return False

def main():
    """Main entry point for credential verification."""
    print("Credential verification script")

    # Example usage - verify all credentials
    print("\n=== Verifying JSON credentials ===")
    for i in range(3):
        json_file = f"./creds/json/credential_{i}.json"
        if os.path.exists(json_file):
            verify_json_credential(json_file)

    print("\n=== Verifying binary credentials ===")
    for i in range(3):
        bin_file = f"./creds/fixed/credential_{i}.bin"
        if os.path.exists(bin_file):
            verify_binary_credential(bin_file)

if __name__ == "__main__":
    main()