# Zero-Knowledge Proof System with Barretenberg

This directory contains scripts for generating and verifying zero-knowledge proofs for Noir circuits using the Barretenberg proving system.

## Overview

The proof system provides a complete workflow for:
- Installing the Barretenberg proving backend
- Generating zero-knowledge proofs from Noir circuits
- Verifying proofs with cryptographic certainty
- Comprehensive benchmarking of proof performance

## Prerequisites

- **Noir/nargo**: Install via [noirup](https://noir-lang.org/docs/getting_started/installation)
- **Python 3.7+**: For running the proof system scripts
- **Internet connection**: For downloading Barretenberg binary

## Quick Start

### 1. Install Barretenberg

```bash
python proof_system/install_barretenberg.py
```

This script automatically:
- Detects your platform (macOS/Linux/Windows)
- Downloads the appropriate Barretenberg binary
- Installs it to `~/.bb/bb`
- Adds it to your PATH

### 2. Generate a Proof

```bash
python proof_system/generate_proof.py
```

This performs the complete proof generation workflow:
- Compiles the Noir circuit to ACIR bytecode
- Executes the circuit to generate a witness
- Creates a verification key
- Generates the zero-knowledge proof

### 3. Verify the Proof

```bash
python proof_system/verify_proof.py
```

This verifies the generated proof:
- Checks proof validity using the verification key
- Provides detailed success/failure information
- Measures verification time

### 4. Run Comprehensive Benchmarks

```bash
python proof_system/benchmark_proofs.py
```

This runs performance benchmarks:
- Multiple iterations for statistical accuracy
- Measures compilation, execution, proving, and verification times
- Analyzes proof and verification key sizes
- Generates detailed performance reports

## File Structure

```
proof_system/
├── README.md                    # This file
├── install_barretenberg.py     # Barretenberg installation script
├── generate_proof.py           # Proof generation workflow
├── verify_proof.py             # Proof verification workflow
└── benchmark_proofs.py         # Comprehensive benchmarking
```

## Generated Files

The scripts create the following files in your age verification project:

```
age_verification/
├── target/                      # Compiled circuit artifacts
│   ├── age_verification.json    # ACIR bytecode
│   └── age_verification.gz      # Circuit witness
└── proofs/                      # Proof artifacts
    ├── circuit.proof            # Zero-knowledge proof
    ├── verification_key          # Verification key
    ├── proof_info.json          # Proof generation metadata
    └── verification_info.json   # Verification results
```

## Barretenberg Commands

The scripts use these core Barretenberg commands:

```bash
# Generate proof
bb prove --scheme ultra_honk -b circuit.json -w witness.gz -o proof

# Generate verification key
bb write_vk --scheme ultra_honk -b circuit.json -o vk

# Verify proof
bb verify --scheme ultra_honk -k vk -p proof
```

## Performance Characteristics

Expected performance for the age verification circuit:
- **Circuit Size**: ~173 ACIR opcodes, 8 Brillig opcodes
- **Compilation**: 50-100ms
- **Execution**: 50-100ms
- **Proof Generation**: 500ms-2s (depends on hardware)
- **Verification**: 10-50ms
- **Proof Size**: ~2-10KB (UltraHonk proofs)
- **Verification Key**: ~1-5KB

## Proving Schemes

This system uses **UltraHonk** proving scheme:
- ✅ EVM-compatible (can generate Solidity verifiers)
- ✅ Gas-efficient verification on blockchain
- ✅ Fast verification times
- ✅ Reasonable proof sizes

## Troubleshooting

### Installation Issues

If Barretenberg installation fails:
1. Check internet connection
2. Verify platform detection (run with `-v` for verbose output)
3. Try manual installation from [Aztec releases](https://github.com/AztecProtocol/aztec-packages/releases)

### Proof Generation Failures

If proof generation fails:
1. Ensure the circuit compiles: `nargo check`
2. Verify inputs are valid: `nargo execute`
3. Check Barretenberg is installed: `bb --help`
4. Review error messages in the output

### Verification Failures

If proof verification fails:
1. Regenerate the proof
2. Ensure verification key matches the circuit
3. Check for file corruption
4. Verify Barretenberg version compatibility

## Integration Examples

### Command Line Usage
```bash
# Full workflow
python proof_system/install_barretenberg.py
python proof_system/generate_proof.py
python proof_system/verify_proof.py
```

### Scripted Integration
```python
import subprocess

# Generate proof programmatically
result = subprocess.run([
    "python", "proof_system/generate_proof.py"
], capture_output=True, text=True)

if result.returncode == 0:
    print("Proof generated successfully")
else:
    print(f"Proof generation failed: {result.stderr}")
```

## Advanced Usage

### Custom Circuit Paths
Modify the `CIRCUIT_DIR` variable in the scripts to work with different circuits.

### Multiple Proving Schemes
Barretenberg supports multiple schemes. Modify the `--scheme` parameter to use different proving systems.

### Batch Operations
The benchmark script demonstrates how to run multiple operations in batch for performance testing.

## Security Considerations

- **Trusted Setup**: UltraHonk uses a universal trusted setup
- **Proof Verification**: Always verify proofs before trusting results
- **Key Management**: Protect verification keys used in production
- **Version Pinning**: Pin Barretenberg versions for production stability

## Further Reading

- [Noir Documentation](https://noir-lang.org/)
- [Barretenberg GitHub](https://github.com/AztecProtocol/barretenberg)
- [Zero-Knowledge Proofs Explained](https://blog.cryptographyengineering.com/2014/11/27/zero-knowledge-proofs-illustrated-primer/)
- [UltraHonk Proving System](https://hackmd.io/@aztec-network/rk8hE5-Hj)