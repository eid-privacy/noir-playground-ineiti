#!/usr/bin/env python3
"""
Credential creation script for circom playground.
Creates credentials with private/public key infrastructure.
"""

import os
import json
import secrets
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

# Static identities
IDENTITIES = [
    {
        "firstname": "Alice",
        "lastname": "Smith",
        "date_of_birth": 631152000  # January 1, 1990 (Unix timestamp)
    },
    {
        "firstname": "Bob",
        "lastname": "Johnson",
        "date_of_birth": 694224000  # January 1, 1992 (Unix timestamp)
    },
    {
        "firstname": "Charlie",
        "lastname": "Brown",
        "date_of_birth": 757382400  # January 1, 1994 (Unix timestamp)
    }
]

def setup_cryptography():
    """Set up cryptographic components: issuer keys, identity keys, and salts."""
    print("Setting up cryptographic components...")

    # Create creds directory structure
    os.makedirs("./creds", exist_ok=True)
    os.makedirs("./creds/json", exist_ok=True)
    os.makedirs("./creds/raw", exist_ok=True)

    # Generate issuer private/public key pair
    issuer_private_key = ec.generate_private_key(ec.SECP256R1())
    issuer_public_key = issuer_private_key.public_key()

    # Save issuer keys
    with open("./creds/issuer_private_key.pem", "wb") as f:
        f.write(issuer_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("./creds/issuer_public_key.pem", "wb") as f:
        f.write(issuer_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Generate keys and salts for each identity
    crypto_data = {}
    for i, identity in enumerate(IDENTITIES):
        # Generate device key pair
        device_private_key = ec.generate_private_key(ec.SECP256R1())
        device_public_key = device_private_key.public_key()

        # Generate 256-bit random salt
        salt = secrets.randbits(256)

        # Store crypto data
        crypto_data[i] = {
            "device_private_key": device_private_key,
            "device_public_key": device_public_key,
            "salt": salt
        }

        # Save device keys
        with open(f"./creds/device_{i}_private_key.pem", "wb") as f:
            f.write(device_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(f"./creds/device_{i}_public_key.pem", "wb") as f:
            f.write(device_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    return issuer_private_key, crypto_data

def create_json_credentials(issuer_private_key, crypto_data):
    """Create JSON format credentials."""
    print("Creating JSON credentials...")

    for i, identity in enumerate(IDENTITIES):
        # Create credential data
        credential = {
            "firstname": identity["firstname"],
            "lastname": identity["lastname"],
            "date_of_birth": identity["date_of_birth"],
            "salt": crypto_data[i]["salt"],
            "device_key": crypto_data[i]["device_public_key"].public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            ).hex(),
            "end_of_validity": int(datetime(2030, 12, 31).timestamp())
        }

        # Create signature over credential data
        credential_bytes = json.dumps(credential, sort_keys=True).encode()
        signature = issuer_private_key.sign(credential_bytes, ec.ECDSA(hashes.SHA256()))

        # Add signature to credential
        credential["signature"] = signature.hex()

        # Save JSON credential
        with open(f"./creds/json/credential_{i}.json", "w") as f:
            json.dump(credential, f, indent=2)

def create_raw_credentials(issuer_private_key, crypto_data):
    """Create raw format credentials."""
    print("Creating raw credentials...")

    for i, identity in enumerate(IDENTITIES):
        # Create raw binary credential data
        credential_binary = bytearray()

        # firstname - 32 bytes (UTF-8, null-padded)
        firstname_bytes = identity["firstname"].encode('utf-8')[:32]
        credential_binary.extend(firstname_bytes.ljust(32, b'\x00'))

        # lastname - 32 bytes (UTF-8, null-padded)
        lastname_bytes = identity["lastname"].encode('utf-8')[:32]
        credential_binary.extend(lastname_bytes.ljust(32, b'\x00'))

        # date_of_birth - 8 bytes (uint64, big-endian)
        credential_binary.extend(identity["date_of_birth"].to_bytes(8, 'big'))

        # salt - 32 bytes (256 bits)
        salt_bytes = crypto_data[i]["salt"].to_bytes(32, 'big')
        credential_binary.extend(salt_bytes)

        # device_key - 65 bytes (uncompressed P-256 public key)
        device_key_bytes = crypto_data[i]["device_public_key"].public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        credential_binary.extend(device_key_bytes)

        # end_of_validity - 8 bytes (uint64, big-endian)
        end_validity = int(datetime(2030, 12, 31).timestamp())
        credential_binary.extend(end_validity.to_bytes(8, 'big'))

        # Create signature over binary credential data
        signature = issuer_private_key.sign(bytes(credential_binary), ec.ECDSA(hashes.SHA256()))

        # signature - 64 bytes (r and s values, 32 bytes each)
        # Note: This is a simplified representation - actual DER encoding might vary
        from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
        r, s = decode_dss_signature(signature)
        signature_bytes = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
        credential_binary.extend(signature_bytes)

        # Save as binary file
        with open(f"./creds/raw/credential_{i}.bin", "wb") as f:
            f.write(credential_binary)

        # Save as hex file (same content as ASCII hex)
        with open(f"./creds/raw/credential_{i}.hex", "w") as f:
            f.write(credential_binary.hex())

def main():
    """Main entry point for credential creation."""
    print("Starting credential creation...")

    # Set up cryptographic components
    issuer_private_key, crypto_data = setup_cryptography()

    # Create JSON credentials
    create_json_credentials(issuer_private_key, crypto_data)

    # Create raw credentials
    create_raw_credentials(issuer_private_key, crypto_data)

    print("Credential creation completed!")

if __name__ == "__main__":
    main()