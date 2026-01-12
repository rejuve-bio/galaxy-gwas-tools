TEST_SHED = testtoolshed
MAIN_SHED = toolshed
GALAXY_ROOT = $(shell pwd)/scripts/
VERSION = 0.0.1

test-tools:
	-@bash $(GALAXY_ROOT)/test_tools.sh $(GALAXY_ROOT)

create-test:
	-@bash $(GALAXY_ROOT)/create_shed.sh $(GALAXY_ROOT) $(TEST_SHED)

# to test-shed
upload-test:
	-@bash $(GALAXY_ROOT)/update_shed.sh $(GALAXY_ROOT) $(TEST_SHED)

update-test:
	-@bash $(GALAXY_ROOT)/update_shed.sh $(GALAXY_ROOT) $(TEST_SHED)

create-shed:
	-@bash $(GALAXY_ROOT)/create_shed.sh $(GALAXY_ROOT) $(MAIN_SHED)

# to upload-shed 
upload-shed:
	-@bash $(GALAXY_ROOT)/upload_shed.sh $(GALAXY_ROOT) $(MAIN_SHED)

update-shed:
	-@bash $(GALAXY_ROOT)/upload_shed.sh $(GALAXY_ROOT) $(MAIN_SHED)
	