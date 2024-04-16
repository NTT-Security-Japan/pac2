# How-to: Establishing and Managing C2 Communication Channels

## Table of Contents

1. [Configuring Settings](#config-setup)
2. [Creating and Logging in Users](#user-creation-and-login)
3. [Creating a PAC2 Client Flow](#client-creation)
4. [Importing a PAC2 Client Flow](#client-import)
5. [Submitting a Preset Tasks](#task-registration)
6. [Identifying Task Status](#task-status-identification)
7. [Deleting a Task](#task-deletion)
8. [Using Preset Teams Tasks](#using-preset-teams-tasks)
8. [Deleting a PAC2 Client Flow](#client-deletion)
9. [Terminating a PAC2 Client Flow](#client-termination)

## Configuring Settings

- Description: The configuration file can be found at `[repository_base]/pac2/config.py`.
    - Configurable Options
        - SET_APPROVE_ACTION: Requires user approval for executing PAC2 payloads (Default: True)
        - SLEEP_TIME: Interval between PAC2 payload executions
        - JITTER: Jitter for sleep interval
        - DROPBOX_MOUNT_PATH: Specifies the mount path for Dropbox. No changes are needed if using `mount-dropbox.sh`

## Creating and Logging in Users

- Description: This section outlines the steps to create PAC2 users and how to log in.
- Prerequisites:
    - PAC2 is runnning.
    - No user exists on PAC2 (default)
- Steps:
    1. Access to http://localhost:9999/register . (Login is required if user already exists.)
    2. Enter `username` and `password`
    3. Press `Register` 
    4. Access to http://localhost:9999/login
    5. Enter `username` and `password` you set in 2.
    6. Press `Login`
    7. Press `Agree and Continue` if you can agree with the term-of-use.

## Creating a PAC2 Client Flow

- Description: This section outlines the steps to create a new PAC2 client.
- Prerequisites:
    - Possession of credentials for Power Automate Platform access.
    - Ability to use the Power Automate Flow Management Connector.
    - Access to either the Dropbox Connector or HTTP Connector.
- Steps:
    1. Navigate to [Power Automate](https://make.powerautomate.com) and log in using your credentials.
    2. Proceed to the 'Connection' tab.
    3. If connections to the prerequisite connectors do not exist, create these connectors from the connection page.
    4. Visit the page of the created connector and retrieve the connector ID from the URL query string:
        - Power Automate Management ID: e.g., `shared-flowmanagemen-95f92266-9e11-4604-974f-2e83905901a0` or `[0-9a-f]{32}`.
        - (If using Dropbox for C2 communication) Dropbox Connection ID: e.g., `[0-9a-f]{32}`.
    5. Access the PAC2 portal at [http://localhost:9999/portal](http://localhost:9999/portal).
    6. Enter the Power Automate Management connection ID into the first text box.
    7. Choose the connection method from the dropdown menu.
    8. Input the `C2 URL` or `Dropbox connection ID` into the designated text box.
    9. Click the `Download` button. The PAC2 Client Flow will be downloaded to your PC.

- Demo: The first half of the following demo video provides a tutorial on creating a client.
    - [How to Set Up PAC2 Client (Demo Movie)](../img/setup_PAC2_client_flow.mp4)


## Importing a PAC2 Client Flow

- Description: This section details the process of importing an existing PAC2 client.
- Steps:
    1. Go to [Power Automate](https://make.powerautomate.com) and log in with your credentials.
    2. Navigate to the 'My flows' tab.
    3. Click the 'Import' button and select 'Import Package (Legacy)'.
    4. Click the 'Upload' button and upload the zip file created in the [Creating a PAC2 Client Flow](#Creating-a-PAC2-Client-Flow) section.
    5. Once the upload is complete, choose the connections to be associated with the flow.
    6. Click 'Import'.
    7. Activate the Flow. This will initiate communication with PAC2.

- Demo: The latter half of the provided demo video offers guidance on importing a client flow.
    - [How to Set Up PAC2 Client (Demo Movie)](../img/setup_PAC2_client_flow.mp4)

## Submitting a Preset Task

- Description: This section provides instructions on how to register a new task.
- Prerequisites:
    - The PAC2 client flow is operational on Power Automate.
    - The communication of the PAC2 client flow is successful.
- Steps:
    1. Navigate to [http://localhost:9999/portal](http://localhost:9999/portal).
    2. Click on the Username displayed on the portal page.
    3. From the tasks listed on the 'Payload List' table, select the task you wish to submit.
        - For tasks requiring argument settings, configure the necessary arguments.`processing`
        - If argument information is available from other tasks, select this information from the dropdown menu.
    4. Click the 'Add' button to submit the task.
        - Note that the same task cannot be registered simultaneously.


## Identifying Task Status

- Description: How to ascertain the current status of a task.
- Status:
    - `submitted`: The task is registered but has not yet been retrieved by the PAC2 Client Flow.
    - `processing`: The PAC2 Client Flow is currently executing the task.
    - `finished`: The PAC2 Client Flow has completed the task.
    - `timeout`: The PAC2 Client Flow attempted to execute the task but timed out (default is 10 minutes).
    - `processed`: The PAC2 Client Flow has executed the task; this status is used for tasks where the completion status cannot be determined.

## Deleting a Task
- Description: Guidelines on how to remove an unnecessary task.
- Prerequisites:
    - The PAC2 client flow is active on Power Automate.
    - Successful communication has been established with the PAC2 client flow.
    - At least one task has been submitted to the client.
- Steps:
    1. Go to [http://localhost:9999/portal](http://localhost:9999/portal).
    2. Click on the Username displayed on the portal page.
    3. Identify and select the task you wish to delete from the 'Client Tasks' table.
    4. Press the 'delete' button.
        - Note: Tasks with the status 'processing' cannot be deleted.

## Using Preset Teams Tasks

### Collecting Team Channel Messages

- Description: How to collect Team channel messages using Preset Teams tasks.
- Prerequisites:
    - The PAC2 client flow is operational on Power Automate.
    - There is successful communication with the PAC2 client flow.
    - The Power Automate user has an established Teams Connector connection.
- Details:
    1. Register the 'CollectTeamsChannel' task to retrieve the list of Teams channels from the PAC2 client flow.
    2. After the completion of the first task, register the `CollectTeamsMessage` task to collect messages from the desired Teams channels.

### Viewing the Collected Information

- Description: Instructions on how to access information gathered using Preset Teams tasks.
- Steps:
    1. Navigate to [http://localhost:9999/portal](http://localhost:9999/portal).
    2. Click on the Username displayed on the portal page.
    3. Select the 'T' icon located on the left sidebar.
    4. A list of Teams will be displayed on the left side. Click on the Team name to view its channel list. Then, click on a channel name to view the messages within that channel.

## Deleting a PAC2 Client Flow

- Description: Steps to securely and effectively delete a client.
- Steps:
    1. Visit [http://localhost:9999/portal](http://localhost:9999/portal).
    2. Press the 'delete' button located in the Client List table.
        - Note: All tasks assigned to the client will be deleted simultaneously.

## Terminating a PAC2 Client Flow

- Description: Instructions on how to stop a client flow.
- Steps:
    1. Either delete the task or halt the PAC2 service to terminate the client flow.