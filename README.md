# Linus' take on using noir and Barretenberg

The goal is to have an easy playground to test different variations
of ZKP circuits with noir.
We want to understand what the best parameters are to use.
This repo has three parts:

- Creating the credentials (using python)
- Writing circuits and compiling them (with noir/nargo)
- Creating a ZKP proof (with bb/Barretenberg)

# TLDR

If you just want to run it all and see it prove, run

```bash
devbox run all
```

To clean up for a new run:

```bash
devbox run clean
```

If you want to develop and test things, you can use:

```bash
devbox shell
```

Then you can use `make all` and `make clean`, or directly call the scripts.

# Components

## Credentials

Currently the following credential is created:

- `fixed_age` with a fixed length for each field

Proposed other credentials include:

- `fixed_age_hobi` for `Holder Binding (hobi)`
- `jwt_age(|_hobi)` for jwt-encoded credentials
- `cbor_age(|_hobi)` using cbor encoding, like mdoc

### Test persona

Two test persona are available:

- Alice, aged 20
- Bob, aged 16

## Circuits

Implemented and tested circuits:

- `c01_fixed_age`

Other circuits should follow...

## Proof creation

In noir, you need to do the following steps:

- `nargo compile` circuit compilation, converts a `.nr` file into a bytecode `.json`
- `nargo execute` takes a `Prover.toml` and fills in the wires of a circuit to create a witness `.gz`
- `bb prove` takes a bytecode and a witness to create a proof
- `bb verify`

# Terms

Here some terms we encountered on our journey:

- ZKP - we suppose you know what it means
- [ACIR Opcodes](https://noir-lang.github.io/noir/docs/acir/circuit/index.html) - intermediate language for ZKPs used by noir.
This is correlated to the size of a R1CS circuit, but not linearly.
Depending on the opcodes, smaller ACIR number can create larger R1CS circuits!
- [Brillig Opcodes](https://noir-lang.org/docs/noir/concepts/unconstrained) - optimized opcodes for doing things outside of the circuit

# Links

- Python ECDSA library: https://ecdsa.readthedocs.io/en/latest/quickstart.html
- Very bad article which does stupid stuff but still helped me find the 'sigencode' argument
- [Noir Lang Docs](https://noir-lang.org/docs/)
- Flakes for Noir and Barretenberg: https://github.com/eid-privacy/flakes
