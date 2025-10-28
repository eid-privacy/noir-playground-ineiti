#!/usr/bin/env python3
"""
Create and sign a credential with issuer's private key.
Generate inputs for the Noir circuit.
"""

import hashlib
import json
import time
from datetime import datetime
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_string

def load_issuer_keys(filename='scripts/issuer_keys.json'):
    """Load issuer keys from JSON file."""
    try:
        with open(filename, 'r') as f:
            keys = json.load(f)

        # Reconstruct the SigningKey object
        private_key_bytes = bytes.fromhex(keys['private_key'])
        private_key_obj = SigningKey.from_string(private_key_bytes, curve=SECP256k1)

        keys['private_key_obj'] = private_key_obj
        return keys
    except FileNotFoundError:
        print("❌ Error: issuer_keys.json not found. Run generate_keys.py first.")
        exit(1)

def create_credential(first_name, last_name, date_of_birth):
    """Create a credential structure."""
    # Convert date of birth to Unix timestamp
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    birth_timestamp = int(birth_date.timestamp())

    credential = {
        'first_name': first_name,
        'last_name': last_name,
        'date_of_birth': date_of_birth,
        'birth_timestamp': birth_timestamp
    }

    return credential

def hash_credential(credential):
    """Create SHA256 hash of credential for signing."""
    # Create a deterministic string representation
    credential_string = f"{credential['first_name']},{credential['last_name']},{credential['birth_timestamp']}"

    # Hash the credential
    credential_bytes = credential_string.encode('utf-8')
    credential_hash = hashlib.sha256(credential_bytes).digest()

    return credential_hash, credential_string

def sign_credential(credential_hash, private_key_obj):
    """Sign the credential hash with the issuer's private key."""
    # Sign the hash (returns r, s as 32-byte values)
    signature = private_key_obj.sign(credential_hash, sigencode=sigencode_string)

    # Extract r and s (each 32 bytes)
    r = signature[:32]
    s = signature[32:]

    # Check s malleability (s should be <= order/2)
    order = SECP256k1.order
    s_int = int.from_bytes(s, byteorder='big')
    if s_int > order // 2:
        # Make s canonical by computing order - s
        s_int = order - s_int
        s = s_int.to_bytes(32, byteorder='big')

    # Combine r and s for 64-byte signature
    full_signature = r + s

    return full_signature, r, s

def format_inputs_for_noir(credential_hash, credential, signature, keys, current_timestamp, min_age=18):
    """Format all inputs for the Noir circuit."""

    # Format credential hash as byte array
    hash_bytes = [f"0x{credential_hash.hex()[i:i+2]}" for i in range(0, 64, 2)]

    # Format credential name fields as byte arrays (padded to 32 bytes)
    first_name_bytes = []
    first_name_str = credential['first_name']
    for i in range(32):
        if i < len(first_name_str):
            first_name_bytes.append(f"0x{ord(first_name_str[i]):02x}")
        else:
            first_name_bytes.append("0x00")

    last_name_bytes = []
    last_name_str = credential['last_name']
    for i in range(32):
        if i < len(last_name_str):
            last_name_bytes.append(f"0x{ord(last_name_str[i]):02x}")
        else:
            last_name_bytes.append("0x00")

    # Format signature as byte array
    sig_bytes = [f"0x{signature.hex()[i:i+2]}" for i in range(0, 128, 2)]

    # Format public key coordinates
    pub_x_bytes = [f"0x{keys['public_key_x'][i:i+2]}" for i in range(0, 64, 2)]
    pub_y_bytes = [f"0x{keys['public_key_y'][i:i+2]}" for i in range(0, 64, 2)]

    return {
        'credential_hash': hash_bytes,
        'first_name_bytes': first_name_bytes,
        'last_name_bytes': last_name_bytes,
        'birth_timestamp': credential['birth_timestamp'],
        'signature': sig_bytes,
        'issuer_pub_key_x': pub_x_bytes,
        'issuer_pub_key_y': pub_y_bytes,
        'current_date': current_timestamp,
        'min_age': min_age
    }

def save_circuit_inputs(inputs, credential_info):
    """Save inputs to Prover.toml file."""

    # Write Prover.toml with all inputs (private and public)
    with open('age_verification/Prover.toml', 'w') as f:
        f.write("# Inputs for the age verification circuit\n")
        f.write(f"credential_hash = {inputs['credential_hash']}\n")
        f.write(f"first_name_bytes = {inputs['first_name_bytes']}\n")
        f.write(f"last_name_bytes = {inputs['last_name_bytes']}\n")
        f.write(f"birth_timestamp = {inputs['birth_timestamp']}\n")
        f.write(f"signature = {inputs['signature']}\n")
        f.write(f"issuer_pub_key_x = {inputs['issuer_pub_key_x']}\n")
        f.write(f"issuer_pub_key_y = {inputs['issuer_pub_key_y']}\n")
        f.write(f"current_date = {inputs['current_date']}\n")
        f.write(f"min_age = {inputs['min_age']}\n")

    # Save credential info for reference
    with open('scripts/credential_info.json', 'w') as f:
        json.dump(credential_info, f, indent=2)

    print("✅ Circuit inputs saved to age_verification/Prover.toml")

def verify_signature_python(credential_hash, signature, keys):
    """Verify the signature using Python ECDSA library for testing."""
    try:
        private_key_obj = keys['private_key_obj']
        public_key = private_key_obj.get_verifying_key()
        public_key.verify(signature, credential_hash)
        return True
    except:
        return False

if __name__ == "__main__":
    print("Creating and signing credential...")

    # Load issuer keys
    keys = load_issuer_keys()

    # Create sample credential
    credential = create_credential(
        first_name="Alice",
        last_name="Smith",
        date_of_birth="2000-05-15"  # 24 years old as of 2024
    )

    print(f"\n=== Credential ===")
    print(f"Name: {credential['first_name']} {credential['last_name']}")
    print(f"Date of Birth: {credential['date_of_birth']}")
    print(f"Birth Timestamp: {credential['birth_timestamp']}")

    # Hash the credential
    credential_hash, credential_string = hash_credential(credential)
    print(f"\nCredential String: {credential_string}")
    print(f"Credential Hash: 0x{credential_hash.hex()}")

    # Sign the credential
    signature, r, s = sign_credential(credential_hash, keys['private_key_obj'])
    print(f"\nSignature (64 bytes): 0x{signature.hex()}")
    print(f"r (32 bytes): 0x{r.hex()}")
    print(f"s (32 bytes): 0x{s.hex()}")

    # Verify signature with Python
    is_valid = verify_signature_python(credential_hash, signature, keys)
    print(f"Python signature verification: {'✅ VALID' if is_valid else '❌ INVALID'}")

    # Current timestamp and minimum age
    current_timestamp = int(time.time())
    min_age = 18

    # Calculate actual age
    age_seconds = current_timestamp - credential['birth_timestamp']
    age_years = age_seconds // (365.25 * 24 * 3600)  # Approximate

    print(f"\nCurrent timestamp: {current_timestamp}")
    print(f"Approximate age: {age_years:.1f} years")
    print(f"Age requirement: {min_age} years")
    print(f"Meets requirement: {'✅ YES' if age_years >= min_age else '❌ NO'}")

    # Format inputs for Noir circuit
    circuit_inputs = format_inputs_for_noir(
        credential_hash, credential, signature, keys, current_timestamp, min_age
    )

    # Save inputs to TOML files
    credential_info = {
        'credential': credential,
        'credential_string': credential_string,
        'credential_hash': credential_hash.hex(),
        'signature': signature.hex(),
        'current_timestamp': current_timestamp,
        'age_years': age_years,
        'meets_requirement': age_years >= min_age
    }

    save_circuit_inputs(circuit_inputs, credential_info)

    print(f"\n✅ Credential signed successfully!")
    print("Next: Implement the Noir circuit in age_verification/src/main.nr")