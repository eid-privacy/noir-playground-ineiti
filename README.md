# Noir Zero-Knowledge Age Verification

A complete example demonstrating zero-knowledge proofs for age verification using **Noir** and **ECDSA secp256k1** signatures. This project shows how to prove someone meets an age requirement (18+) without revealing their exact age or personal information, using cryptographically signed credentials from a trusted issuer.

## 🎯 Overview

This example implements:
- **Credential System**: First name, last name, and date of birth
- **Issuer System**: secp256k1 private/public key pair for signing credentials
- **ZK Circuit**: Proves signature validity and age requirement without revealing personal data
- **Performance Benchmarking**: Comprehensive timing and size metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Issuer Keys   │    │   Credential     │    │  Noir Circuit   │
│  (secp256k1)    │───▶│   + Signature    │───▶│ Age Verification│
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   Private Key            Credential Hash           ZK Proof Output
   Public Key             Birth Timestamp               (Boolean)
                         ECDSA Signature
```

## 🚀 Quick Start

### Prerequisites

- [Devbox](https://www.jetpack.io/devbox/) installed

### Setup & Run

1. **Initialize the environment:**
   ```bash
   devbox shell
   devbox run setup
   ```

2. **Create example data:**
   ```bash
   devbox run setup-example
   ```

3. **Run the complete demo:**
   ```bash
   devbox run full-demo
   ```

That's it! The demo will:
- Generate issuer keys
- Create and sign a credential
- Compile and test the circuit
- Execute the zero-knowledge proof

## 📋 Available Scripts

| Command | Description |
|---------|-------------|
| `devbox run setup` | Install dependencies |
| `devbox run setup-example` | Generate example data (keys, credentials, inputs) |
| `devbox run generate-keys` | Generate secp256k1 issuer keys |
| `devbox run sign-credential` | Create and sign a test credential |
| `devbox run check-circuit` | Validate Noir circuit syntax |
| `devbox run test-circuit` | Run circuit unit tests |
| `devbox run run-circuit` | Execute circuit with inputs |
| `devbox run compile-circuit` | Compile circuit to bytecode |
| `devbox run circuit-info` | Display circuit analysis |
| `devbox run benchmark` | Run performance benchmarks |
| `devbox run full-demo` | Complete end-to-end demonstration |
| `devbox run clean` | Clean generated files |

## 🔧 Manual Usage

### 1. Generate Issuer Keys
```bash
python3 scripts/generate_keys.py
```
Creates a secp256k1 key pair and saves to `scripts/issuer_keys.json`.

### 2. Sign Credential
```bash
python3 scripts/sign_credential.py
```
Creates a sample credential (Alice Smith, born 2000-05-15) and generates the ECDSA signature.

### 3. Run Circuit
```bash
cd age_verification
nargo check    # Validate circuit
nargo test     # Run tests
nargo execute  # Execute with inputs
```

### 4. Benchmark Performance
```bash
python3 scripts/run_benchmark.py
```

## 📊 Performance Metrics

The circuit achieves excellent performance:

- **⏱️ Compilation**: ~60ms
- **🔢 Circuit Size**: 173 ACIR opcodes + 8 Brillig opcodes
- **📦 Bytecode Size**: 6.49 KB
- **⚡ Execution**: ~59ms
- **🧪 Tests**: ~104ms

## 🔐 Circuit Design

### Private Inputs
- `credential_hash: [u8; 32]` - SHA256 hash of credential data
- `birth_timestamp: u32` - Birth date as Unix timestamp
- `signature: [u8; 64]` - ECDSA signature from issuer

### Public Inputs
- `issuer_pub_key_x: [u8; 32]` - Issuer public key x-coordinate
- `issuer_pub_key_y: [u8; 32]` - Issuer public key y-coordinate
- `current_date: u32` - Current date as Unix timestamp
- `min_age: u32` - Minimum age requirement (e.g., 18)

### Output
- `bool` - True if signature is valid AND age requirement is met

## 📁 Project Structure

```
noir-playground-ineiti-2/
├── CLAUDE.md                 # Implementation plan
├── README.md                 # This file
├── devbox.json              # Environment & scripts
├── .gitignore               # Git ignore rules
├── age_verification/        # Noir circuit project
│   ├── Nargo.toml          # Project config
│   ├── src/main.nr         # Circuit implementation
│   └── Prover.toml         # Circuit inputs
└── scripts/
    ├── generate_keys.py     # Key generation
    ├── sign_credential.py   # Credential signing
    └── run_benchmark.py     # Performance testing
```

## 🔬 Technical Details

### Cryptography
- **Curve**: secp256k1 (Bitcoin/Ethereum curve)
- **Hash Function**: SHA256
- **Signature**: ECDSA with malleability protection

### Zero-Knowledge Properties
- **Completeness**: Valid proofs always verify
- **Soundness**: Invalid proofs cannot be forged
- **Zero-Knowledge**: No personal information is revealed

### Security Considerations
- Private keys are generated securely using system randomness
- Signatures prevent malleability (s ≤ order/2)
- Credential hash ensures data integrity
- Age calculation uses precise Unix timestamps

## 🛠️ Development

### Testing
```bash
# Run circuit tests
devbox run test-circuit

# Test with custom inputs
cd age_verification
nargo execute --input custom_inputs.toml
```

### Circuit Analysis
```bash
# Get detailed circuit info
devbox run circuit-info

# Benchmark performance
devbox run benchmark
```

### Debugging
```bash
# Check circuit syntax
devbox run check-circuit

# View compilation output
cd age_verification
nargo compile --verbose
```

## 🤝 Contributing

This is an educational example demonstrating Noir ZK capabilities. Feel free to:
- Extend the credential schema
- Add more verification logic
- Optimize circuit performance
- Implement additional test cases

## ⚠️ Security Notice

This is a **proof-of-concept** for educational purposes. For production use:
- Use hardware security modules for key generation
- Implement proper key management
- Add comprehensive input validation
- Perform security audits

## 📚 Learn More

- [Noir Documentation](https://noir-lang.org/docs/)
- [Zero-Knowledge Proofs](https://z.cash/technology/zksnarks/)
- [ECDSA Cryptography](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [Devbox Documentation](https://www.jetpack.io/devbox/docs/)

---

**Built with:** Noir v1.0.0-beta.13 • Python 3.11 • secp256k1 • devbox