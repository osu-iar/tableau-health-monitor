# Tableau Health Monitor

A simple script intended to log the state of our Tableau Server cluster.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

1. Edit the Windows Firewall on the primary node of your Tableau Server cluster to allow for connections on the TSM port to the computer hosting this script.
2. Python dependencies for this project can be found in the `requirements.txt` file. Install using pip as normal.
3. An AD member in the group, `tsmadmins`. See the secion, _Windows Configuration_.

```
pip install -r requirements.txt
```

### Script Configuration

Configuration for this script is done via environment variables. You can set these through your OS, scheduler, or a `.env` file. These variables are loaded via the library, python-dotenv.

The value of `tabhealth_server` needs to start with `https://`. Otherwise, the requests library will throw a `requests.exceptions.InvalidSchema` exception.

```
tabhealth_server=https://
tabhealth_port=
tabhealth_username=
tabhealth_password=
tabhealth_console_logging=true
tabhealth_file_logging=true
```

### Windows Configuration

TSM users are members of either the VM's local `Administrators` or `tsmadmins` group. Running this script with credentials for a VM credentials **is not advised**. The latter option, `tsmadmins` does not exist by default. If you haven't done so already, create this group using `lusrmgr.msc` and add your AD member to it.

This will automatically grant the user access to the TSM interface. No restart is necessary.

### Executing program

Simply execute the file, `main.py`.

```
python main.py
```

## Help

## Authors

- Jacob Mastel <jacob.mastel@oregonstate.edu>

## Version History

* 1.0
  * Initial Release

## License

## Acknowledgments