# PowerTrace

Minimal setup and run instructions for PowerTrace.

## Prerequisites

### Hardware

- [Seeed Studio XIAO-ESP32S3-Plus](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) development  board
- [Adafruit microSD Card BFF](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-microsd-card-bff.pdf) shield
- [Texas Instrument INA228](https://www.ti.com/document-viewer/ina228/datasheet) measurement module
- USB-A to USB-C cable

### Software

- Python 3.14+
- PyCharm 2026.0+

## Installation

```bash
git clone https://github.com/Christ0u/PowerTrace.git
cd PowerTrace
```

Create and activate virtual environment

```bash
python.exe -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## PyCharm configuration

### Python interpreter configuration

Open PyCharm

1. `File` > `Open` and select the project folder
2. `File` > `Settings` > `Python` > `Interpreter`
3. `Add Interpreter` > `Add Local Interpreter`
4. `Select existing` and point to the project's virtual environement (`...\.venv\Scripts\python.exe`)

### MicroPython configuration

1. `File` > `Settings` > `Languages & Frameworks` > `MicroPython Tools`
2. Check the `Enable MicroPython support` box
3. Hold the BOOT button on the ESP32-S3 while plugging USB
4. Click `Install or update MicroPython firmware`:
    - MCU: `ESP32S3`
    - Board variant: `XIAO ESP32S3`
    - Check the `Erase flash first` box
    - Uncheck the `Connect to the device after flashing` box
    - Click `Flash` and wait for completion
5. Reconnect the board, select the correct COM port in `MicroPython Tools` menu and click `Connect device`

### Running configuration

Click on `Run / Debug Configurations` drop-down menu then `Edit Configurations`

`Add new run configuration` > `MicroPython Tools` > `Upload`
  - Name: `PowerTrace`
  - Define a source mapping with Local path: `<project folder>`

Recommended exclusions

| Value           | Exclude type  | Exclude from uploads | Exclude from synchronisation |
|-----------------|---------------|----------------------|------------------------------|
| /venv           | Absolute Path | Yes                  | No                           |
| /LICENSE        | Absolute Path | Yes                  | No                           |
| /pyproject.toml | Absolute Path | Yes                  | No                           |
| /temp           | Absolute Path | Yes                  | No                           |
| /doc            | Absolute Path | Yes                  | No                           |
| *.md            | Pattern       | Yes                  | No                           |
| *.txt           | Pattern       | Yes                  | No                           |
| .*              | Pattern       | Yes                  | No                           |

Check the `Reset on success` (Soft Reset) and `Synchronize` boxes

### Running the project

Select the `PowerTrace` configuration and click  the green triangle-shaped `Run` button

### Troubleshooting

- Board not detected: verify COM port and drivers.
- Upload fails: reflash MicroPython firmware and verify exclusions so large or irrelevant files are not uploaded.

For further help, open an issue on the repository.