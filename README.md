# Sop-to-Lop-Script
A Houdini Python GUI tool that automates importing SOP assets into LOPs, minimizing manual setup for Karma scenes.

#### Features
- Import scene assets into LOPs:
  - **All Together**: Imports everything at once.
  - **By Category**: Separates geometry, lights, and cameras.
  - **By Node/Prefix**: Filters imports based on selection or prefix.
- Scene graph path management with duplicate import detection.
- Automates creation of **Scene Import** and **Merge** nodes for Karma.

#### Usage
1. Launch the tool and specify the **Scene Graph Path**.
2. Choose the desired import mode.
3. Click **Create Karma Setup** to generate the nodes in the LOP network.
4. Verify the imported assets in Karma.

#### Installation
1. Download the script file from the repository.
2. 2. Create a new shelf tool in Houdini.
3. Ensure Karma and LOPs are enabled in your Houdini session.
3. Edit the new tool and add the script in the python module under the script tab.


## Prerequisites
- **Houdini** (with Karma rendering support for relevant tools).
- **PySide2** (for GUI-based scripts).


## Contribution
Contributions are welcome! Feel free to submit pull requests or raise issues for any suggestions or bugs.


## Acknowledgments
- **PolyHaven** for their open-access library and public API.
- The Houdini community for inspiring innovative tools and workflows.
