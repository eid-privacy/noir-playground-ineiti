#!/bin/bash

SCHEME=""
# SCHEME="-s ultra_honk"
CIRCUIT_BASE_DIR=circuits

prove_circuit(){
    CIRCUIT=$1
    CIRCUIT_DIR=$CIRCUIT_BASE_DIR/$CIRCUIT
    BYTECODE=$CIRCUIT_DIR/target/$CIRCUIT.json
    WITNESS=$CIRCUIT_DIR/target/$CIRCUIT.gz
    PROOF_DIR=proofs/$CIRCUIT

    echo -e "\n\n*** Proving circuit: $CIRCUIT\n"

    echo -e "*** Gates count\n"
    bb gates $SCHEME -b $BYTECODE

    echo -e "\n\n*** Create a verifier key\n"
    time bb write_vk $SCHEME -b $BYTECODE -o $PROOF_DIR

    echo -e "\n*** Create a proof for the circuit $CIRCUIT\n"
    time bb prove $SCHEME -b $BYTECODE -w $WITNESS -k $PROOF_DIR/vk -o $PROOF_DIR

    echo -e "\n*** Verify the created proof\n"
    time bb verify $SCHEME -p $PROOF_DIR/proof -k $PROOF_DIR/vk -i $PROOF_DIR/public_inputs
}

prove_circuit c00_fixed
prove_circuit c01_fixed_age
prove_circuit c02_device_fixed_age