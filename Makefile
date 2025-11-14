CREDS := credentials
CIRCUITS := circuits

all: issuer sign provers witness proof

clean:
	rm -rf credentials proofs
	find $(CIRCUITS) -name target | xargs rm -rf
	find $(CIRCUITS) -name "Prover*toml" | xargs rm -rf

issuer:
	./scripts/1-create-keys.py $(CREDS)

sign:
	./scripts/2-create-signed-credentials.py $(CREDS)

provers:
	./scripts/3-create-provers.py $(CREDS) $(CIRCUITS)

witness:
	./scripts/4-create-witness.sh

proof:
	./scripts/5-create-proof.sh
