# ESO-trade-mon
Purpose: Searches for the latest price drop on specified ESO game items and sends an email notification. You can schedule this program to run every minute throughout the day. It will help you get the item at your desired price on time while you are busy with something else.

Scenario: Certain popular items have prices that remain high. Occasionally, discounted sales will appear, but they are gone very soon. This tool helps you get them before it's too late.

## Installation
To use this script, Python 3.x is needed to be installed on the system. It can be download the latest version of Python from the official website: "https://www.python.org/downloads/"

Also, install chrome,selenium and webdriver-manager. This example setup on Linux Ubuntu with
1. Chrome - DEB Apps v139.0 Ref.: https://pkgs.org/download/google-chrome-stable
2. selenium - check and upgrade version to match with chrome installed. Ref.:https://www.selenium.dev/blog/2025/
```python
    pip3 install selenium==4.35.0 --break-system-packages
```
3. webdriver-manager . Ref.: https://pypi.org/project/webdriver-manager/
4. Set an gmail app password for smtp. Ref.: https://myaccount.google.com/apppasswords

## Usage

Wishlist input file: eso-trade-items.yml specify item name, URL and threshold
1. item name : For input file readability only.
2. URL : Copy the URL after your found your target item with max price filtered and sort by lastseen. (See sample URL parameter &SortBy=LastSeen&Order=desc)
3. minThershold : send you alert only when that items appear within the minutes you want e.g. "240" mean last seen less than 240 minutes.


To run the script, open your terminal and navigate to the directory where the eso-trade-price-alert file is located. Then run the following command:
```bash
source set_env.sh && python3 eso-trade-price-alert.py
```
OR debug in vscode with .vscode/launch.json set 

## Output
  - Receving alert e-mail when any item found beyond thershold
  - Log files are supporting the rule update and review

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License - see the LICENSE file for details.
