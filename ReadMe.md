## If running this for the first time, youll need to run the following to get the required dependencies

```pip install selenium requests pandas openpyxl```

## To Update Prices

1. Duplicate the Clean Leves into Prepped Leves if needed (only needed when leves get an update)

2.  Update the WORLD constant in update_leve_prices.py to your world, default is Famfrit and save the script

3. Run master.py (will automatically run update_leve_prices.py and then export.py) to create the Leve Profits.xlsx file



## To Update the Class Leves 
### Only needs to be done once/xpac or whenever new leves are added

1. Navigate to https://ffxivteamcraft.com/levequests?min=1&max=100 and select the job you want to export

2. Open your browser dev console and paste the following

```
(() => {
  const rows = Array.from(document.querySelectorAll('div.leve-row'));
  const data = rows.map(el => {
    // 1. Leve Name
    const nameEl = el.querySelector('app-i18n-name[content="leves"] span');
    const leveName = nameEl ? nameEl.textContent.trim() : '';

    // 2. Leve Item + quantity
    const itemContainer = el.querySelector('app-i18n-name[content="items"]')?.parentElement;
    const leveItem = itemContainer ? itemContainer.textContent.trim() : '';

    // collect all <b> tags to find level, exp, gil
    const bolds = Array.from(el.querySelectorAll('b'));

    // 3. Leve Level
    const lvlEl = bolds.find(b => b.textContent.trim().startsWith('Lvl'));
    const leveLevel = lvlEl
      ? lvlEl.textContent.trim().replace(/^Lvl\s*/, '')
      : '';

    // 4. Leve EXP
    const expEl = bolds.find(b => b.textContent.trim().startsWith('Exp'));
    const leveExp = expEl && expEl.nextSibling
      ? expEl.nextSibling.textContent.trim()
      : '';

    // 5. Leve Gil
    const gilEl = bolds.find(b => b.textContent.trim().startsWith('Gil'));
    const leveGil = gilEl && gilEl.nextSibling
      ? gilEl.nextSibling.textContent.trim()
      : '';

    return {
      "Leve Name": leveName,
      "Leve Item": leveItem,
      "Leve Level": leveLevel,
      "Leve EXP": leveExp,
      "Leve Gil": leveGil
    };
  });

  console.log(data);
  return data;
})();
```


3. Copy the output into the required Class Leves File

4. Duplicate the json files from Class Leves into the Clean Leves Directory

4. Run clean.py

5. Run fetch_leve_item_ids.py to fetch the leve item ids from universalis

