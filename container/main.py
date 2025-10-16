# import debugpy  # for debug
import rdetoolkit

from modules import datasets_process

# START for docker's debug
# debugpy.listen(('0.0.0.0', 5678))  # Listening on port 5678.
# print("Waiting for debugger to attach...")
# debugpy.wait_for_client()  # Waiting for the debugger to connect.
# END for docker's debug

rdetoolkit.workflows.run(custom_dataset_function=datasets_process.dataset)
