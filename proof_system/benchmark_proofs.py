#!/usr/bin/env python3
"""
Comprehensive benchmark script for Noir zero-knowledge proof system.
This script measures all aspects of the ZK proof workflow including:
- Circuit compilation and execution
- Proof generation and verification
- File sizes and performance metrics
- Multiple runs for statistical accuracy
"""

import os
import subprocess
import sys
import time
import json
import statistics
from pathlib import Path

# Configuration
CIRCUIT_DIR = "age_verification"
TARGET_DIR = Path(CIRCUIT_DIR) / "target"
PROOFS_DIR = Path(CIRCUIT_DIR) / "proofs"
BENCHMARK_RUNS = 5  # Number of runs for averaging

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
    """Check if all required tools are available."""
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

    # Check circuit directory
    if not Path(CIRCUIT_DIR).exists():
        print(f"❌ Circuit directory {CIRCUIT_DIR} not found")
        return None

    print("✅ All dependencies available")
    return bb_binary

def run_command_with_timing(cmd, cwd=None):
    """Run a command and measure execution time."""
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd
        )
        end_time = time.time()
        duration = end_time - start_time

        return {
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        return {
            'success': False,
            'duration': duration,
            'error': str(e)
        }

def clean_target_directory():
    """Clean the target directory for fresh compilation."""
    if TARGET_DIR.exists():
        for file in TARGET_DIR.glob("*"):
            if file.is_file():
                file.unlink()
    TARGET_DIR.mkdir(exist_ok=True)

def clean_proofs_directory():
    """Clean the proofs directory for fresh proof generation."""
    if PROOFS_DIR.exists():
        for file in PROOFS_DIR.glob("*"):
            if file.is_file():
                file.unlink()
    PROOFS_DIR.mkdir(exist_ok=True)

def benchmark_compilation():
    """Benchmark circuit compilation."""
    print("📝 Benchmarking circuit compilation...")
    results = []

    for run in range(BENCHMARK_RUNS):
        print(f"   Run {run + 1}/{BENCHMARK_RUNS}")
        clean_target_directory()

        result = run_command_with_timing("nargo compile", cwd=CIRCUIT_DIR)
        if result['success']:
            results.append(result['duration'])
        else:
            print(f"❌ Compilation failed on run {run + 1}: {result.get('stderr', 'Unknown error')}")
            return None

    return {
        'times': results,
        'mean': statistics.mean(results),
        'median': statistics.median(results),
        'stdev': statistics.stdev(results) if len(results) > 1 else 0,
        'min': min(results),
        'max': max(results)
    }

def benchmark_execution():
    """Benchmark circuit execution (witness generation)."""
    print("🧮 Benchmarking circuit execution...")
    results = []

    # Ensure circuit is compiled first
    compile_result = run_command_with_timing("nargo compile", cwd=CIRCUIT_DIR)
    if not compile_result['success']:
        print("❌ Could not compile circuit for execution benchmark")
        return None

    for run in range(BENCHMARK_RUNS):
        print(f"   Run {run + 1}/{BENCHMARK_RUNS}")

        # Remove witness file
        for witness_file in TARGET_DIR.glob("*.gz"):
            witness_file.unlink()

        result = run_command_with_timing("nargo execute", cwd=CIRCUIT_DIR)
        if result['success']:
            results.append(result['duration'])
        else:
            print(f"❌ Execution failed on run {run + 1}: {result.get('stderr', 'Unknown error')}")
            return None

    return {
        'times': results,
        'mean': statistics.mean(results),
        'median': statistics.median(results),
        'stdev': statistics.stdev(results) if len(results) > 1 else 0,
        'min': min(results),
        'max': max(results)
    }

def benchmark_proof_generation(bb_binary):
    """Benchmark proof generation with Barretenberg."""
    print("🔐 Benchmarking proof generation...")
    results = []

    # Ensure circuit is compiled and executed
    compile_result = run_command_with_timing("nargo compile", cwd=CIRCUIT_DIR)
    if not compile_result['success']:
        print("❌ Could not compile circuit for proof benchmark")
        return None

    execute_result = run_command_with_timing("nargo execute", cwd=CIRCUIT_DIR)
    if not execute_result['success']:
        print("❌ Could not execute circuit for proof benchmark")
        return None

    # Find circuit and witness files
    circuit_files = list(TARGET_DIR.glob("*.json"))
    witness_files = list(TARGET_DIR.glob("*.gz"))

    if not circuit_files or not witness_files:
        print("❌ Missing circuit or witness files for proof generation")
        return None

    circuit_file = circuit_files[0]
    witness_file = witness_files[0]

    clean_proofs_directory()

    for run in range(BENCHMARK_RUNS):
        print(f"   Run {run + 1}/{BENCHMARK_RUNS}")

        proof_dir = PROOFS_DIR / f"circuit_{run}"
        proof_dir.mkdir(exist_ok=True)
        proof_file = proof_dir / "proof"

        cmd = (
            f'"{bb_binary}" prove '
            f'--scheme ultra_honk '
            f'-b "{circuit_file}" '
            f'-w "{witness_file}" '
            f'-o "{proof_dir}"'
        )

        result = run_command_with_timing(cmd)
        if result['success'] and proof_file.exists():
            results.append(result['duration'])
        else:
            print(f"❌ Proof generation failed on run {run + 1}: {result.get('stderr', 'Unknown error')}")
            return None

    # Get proof size from the first proof
    proof_file = PROOFS_DIR / "circuit_0" / "proof"
    proof_size = proof_file.stat().st_size if proof_file.exists() else 0

    return {
        'times': results,
        'mean': statistics.mean(results),
        'median': statistics.median(results),
        'stdev': statistics.stdev(results) if len(results) > 1 else 0,
        'min': min(results),
        'max': max(results),
        'proof_size': proof_size
    }

def benchmark_verification(bb_binary):
    """Benchmark proof verification with Barretenberg."""
    print("🛡️  Benchmarking proof verification...")
    results = []

    # Generate a single verification key and proof for testing
    circuit_files = list(TARGET_DIR.glob("*.json"))
    witness_files = list(TARGET_DIR.glob("*.gz"))

    if not circuit_files or not witness_files:
        print("❌ Missing circuit or witness files for verification benchmark")
        return None

    circuit_file = circuit_files[0]
    witness_file = witness_files[0]

    # Generate verification key
    vk_dir = PROOFS_DIR / "verification_key"
    vk_dir.mkdir(exist_ok=True)
    vk_file = vk_dir / "vk"
    vk_cmd = (
        f'"{bb_binary}" write_vk '
        f'--scheme ultra_honk '
        f'-b "{circuit_file}" '
        f'-o "{vk_dir}"'
    )

    vk_result = run_command_with_timing(vk_cmd)
    if not vk_result['success']:
        print("❌ Could not generate verification key")
        return None

    # Generate a proof to verify
    proof_dir = PROOFS_DIR / "circuit_verify"
    proof_dir.mkdir(exist_ok=True)
    proof_file = proof_dir / "proof"
    proof_cmd = (
        f'"{bb_binary}" prove '
        f'--scheme ultra_honk '
        f'-b "{circuit_file}" '
        f'-w "{witness_file}" '
        f'-o "{proof_dir}"'
    )

    proof_result = run_command_with_timing(proof_cmd)
    if not proof_result['success']:
        print("❌ Could not generate proof for verification")
        return None

    # Now benchmark verification
    for run in range(BENCHMARK_RUNS):
        print(f"   Run {run + 1}/{BENCHMARK_RUNS}")

        verify_cmd = (
            f'"{bb_binary}" verify '
            f'--scheme ultra_honk '
            f'-k "{vk_file}" '
            f'-p "{proof_file}"'
        )

        result = run_command_with_timing(verify_cmd)
        if result['success']:
            results.append(result['duration'])
        else:
            print(f"❌ Verification failed on run {run + 1}: {result.get('stderr', 'Unknown error')}")
            return None

    # Get verification key size
    vk_size = vk_file.stat().st_size if vk_file.exists() else 0

    return {
        'times': results,
        'mean': statistics.mean(results),
        'median': statistics.median(results),
        'stdev': statistics.stdev(results) if len(results) > 1 else 0,
        'min': min(results),
        'max': max(results),
        'vk_size': vk_size
    }

def get_circuit_info():
    """Get circuit constraint information."""
    result = run_command_with_timing("nargo info", cwd=CIRCUIT_DIR)

    circuit_info = {
        'acir_opcodes': 0,
        'brillig_opcodes': 0,
        'expression_width': 'Unknown'
    }

    if result['success']:
        lines = result['stdout'].split('\n')
        for line in lines:
            if '|' in line and ('main' in line or 'age_verification' in line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    try:
                        # Extract ACIR opcodes
                        acir_str = parts[3]
                        if acir_str.isdigit():
                            circuit_info['acir_opcodes'] = int(acir_str)

                        # Extract Brillig opcodes
                        brillig_str = parts[4]
                        if brillig_str.isdigit():
                            circuit_info['brillig_opcodes'] = int(brillig_str)

                        # Extract expression width
                        width_str = parts[2]
                        circuit_info['expression_width'] = width_str
                    except (ValueError, IndexError):
                        pass
                break

    return circuit_info

def save_benchmark_results(results):
    """Save benchmark results to JSON file."""
    benchmark_info = {
        'timestamp': time.time(),
        'benchmark_runs': BENCHMARK_RUNS,
        'results': results
    }

    results_file = "proof_benchmark_results.json"
    with open(results_file, 'w') as f:
        json.dump(benchmark_info, f, indent=2)

    print(f"💾 Benchmark results saved to {results_file}")

def print_benchmark_summary(results):
    """Print a comprehensive summary of benchmark results."""
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE ZK PROOF BENCHMARK RESULTS")
    print("=" * 70)

    # Circuit information
    if 'circuit_info' in results:
        info = results['circuit_info']
        print(f"🔢 Circuit Constraints:")
        print(f"   ACIR Opcodes: {info['acir_opcodes']}")
        print(f"   Brillig Opcodes: {info['brillig_opcodes']}")
        print(f"   Expression Width: {info['expression_width']}")
        print()

    # Timing results
    timing_sections = [
        ('compilation', '📝 Circuit Compilation'),
        ('execution', '🧮 Circuit Execution'),
        ('proof_generation', '🔐 Proof Generation'),
        ('verification', '🛡️  Proof Verification')
    ]

    for key, title in timing_sections:
        if key in results and results[key]:
            data = results[key]
            print(f"{title}:")
            print(f"   Mean time: {data['mean']:.3f}s ± {data['stdev']:.3f}s")
            print(f"   Median time: {data['median']:.3f}s")
            print(f"   Range: {data['min']:.3f}s - {data['max']:.3f}s")
            print()

    # File sizes
    if 'proof_generation' in results and results['proof_generation']:
        proof_size = results['proof_generation'].get('proof_size', 0)
        if proof_size > 0:
            print(f"📦 Proof Size: {proof_size} bytes ({proof_size/1024:.2f} KB)")

    if 'verification' in results and results['verification']:
        vk_size = results['verification'].get('vk_size', 0)
        if vk_size > 0:
            print(f"🔑 Verification Key Size: {vk_size} bytes ({vk_size/1024:.2f} KB)")

    # Performance summary
    total_time = 0
    if all(key in results and results[key] for key in ['compilation', 'execution', 'proof_generation', 'verification']):
        total_time = (
            results['compilation']['mean'] +
            results['execution']['mean'] +
            results['proof_generation']['mean'] +
            results['verification']['mean']
        )
        print(f"\n⏱️  Total End-to-End Time: {total_time:.3f}s")

    print("\n✅ Benchmark Complete!")

def main():
    """Main benchmark workflow."""
    print("🚀 Comprehensive Noir ZK Proof Benchmark")
    print("=" * 50)
    print(f"Running {BENCHMARK_RUNS} iterations of each operation for statistical accuracy")
    print()

    bb_binary = check_dependencies()
    if not bb_binary:
        sys.exit(1)

    # Store all results
    results = {}

    # Get circuit information
    print("📋 Getting circuit information...")
    results['circuit_info'] = get_circuit_info()

    # Run benchmarks
    benchmarks = [
        ('compilation', benchmark_compilation),
        ('execution', benchmark_execution),
        ('proof_generation', lambda: benchmark_proof_generation(bb_binary)),
        ('verification', lambda: benchmark_verification(bb_binary))
    ]

    for name, benchmark_func in benchmarks:
        print(f"\n{'='*20} {name.upper()} {'='*20}")
        result = benchmark_func()
        results[name] = result

        if result is None:
            print(f"❌ {name} benchmark failed, stopping execution")
            sys.exit(1)

    # Save and display results
    save_benchmark_results(results)
    print_benchmark_summary(results)

if __name__ == "__main__":
    main()