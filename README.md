# Tableau Health Monitor

A simple script intended to log the state of our Tableau Server cluster.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

1. Edit the Windows Firewall on the primary node of your Tableau Server cluster to allow for connections on the TSM port to the computer hosting this script.
2. Python dependencies for this project can be found in the `requirements.txt` file. Install using pip as normal.

```
pip install -r requirements.txt
```

### Configuring

Configuration for this script is done via environment variables. You can set these through your OS, scheduler, or a `.env` file. These variables are loaded via the library, python-dotenv.

```
tabhealth_server=
tabhealth_port=
tabhealth_username=
tabhealth_password=
tabhealth_console_logging=true
tabhealth_file_logging=true
```

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