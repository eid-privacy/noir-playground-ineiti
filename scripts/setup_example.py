#!/usr/bin/env python3
"""
Setup script to create example data for the Noir age verification circuit.
Generates example issuer keys, credentials, and circuit inputs for testing and demonstration.
"""

import os
import sys
import subprocess

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run([sys.executable, f"scripts/{script_name}"],
                               capture_output=True, text=True, check=True)
        print(f"✅ {description} - Complete")
        if result.stdout:
            # Print key information but not the full output
            lines = result.stdout.split('\n')
            for line in lines:
                if ('✅' in line or 'Keys saved' in line or
                    'Circuit inputs saved' in line or 'Age:' in line or
                    'Meets requirement:' in line):
                    print(f"   {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - Script not found: scripts/{script_name}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")

    try:
        import ecdsa
        print("✅ Python ecdsa library found")
    except ImportError:
        print("❌ Python ecdsa library not found")
        print("   Please install with: pip install ecdsa")
        return False

    # Check if nargo is available
    try:
        result = subprocess.run(['nargo', '--version'],
                               capture_output=True, text=True, check=True)
        version = result.stdout.strip().split('\n')[0]
        print(f"✅ Noir toolchain found: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Noir toolchain (nargo) not found")
        print("   Please install Noir or run in devbox environment")
        return False

    return True

def create_example_data():
    """Create all example data for the project."""
    print("🚀 Setting up Noir Age Verification Example Data")
    print("=" * 50)

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Setup failed due to missing dependencies")
        return False

    # Step 1: Generate issuer keys
    if not run_script("generate_keys.py", "Generating example issuer keys"):
        return False

    # Step 2: Create and sign credential
    if not run_script("sign_credential.py", "Creating and signing example credential"):
        return False

    # Step 3: Verify circuit setup
    print("🔍 Verifying circuit setup...")
    try:
        result = subprocess.run(['nargo', 'check'],
                               cwd='age_verification',
                               capture_output=True, text=True, check=True)
        print("✅ Circuit verification - Complete")
    except subprocess.CalledProcessError as e:
        print("❌ Circuit verification - Failed")
        print(f"   Error: {e.stderr}")
        return False

    print("\n" + "=" * 50)
    print("🎉 Example data setup complete!")
    print("\nGenerated files:")
    print("📁 scripts/issuer_keys.json - Example secp256k1 keys")
    print("📁 scripts/credential_info.json - Example credential data")
    print("📁 age_verification/Prover.toml - Circuit inputs")
    print("\n🚀 You can now run:")
    print("   devbox run test-circuit    # Run circuit tests")
    print("   devbox run run-circuit     # Execute the circuit")
    print("   devbox run benchmark       # Performance analysis")
    print("   devbox run full-demo       # Complete demonstration")

    return True

def main():
    """Main setup function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Noir Age Verification - Example Data Setup")
        print("")
        print("This script creates example data for testing the zero-knowledge")
        print("age verification circuit, including:")
        print("  • Example issuer keys (secp256k1)")
        print("  • Sample credential (Alice Smith, born 2000-05-15)")
        print("  • Circuit input files")
        print("")
        print("Usage:")
        print("  python3 scripts/setup_example.py")
        print("  devbox run setup-example")
        return

    success = create_example_data()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()