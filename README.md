# GNSS Quality Evaluation Tool
This tool's purpose is to get raw data from Ramp's DB, analyze it
and show the results on graphs in order to evaluate the quality of the data
provided by the RedBox.

## Setup
- Get the DB credentials and load them into the .env file.
- Run 'pip3 install -r requirements.txt' in order to install
the required dependencies.

## Run
To run execute the command 'python3 main.py -s ... -e ...'.

Note that start and end times are mandatory fields.

Run python3 main.py --help for more information about available arguments for configuration.
