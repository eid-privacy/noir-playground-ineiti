use sha256::sha256_var;

fn main(
    // Private inputs - credential data
    credential_raw: [u8; 74],
    // credential_msg_hash: [u8; 32],
    signature: [u8; 64],

    // Public inputs
    pubkey_issuer_x: pub [u8; 32],
    pubkey_issuer_y: pub [u8; 32],
    current_date: pub u64,
) -> pub bool {
    // Step 1: Calculate the credential hash from components
    let credential_hash: [u8; 32] = sha256_var(credential_raw, 74).into();
    println(f"hash:  {credential_hash}");
    println(f"pub_x: {pubkey_issuer_x}");
    println(f"pub_y: {pubkey_issuer_y}");
    println(f"sig:   {signature}");

    // Step 2: Verify ECDSA signature on the credential hash
    let signature_valid = std::ecdsa_secp256k1::verify_signature(
        pubkey_issuer_x,
        pubkey_issuer_y,
        signature,
        credential_hash
    );

    // Step 3: Check age requirement using the birth_timestamp from the credential
    let mut birth_timestamp: u64 = 0;
    for i in 64..74 {
        birth_timestamp = birth_timestamp * 10 + credential_raw[i] as u64 - 48;
    }

    let age_seconds = current_date - birth_timestamp;
    // Approximate seconds per year: 365.25 * 24 * 3600 = 31,557,600
    let seconds_per_year = 31557600;
    let min_age_seconds = 18 * seconds_per_year;
    let age_requirement_met = age_seconds >= min_age_seconds;

    // Step 4: Return combined result
    // The prover must provide correct credential components AND valid signature
    // signature_valid & age_requirement_met
    println(f"valid: {signature_valid}");
    age_requirement_met
}
