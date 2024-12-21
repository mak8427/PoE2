Here's a rewritten and improved README following standard conventions:

---


# Path of Exile 2 Trade Client

## Overview

This is a Python-based client for interacting with the Path of Exile trade API (`pathofexile.com/trade2`). It provides a demonstration of how to perform item searches, set up live searches, and send whisper messages using the API.

The project serves as an example for developers interested in integrating Path of Exile trading functionality into their own applications.

---

## Features

- **Item Search:** Query the Path of Exile trade API to find specific items.
- **Live Search:** Monitor the trade API for new listings of specific items.
- **Whisper Integration:** Automatically generate whisper messages to contact sellers directly for trades.

---

## Prerequisites

Before running this project, ensure you have the following:

1. **Python 3.7 or higher** installed.
2. **Pip** for managing Python dependencies.
3. A valid Path of Exile account with an active `POESESSID`. Set this session ID as an environment variable for API access:
   ```bash
   export POESESSID=<your-session-id>
   ```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ChanceToZoinks/poe_trade_client
   cd poe_trade_client
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the application:
```bash
python3 ./app.py
```

By default, the following actions are performed:

1. **Item Search:** Searches for the item "Redbeak" on the "Standard" league. The first 10 results are saved to a file named `redbeak_search.json`.

2. **Send Whisper Message:** Automatically sends a whisper for an "Incandescent Heart" that is listed on the "Standard" league.

3. **Live Search:** Sets up a live search for "Tabula Rasa" on the "Standard" league, monitoring the trade API for new listings.

---

## Configuration

The search and live search parameters can be modified in the script (`app.py`) to match your requirements. Key areas to customize:

- **Search Terms:** Modify the search configuration to look for different items.
- **League:** Change the league to match your current Path of Exile league (e.g., "Standard", "Hardcore").
- **Whisper Targets:** Update the target and item details for the whisper feature.

---

## Example Outputs

1. **Search Results File:**  
   Search results for "Redbeak" are stored in `search.json`.

2. **Whisper Messages:**  
   Generated whisper messages are sent directly via the Path of Exile in-game chat.

3. **Live Search Monitoring:**  
   Real-time monitoring of the trade API outputs new listings for "Tabula Rasa" in the terminal.

---

## Contributing

Contributions are welcome! If you would like to add new features or improve existing functionality, feel free to open a pull request or submit an issue.

---


## Author

Developed by [Mak8427](https://github.com/mak8427).
For more information on Path of Exile APIs, visit the official [Developer Docs](https://www.pathofexile.com/developer/docs).
Many thanks to [ChanceToZoinks](https://github.com/ChanceToZoinks)
---



