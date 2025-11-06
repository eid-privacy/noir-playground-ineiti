#!/bin/bash

for circuit in circuits/*; do
    if [ -f $circuit/Nargo.toml ]; then
      echo "Executing circuit $circuit"
      (cd $circuit && nargo execute -p Prover_0.toml)
    fi
done
