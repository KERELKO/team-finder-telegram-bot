EXEC_APP = docker exec -it app


.PHONY: test-details
test-details:
	${EXEC_APP} pytest tests/details

.PHONY: test-domain
test-domain:
	${EXEC_APP} pytest tests/domain

.PHONY: tests
tests:
	${EXEC_APP} pytest tests
