#!/data/data/com.termux/files/usr/bin/bash

REPO="$HOME/TABELA"
SRC="$HOME/storage/downloads"
DEST="$REPO/market_data"
PHONE_DEST="$HOME/storage/downloads"

cd "$REPO" || exit 1

mkdir -p "$DEST"

mapfile -t FILES < <(ls -t "$SRC"/*.csv 2>/dev/null | head -n 2)

ETF_FILE="${FILES[0]}"
STOCKS_FILE="${FILES[1]}"

if [ -n "$ETF_FILE" ]; then
  mv -f "$ETF_FILE" "$DEST/ETF.csv"
  echo "Moved newest file to ETF.csv"
else
  echo "No newest CSV found."
fi

if [ -n "$STOCKS_FILE" ]; then
  mv -f "$STOCKS_FILE" "$DEST/stocks.csv"
  echo "Moved second newest file to stocks.csv"
else
  echo "No second CSV found."
fi

echo "Running main.py..."
python main.py || exit 1

echo "Copying market_data to phone Downloads..."
rm -rf "$PHONE_DEST/market_data"
cp -r "$DEST" "$PHONE_DEST/"

echo "Done."

