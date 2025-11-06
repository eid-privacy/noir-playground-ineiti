all: issuer sign provers witness proof

clean:
	rm -rf credentials proofs

CREDS := credentials
CIRCUITS := circuits

issuer:
	./scripts/1-create-issuer-key.py $(CREDS)

sign:
	./scripts/2-create-signed-credentials.py $(CREDS)

provers:
	./scripts/3-create-provers.py $(CREDS) $(CIRCUITS)

witness:
	./scripts/4-create-witness.sh

proof:
	./scripts/5-create-proof.sh
