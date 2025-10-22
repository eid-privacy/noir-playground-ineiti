use dep::std;

fn main(
    credential: [u8; 177], // Raw credential data without signature (241 - 64 = 177 bytes)
    signature_r: Field,     // First half of ECDSA signature
    signature_s: Field,     // Second half of ECDSA signature
    pub_key_x: Field,      // Issuer public key x coordinate
    pub_key_y: Field       // Issuer public key y coordinate
) -> pub Field {
    // Hash the credential data using SHA256
    let message_hash = std::hash::sha256(credential);

    // Verify ECDSA signature over the credential hash
    let valid_signature = std::ecdsa_secp256r1::verify_signature(
        pub_key_x,
        pub_key_y,
        signature_r,
        signature_s,
        message_hash
    );

    // Return 1 if signature is valid, 0 if invalid
    if valid_signature {
        1
    } else {
        0
    }
}