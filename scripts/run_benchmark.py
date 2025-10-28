#!/usr/bin/env python3
"""
Benchmark script for the Noir age verification circuit.
Measures compilation, execution times, and circuit analysis.
Note: Proof generation requires external proving system (not included in nargo).
"""

import subprocess
import time
import os
import json

def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return result with timing."""
    start_time = time.time()

    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        output = result.stdout + result.stderr
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        output = ""

    end_time = time.time()
    duration = end_time - start_time

    return {
        'command': cmd,
        'duration': duration,
        'return_code': result.returncode,
        'output': output.strip() if output else "",
        'success': result.returncode == 0
    }

def measure_circuit_compilation():
    """Measure circuit compilation time."""
    print("🔨 Compiling circuit...")

    # Clean previous compilation
    run_command("rm -rf target/", cwd="age_verification")

    # Compile the circuit
    result = run_command("nargo check", cwd="age_verification")

    if result['success']:
        print(f"✅ Circuit compilation: {result['duration']:.3f}s")
        return result
    else:
        print(f"❌ Circuit compilation failed: {result['output']}")
        return result

def measure_circuit_info():
    """Measure circuit information and constraints."""
    print("📊 Analyzing circuit info...")

    result = run_command("nargo info", cwd="age_verification")

    if result['success']:
        # Extract circuit information from output
        lines = result['output'].split('\n')
        circuit_info = {}

        for line in lines:
            if 'function' in line.lower() or 'circuit' in line.lower():
                circuit_info['circuit'] = line.strip()
            elif 'opcodes' in line.lower() or 'gates' in line.lower():
                circuit_info['constraints'] = line.strip()

        print(f"✅ Circuit analysis: {result['duration']:.3f}s")
        for key, value in circuit_info.items():
            print(f"   {value}")

        return result, circuit_info
    else:
        print(f"❌ Circuit info analysis failed: {result['output']}")
        return result, {}

def measure_bytecode_generation():
    """Measure circuit compilation to bytecode."""
    print("🔐 Compiling to bytecode...")

    # Clean previous compilation artifacts
    run_command("rm -rf target/", cwd="age_verification")

    result = run_command("nargo compile", cwd="age_verification")

    bytecode_size = 0
    if result['success']:
        # Check bytecode file size
        try:
            target_dir = "age_verification/target"
            if os.path.exists(target_dir):
                for root, dirs, files in os.walk(target_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        bytecode_size += os.path.getsize(file_path)

                print(f"✅ Bytecode generation: {result['duration']:.3f}s")
                print(f"   📦 Bytecode size: {bytecode_size} bytes ({bytecode_size/1024:.2f} KB)")
            else:
                print("⚠️ No target directory found after compilation")
        except Exception as e:
            print(f"⚠️ Could not measure bytecode size: {e}")
    else:
        print(f"❌ Bytecode generation failed: {result['output']}")

    return result, bytecode_size

def measure_circuit_execution():
    """Measure circuit execution time."""
    print("🔍 Executing circuit...")

    result = run_command("nargo execute", cwd="age_verification")

    if result['success']:
        print(f"✅ Circuit execution: {result['duration']:.3f}s")
        return result
    else:
        print(f"❌ Circuit execution failed: {result['output']}")
        return result

def measure_witness_generation():
    """Measure witness file generation and size."""
    print("🧾 Analyzing witness generation...")

    witness_size = 0
    witness_path = "age_verification/target/age_verification.gz"

    if os.path.exists(witness_path):
        witness_size = os.path.getsize(witness_path)
        print(f"✅ Witness file found: {witness_size} bytes ({witness_size/1024:.2f} KB)")
    else:
        # Look for any witness files
        target_dir = "age_verification/target"
        if os.path.exists(target_dir):
            for file in os.listdir(target_dir):
                if file.endswith(".gz") or "witness" in file.lower():
                    file_path = os.path.join(target_dir, file)
                    witness_size = os.path.getsize(file_path)
                    print(f"✅ Witness file found: {witness_size} bytes ({witness_size/1024:.2f} KB)")
                    break

    if witness_size == 0:
        print("⚠️ No witness file found")

    return witness_size

def run_circuit_tests():
    """Run the Noir circuit tests."""
    print("🧪 Running circuit tests...")

    result = run_command("nargo test", cwd="age_verification")

    if result['success']:
        print(f"✅ Circuit tests: {result['duration']:.3f}s")
        print(f"   Test output: {result['output']}")
        return result
    else:
        print(f"❌ Circuit tests failed: {result['output']}")
        return result

def main():
    """Run the complete benchmark suite."""
    print("🚀 Starting Noir Age Verification Benchmark")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("age_verification"):
        print("❌ Error: age_verification directory not found")
        print("Please run this script from the project root directory")
        return

    # Store all results
    benchmark_results = {
        'timestamp': time.time(),
        'results': {}
    }

    # 1. Circuit checking
    check_result = measure_circuit_compilation()
    benchmark_results['results']['check_compilation'] = check_result

    if not check_result['success']:
        print("❌ Cannot proceed with benchmarks due to compilation failure")
        return

    # 2. Circuit analysis
    info_result, circuit_info = measure_circuit_info()
    benchmark_results['results']['circuit_analysis'] = info_result
    benchmark_results['results']['circuit_info'] = circuit_info

    # 3. Circuit tests
    test_result = run_circuit_tests()
    benchmark_results['results']['tests'] = test_result

    # 4. Bytecode generation
    compile_result, bytecode_size = measure_bytecode_generation()
    benchmark_results['results']['bytecode_generation'] = compile_result
    benchmark_results['results']['bytecode_size'] = bytecode_size

    if compile_result['success']:
        # 5. Circuit execution
        execute_result = measure_circuit_execution()
        benchmark_results['results']['circuit_execution'] = execute_result

        if execute_result['success']:
            # 6. Witness analysis
            witness_size = measure_witness_generation()
            benchmark_results['results']['witness_size'] = witness_size

    # Summary
    print("\n" + "=" * 50)
    print("📋 BENCHMARK SUMMARY")
    print("=" * 50)

    if check_result['success']:
        print(f"⏱️  Initial check time: {check_result['duration']:.3f}s")

    if circuit_info:
        for key, value in circuit_info.items():
            print(f"🔢 {value}")

    if test_result['success']:
        print(f"🧪 Circuit tests time: {test_result['duration']:.3f}s")

    if 'bytecode_generation' in benchmark_results['results'] and benchmark_results['results']['bytecode_generation']['success']:
        compile_time = benchmark_results['results']['bytecode_generation']['duration']
        print(f"⏱️  Bytecode generation time: {compile_time:.3f}s")
        print(f"📦 Bytecode size: {bytecode_size} bytes ({bytecode_size/1024:.2f} KB)")

        if 'circuit_execution' in benchmark_results['results'] and benchmark_results['results']['circuit_execution']['success']:
            execute_time = benchmark_results['results']['circuit_execution']['duration']
            print(f"⚡ Circuit execution time: {execute_time:.3f}s")

            if 'witness_size' in benchmark_results['results']:
                witness_size = benchmark_results['results']['witness_size']
                print(f"🧾 Witness size: {witness_size} bytes ({witness_size/1024:.2f} KB)")
                print("")
                print("⚠️  Note: Noir v1.0.0-beta.13 does not include prove/verify commands.")
                print("    For ZK proof generation, use an external proving system like:")
                print("    - Barretenberg (bb) for PLONK proofs")
                print("    - Or integrate with a proving service")

    # Save detailed results
    with open('benchmark_results.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)

    print(f"\n💾 Detailed results saved to benchmark_results.json")
    print("✅ Benchmark complete!")

if __name__ == "__main__":
    main()