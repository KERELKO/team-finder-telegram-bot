EXEC_APP = docker exec -it app


.PHONY: test-details
test-details:
	${EXEC_APP} pytest tests/details
