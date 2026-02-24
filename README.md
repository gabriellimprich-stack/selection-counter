## Selection Counter — QGIS Plugin

A lightweight QGIS plugin that counts selected features grouped by a chosen attribute field, displaying the results in a clean, interactive table panel.

### Features

- Dockable panel that integrates naturally into the QGIS interface
- Layer and field dropdowns that populate automatically from the active project
- Auto-refresh: the table updates instantly whenever the selection changes
- Summary label showing total selected features and number of unique values
- Highlights the category with the highest count

### Installation

1. Download the `.zip` file from the [Releases](../../releases) page
2. Extract the `selection_counter/` folder into your QGIS plugins directory:
   - **Windows:** `C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux/macOS:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. In QGIS, go to `Plugins > Manage and Install Plugins > Installed` and enable **Selection Counter**

### Usage

1. Open the panel via the Vector menu or the toolbar icon
2. Select a vector layer and a grouping field from the dropdowns
3. Select features on the map — the table updates automatically

### Requirements

- QGIS 3.0 or higher

---

*This plugin was developed with assistance from [Claude](https://claude.ai), an AI assistant made by [Anthropic](https://www.anthropic.com).*
