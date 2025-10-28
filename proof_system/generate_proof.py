#!/usr/bin/env python3
"""
Generate zero-knowledge proofs for Noir circuits using Barretenberg.
This script compiles, executes, and generates proofs for the age verification circuit.
"""

import os
import subprocess
import sys
import time
import json
from pathlib import Path

# Configuration
CIRCUIT_DIR = "age_verification"
TARGET_DIR = Path(CIRCUIT_DIR) / "target"
PROOFS_DIR = Path(CIRCUIT_DIR) / "proofs"

def find_bb_binary():
    """Find the bb binary in local and common locations."""
    # Check local repository installation first
    repo_root = Path(__file__).parent.parent
    local_bb = repo_root / ".local" / "bin" / "bb"
    if local_bb.exists():
        return local_bb

    # Also check PATH and common locations
    possible_locations = [
        Path.home() / ".bb" / "bb",
        Path.home() / ".local" / "bin" / "bb",
        Path("/usr/local/bin/bb"),
        Path("/opt/homebrew/bin/bb"),
    ]

    try:
        result = subprocess.run(["which", "bb"], capture_output=True, text=True)
        if result.returncode == 0:
            bb_path = Path(result.stdout.strip())
            if bb_path.exists():
                return bb_path
    except Exception:
        pass

    # Check common locations
    for location in possible_locations:
        if location.exists() and location.is_file():
            return location

    return None

def check_dependencies():
    """Check if required tools are available."""
    print("🔍 Checking dependencies...")

    # Check for nargo
    try:
        result = subprocess.run(["nargo", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ nargo not found. Please install Noir first.")
            return None
        print(f"✅ nargo: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ nargo not found. Please install Noir first.")
        return None

    # Check for bb (Barretenberg)
    bb_binary = find_bb_binary()
    if not bb_binary:
        print("❌ bb binary not found")
        print("Run 'python proof_system/install_barretenberg.py' first.")
        return None

    try:
        result = subprocess.run([str(bb_binary), "--version"], capture_output=True, text=True)
        print(f"✅ barretenberg: {result.stdout.strip() if result.returncode == 0 else 'installed'}")
    except Exception:
        print("⚠️  bb binary found but version check failed")

    return bb_binary

def run_command_with_timing(cmd, description, cwd=None):
    """Run a command and measure execution time."""
    print(f"🔄 {description}...")
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd
        )
        end_time = time.time()
        duration = end_time - start_time

        if result.returncode == 0:
            print(f"✅ {description}: {duration:.3f}s")
            return {
                'success': True,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"❌ {description} failed ({duration:.3f}s):")
            print(f"   Error: {result.stderr}")
            return {
                'success': False,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {description} failed ({duration:.3f}s): {e}")
        return {
            'success': False,
            'duration': duration,
            'error': str(e)
        }

def compile_circuit():
    """Compile the Noir circuit to ACIR bytecode."""
    if not Path(CIRCUIT_DIR).exists():
        print(f"❌ Circuit directory {CIRCUIT_DIR} not found")
        return False

    # Clean previous compilation
    TARGET_DIR.mkdir(exist_ok=True)
    for file in TARGET_DIR.glob("*.json"):
        file.unlink()

    result = run_command_with_timing(
        "nargo compile",
        "Circuit compilation",
        cwd=CIRCUIT_DIR
    )
    return result

def execute_circuit():
    """Execute the circuit to generate witness."""
    result = run_command_with_timing(
        "nargo execute",
        "Circuit execution (witness generation)",
        cwd=CIRCUIT_DIR
    )
    return result

def generate_proof(bb_binary):
    """Generate a zero-knowledge proof using Barretenberg."""
    # Find the compiled circuit file
    circuit_files = list(TARGET_DIR.glob("*.json"))
    if not circuit_files:
        print("❌ No compiled circuit found. Run compilation first.")
        return False

    circuit_file = circuit_files[0]  # Use the first .json file found

    # Find the witness file
    witness_files = list(TARGET_DIR.glob("*.gz"))
    if not witness_files:
        print("❌ No witness file found. Run execution first.")
        return False

    witness_file = witness_files[0]  # Use the first .gz file found

    # Create proofs directory and proof directory
    PROOFS_DIR.mkdir(exist_ok=True)
    proof_dir = PROOFS_DIR / "circuit"
    proof_dir.mkdir(exist_ok=True)
    proof_file = proof_dir / "proof"

    # Generate proof using Barretenberg
    cmd = (
        f'"{bb_binary}" prove '
        f'--scheme ultra_honk '
        f'-b "{circuit_file}" '
        f'-w "{witness_file}" '
        f'-o "{proof_dir}"'
    )

    result = run_command_with_timing(
        cmd,
        "Zero-knowledge proof generation"
    )

    if result['success'] and proof_file.exists():
        proof_size = proof_file.stat().st_size
        print(f"📦 Proof generated: {proof_size} bytes ({proof_size/1024:.2f} KB)")
        result['proof_size'] = proof_size
        result['proof_file'] = str(proof_file)

    return result

def generate_verification_key(bb_binary):
    """Generate verification key for the circuit."""
    circuit_files = list(TARGET_DIR.glob("*.json"))
    if not circuit_files:
        print("❌ No compiled circuit found.")
        return False

    circuit_file = circuit_files[0]

    # Create proofs directory and verification key directory
    PROOFS_DIR.mkdir(exist_ok=True)
    vk_dir = PROOFS_DIR / "verification_key"
    vk_dir.mkdir(exist_ok=True)
    vk_file = vk_dir / "vk"

    cmd = (
        f'"{bb_binary}" write_vk '
        f'--scheme ultra_honk '
        f'-b "{circuit_file}" '
        f'-o "{vk_dir}"'
    )

    result = run_command_with_timing(
        cmd,
        "Verification key generation"
    )

    if result['success'] and vk_file.exists():
        vk_size = vk_file.stat().st_size
        print(f"🔑 Verification key: {vk_size} bytes ({vk_size/1024:.2f} KB)")
        result['vk_size'] = vk_size
        result['vk_file'] = str(vk_file)

    return result

def save_proof_info(results):
    """Save proof generation information to JSON file."""
    proof_info = {
        'timestamp': time.time(),
        'circuit_dir': CIRCUIT_DIR,
        'results': results
    }

    info_file = PROOFS_DIR / "proof_info.json"
    with open(info_file, 'w') as f:
        json.dump(proof_info, f, indent=2)

    print(f"💾 Proof info saved to {info_file}")

def main():
    """Main proof generation workflow."""
    print("🚀 Noir Zero-Knowledge Proof Generation")
    print("=" * 50)

    bb_binary = check_dependencies()
    if not bb_binary:
        sys.exit(1)

    # Store all results
    results = {}

    # Step 1: Compile circuit
    print("\n📝 Step 1: Circuit Compilation")
    compile_result = compile_circuit()
    results['compilation'] = compile_result
    if not compile_result['success']:
        print("❌ Cannot proceed due to compilation failure")
        sys.exit(1)

    # Step 2: Execute circuit (generate witness)
    print("\n🧮 Step 2: Circuit Execution")
    execute_result = execute_circuit()
    results['execution'] = execute_result
    if not execute_result['success']:
        print("❌ Cannot proceed due to execution failure")
        sys.exit(1)

    # Step 3: Generate verification key
    print("\n🔑 Step 3: Verification Key Generation")
    vk_result = generate_verification_key(bb_binary)
    results['verification_key'] = vk_result
    if not vk_result['success']:
        print("❌ Cannot proceed due to verification key generation failure")
        sys.exit(1)

    # Step 4: Generate proof
    print("\n🔐 Step 4: Zero-Knowledge Proof Generation")
    proof_result = generate_proof(bb_binary)
    results['proof_generation'] = proof_result
    if not proof_result['success']:
        print("❌ Proof generation failed")
        sys.exit(1)

    # Save results
    save_proof_info(results)

    # Summary
    print("\n" + "=" * 50)
    print("📋 PROOF GENERATION SUMMARY")
    print("=" * 50)
    print(f"⏱️  Total compilation time: {compile_result['duration']:.3f}s")
    print(f"⏱️  Total execution time: {execute_result['duration']:.3f}s")
    print(f"⏱️  Verification key time: {vk_result['duration']:.3f}s")
    print(f"⏱️  Proof generation time: {proof_result['duration']:.3f}s")

    if 'proof_size' in proof_result:
        print(f"📦 Proof size: {proof_result['proof_size']} bytes ({proof_result['proof_size']/1024:.2f} KB)")

    if 'vk_size' in vk_result:
        print(f"🔑 Verification key size: {vk_result['vk_size']} bytes ({vk_result['vk_size']/1024:.2f} KB)")

    total_time = sum([
        compile_result['duration'],
        execute_result['duration'],
        vk_result['duration'],
        proof_result['duration']
    ])
    print(f"⏱️  Total time: {total_time:.3f}s")

    print(f"\n✅ Proof generation complete!")
    print(f"🔍 Next: Run 'python proof_system/verify_proof.py' to verify the proof")

if __name__ == "__main__":
    main()