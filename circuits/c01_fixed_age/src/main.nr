use sha256::sha256_var;

fn main(
    // Private inputs - credential data
    credential_string: str<74>,
    signature_issuer: [u8; 64],

    // Public inputs
    pubkey_issuer_x: pub [u8; 32],
    pubkey_issuer_y: pub [u8; 32],
    current_date: pub u64,
) {
    // Step 1: Calculate the credential hash from components
    let credential_hash: [u8; 32] = sha256_var(credential_string.as_bytes(), 74).into();

    // Step 2: Verify ECDSA signature on the credential hash
    let signature_valid = std::ecdsa_secp256k1::verify_signature(
        pubkey_issuer_x,
        pubkey_issuer_y,
        signature_issuer,
        credential_hash
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
}
