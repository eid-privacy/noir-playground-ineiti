#!/usr/bin/env python3
"""
Install Barretenberg (bb) binary for proof generation and verification.
This script downloads and installs Barretenberg locally to this repository.
"""

import os
import subprocess
import sys
import urllib.request
import tarfile
import tempfile
import platform
from pathlib import Path

# Local installation directory (relative to repository root)
REPO_ROOT = Path(__file__).parent.parent
LOCAL_BIN_DIR = REPO_ROOT / ".local" / "bin"
BB_BINARY_PATH = LOCAL_BIN_DIR / "bb"

def get_platform_info():
    """Determine the platform and architecture for binary download."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map platform names
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    # Map architecture names
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    return os_name, arch

def get_compatible_version():
    """Get the compatible Barretenberg version for the current Noir installation."""
    try:
        result = subprocess.run(["nargo", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.strip()
            print(f"📋 Found nargo: {version_line}")

            # Extract noir version and map to barretenberg version
            # Based on search results, v0.82.2+ is recommended for security
            if "1.0.0-beta.13" in version_line:
                return "0.82.2"  # Secure version
            else:
                return "0.82.2"  # Default secure version
        else:
            print("⚠️  nargo not found, using default version")
            return "0.82.2"
    except Exception:
        print("⚠️  Could not detect nargo version, using default")
        return "0.82.2"

def download_barretenberg():
    """Download Barretenberg binary directly from GitHub releases."""
    print("📥 Downloading Barretenberg...")

    try:
        os_name, arch = get_platform_info()
        version = get_compatible_version()

        # Create local bin directory
        LOCAL_BIN_DIR.mkdir(parents=True, exist_ok=True)

        # Try multiple version formats and naming conventions
        version_attempts = [
            f"barretenberg-v{version}",  # barretenberg-v0.82.2
            f"v{version}",               # v0.82.2
            version,                     # 0.82.2
        ]

        filename_attempts = [
            f"barretenberg-{arch}-{os_name}.tar.gz",
            f"bb-{arch}-{os_name}.tar.gz",
            f"{arch}-{os_name}.tar.gz",
        ]

        for version_tag in version_attempts:
            for filename in filename_attempts:
                url = f"https://github.com/AztecProtocol/aztec-packages/releases/download/{version_tag}/{filename}"
                print(f"   Trying: {url}")

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir) / filename

                        # Download the file
                        urllib.request.urlretrieve(url, temp_path)
                        print(f"✅ Downloaded {filename}")

                        # Extract the archive
                        print(f"📦 Extracting {filename}...")
                        with tarfile.open(temp_path, 'r:gz') as tar:
                            # Find and extract bb binary
                            for member in tar.getmembers():
                                if member.name == "bb" or member.name.endswith("/bb"):
                                    member.name = "bb"  # Rename to just 'bb'
                                    tar.extract(member, LOCAL_BIN_DIR)
                                    break
                            else:
                                raise RuntimeError("Could not find 'bb' binary in archive")

                        # Make binary executable
                        os.chmod(BB_BINARY_PATH, 0o755)
                        print(f"✅ Barretenberg installed to: {BB_BINARY_PATH}")
                        return True

                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        continue  # Try next URL
                    else:
                        print(f"❌ Download failed: {e}")
                        continue

        # If we get here, all attempts failed
        print(f"❌ Could not find Barretenberg v{version} for {arch}-{os_name}")
        print("💡 Available options:")
        print("1. Check https://github.com/AztecProtocol/aztec-packages/releases for available versions")
        print("2. Try installing with: curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/master/barretenberg/bbup/install | bash")
        print("3. Then run: bbup")
        return False

    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def find_bb_binary():
    """Find the bb binary in local and common locations."""
    # Check local installation first (repository-local)
    if BB_BINARY_PATH.exists():
        return BB_BINARY_PATH

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

    for location in possible_locations:
        if location.exists() and location.is_file():
            return location

    return None

def check_existing_installation():
    """Check if Barretenberg is already installed."""
    bb_path = find_bb_binary()
    if bb_path:
        try:
            result = subprocess.run([str(bb_path), "--version"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Barretenberg already installed: {bb_path}")
                print(f"   Version: {result.stdout.strip()}")
                return bb_path
        except Exception:
            pass

        # Try --help if --version doesn't work
        try:
            result = subprocess.run([str(bb_path), "--help"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Barretenberg already installed: {bb_path}")
                return bb_path
        except Exception:
            pass

    return None

def add_to_path(bb_path):
    """Add BB installation directory to PATH."""
    bb_dir = bb_path.parent
    print(f"\n📝 To use bb from anywhere, add this to your shell profile:")
    print(f"   export PATH=\"{bb_dir}:$PATH\"")

    # Check if already in PATH
    current_path = os.environ.get('PATH', '')
    if str(bb_dir) not in current_path:
        print(f"\n💡 Or run this command for the current session:")
        print(f"   export PATH=\"{bb_dir}:$PATH\"")

def test_installation(bb_path):
    """Test the Barretenberg installation."""
    print(f"\n🧪 Testing installation...")
    try:
        result = subprocess.run([str(bb_path), "--help"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Barretenberg is working correctly")
            return True
        else:
            print(f"❌ Barretenberg test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Barretenberg test timed out")
        return False
    except Exception as e:
        print(f"❌ Barretenberg test failed: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 Barretenberg Local Installation Script")
    print("=" * 50)
    print(f"Installing to: {LOCAL_BIN_DIR}")
    print()

    # Check if already installed
    existing_bb = check_existing_installation()
    if existing_bb:
        response = input("Reinstall? (y/N): ").strip().lower()
        if response != 'y':
            print("Installation cancelled.")
            sys.exit(0)

    try:
        # Download and install Barretenberg locally
        if not download_barretenberg():
            print("❌ Failed to download and install Barretenberg")
            sys.exit(1)

        # Find the installed bb binary
        bb_path = find_bb_binary()
        if not bb_path:
            print("❌ Could not find bb binary after installation")
            sys.exit(1)

        # Test installation
        if test_installation(bb_path):
            add_to_path(bb_path)
            print(f"\n✅ Installation complete!")
            print(f"\nInstalled Barretenberg at: {bb_path}")
            print(f"\nNext steps:")
            print(f"1. The binary is available at: {bb_path}")
            print(f"2. Run '{bb_path} --help' to see available commands")
            print(f"3. Use the proof generation scripts in this directory")
            print(f"\n💡 This installation is local to this repository only.")
        else:
            print(f"\n❌ Installation completed but testing failed")
            print(f"💡 bb binary is at: {bb_path}")
            print(f"Try running: {bb_path} --help")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print(f"\n🔧 Manual installation:")
        print(f"Visit: https://github.com/AztecProtocol/aztec-packages/releases")
        print(f"Download the appropriate binary for your platform")
        sys.exit(1)

if __name__ == "__main__":
    main()