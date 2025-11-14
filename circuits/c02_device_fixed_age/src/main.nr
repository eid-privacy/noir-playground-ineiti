use sha256::sha256_var;

global CREDENTIAL_LENGTH: u32 = 202;

fn main(
    // Private inputs - credential data
    credential_string: str<CREDENTIAL_LENGTH>,
    signature_issuer: [u8; 64],
    signature_device: [u8; 64],
    // Public inputs
    pubkey_issuer_x: pub [u8; 32],
    pubkey_issuer_y: pub [u8; 32],
    current_date: pub u64,
    challenge_hash: pub [u8; 32],
) {
    // Step 1: Calculate the credential hash from components
    let credential_hash: [u8; 32] =
        sha256_var(credential_string.as_bytes(), CREDENTIAL_LENGTH as u64).into();

    // Step 2: Verify ECDSA signature on the credential hash
    let signature_valid = std::ecdsa_secp256k1::verify_signature(
        pubkey_issuer_x,
        pubkey_issuer_y,
        signature_issuer,
        credential_hash,
    );
    assert(signature_valid);

    // Step 3: Check age requirement using the birth_timestamp from the credential
    let mut birth_timestamp: u64 = 0;
    for i in 64..74 {
        birth_timestamp = birth_timestamp * 10 + credential_string.as_bytes()[i] as u64 - 48;
    }

    let age_seconds = current_date - birth_timestamp;
    // Approximate seconds per year: 365.25 * 24 * 3600 = 31,557,600
    let seconds_per_year = 31557600;
    let min_age_seconds = 18 * seconds_per_year;
    assert(age_seconds >= min_age_seconds);

    // Sep 4: Verify device signature on the challenge hash
    // Extract public key from credential_raw from hex encoded values in position
    // 74 to 138 (32 bytes X, 32 bytes Y).
    let pubkey_device_x = decode_hex_32(credential_string.as_bytes(), 74);
    let pubkey_device_y = decode_hex_32(credential_string.as_bytes(), 138);

    let signature_device_valid = std::ecdsa_secp256k1::verify_signature(
        pubkey_device_x,
        pubkey_device_y,
        signature_device,
        challenge_hash,
    );
    assert(signature_device_valid);
}

fn decode_hex_32(hex_str: [u8; CREDENTIAL_LENGTH], start: u32) -> [u8; 32] {
    let mut result: [u8; 32] = [0u8; 32];
    for i in 0..32 {
        let high_nibble = decode_nibble(hex_str[start + 2 * i]);
        let low_nibble = decode_nibble(hex_str[start + 2 * i + 1]);
        result[i] = high_nibble * 16 + low_nibble;
    }
    result
}

fn decode_nibble(hex_char: u8) -> u8 {
    if hex_char >= 97 {
        hex_char - 97 + 10
    } else {
        hex_char - 48
    }
}
