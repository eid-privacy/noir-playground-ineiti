#!/bin/bash

CIRCUIT=circuits/01-fixed-age
PROOF_DIR=proofs

bb gates -s ultra_honk -b $CIRCUIT/target/age_verification.json
bb write_vk -d -s ultra_honk -b $CIRCUIT/target/age_verification.json -o $PROOF_DIR
bb prove -d -s ultra_honk -b $CIRCUIT/target/age_verification.json -w $CIRCUIT/target/age_verification.gz -k $PROOF_DIR -o $PROOF_DIR
bb verify -d -s ultra_honk -p $PROOF_DIR -k $PROOF_DIR -i $PROOF_DIR/public_inputs
