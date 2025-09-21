# easyepg lite

This tool retrieves the EPG data provided by Gracenote (TMS) and converts the JSON files into a single XMLTV file.

### Disclaimer

* This tool is not affiliated with Gracenote and is in no way sponsored or endorsed by Gracenote.

### Features

* Select the channels you need
* Add your unique EPG IDs to the channels
* Upload your playlist/link to map the IDs faster
* Search/Lineup feature to access channels/lists
* Settings tool to decide how to create the XMLTV file
* Scheduler: Download/create the files automatically

### Prerequisites

* Python 3.x (+ modules: beautifulsoup4, bottle, requests, xmltodict)
* Kodi 19.x or higher (addon version)
* TMS API key (Sample/Commercial Plan)

### How to start

##### PC

* Download the ZIP of the repository and extract it on your computer
* Run the terminal within the script directory
* Start the script: "python main.py"
* Visit "http://localhost:4000" and follow the instructions

#### Kodi

* Download the ZIP of the repository and store it on your Kodi machine
* Install the addon
* Visit "http://(IP address):4000" and follow the instructions
