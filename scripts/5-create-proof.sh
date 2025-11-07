#!/bin/bash

CIRCUIT=c01_fixed_age
CIRCUIT_BASE_DIR=circuits
CIRCUIT_DIR=$CIRCUIT_BASE_DIR/$CIRCUIT
PROOF_DIR=proofs

bb gates -s ultra_honk -b $CIRCUIT_DIR/target/$CIRCUIT.json
bb prove -d -s ultra_honk -b $CIRCUIT_DIR/target/$CIRCUIT.json -w $CIRCUIT_DIR/target/$CIRCUIT.gz --write_vk -o $PROOF_DIR
bb verify -d -s ultra_honk -p $PROOF_DIR/proof -k $PROOF_DIR/vk -i $PROOF_DIR/public_inputs
