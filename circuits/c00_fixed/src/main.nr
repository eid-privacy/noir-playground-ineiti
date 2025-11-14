use sha256::sha256_var;

fn main(
    // Private inputs - credential data
    credential_string: str<74>,
    signature_issuer: [u8; 64],

    // Public inputs
    pubkey_issuer_x: pub [u8; 32],
    pubkey_issuer_y: pub [u8; 32],
) {
    // Calculate the credential hash from components
    let credential_hash: [u8; 32] = sha256_var(credential_string.as_bytes(), 74).into();

    // Verify ECDSA signature on the credential hash
    let signature_valid = std::ecdsa_secp256k1::verify_signature(
        pubkey_issuer_x,
        pubkey_issuer_y,
        signature_issuer,
        credential_hash
    );
    assert(signature_valid);
}
