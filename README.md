# Linus' take on using noir and Barretenberg

The goal is to have an easy playground to test different variations
of ZKP circuits with noir.
We want to understand what the best parameters are to use.
This repo has three parts:

- Creating the credentials (using python)
- Writing circuits and compiling them (with noir/nargo)
- Creating a ZKP proof (with bb/Barretenberg)

# TLDR

If you just want to run it all and see it fail, run

```bash
devbox run all
```

# Components

## Credentials

## Circuits

## ZKP Proofs

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
