#!/usr/bin/env bash
# Contrôle une combinaison démo × langue : check et snapshot opèrent sur les valeurs
# par défaut des variables de index.html, qu'on bascule le temps du contrôle.
#   scripts/qa.sh <analyse|entretien|lettre> <fr|en> [check|snapshot] [--at 1,2,3]
set -euo pipefail
cd "$(dirname "$0")/.."
demo="$1"; lang="$2"; action="${3:-snapshot}"; shift $(( $# >= 3 ? 3 : 2 ))
cp index.html .index.qa.bak
trap 'mv .index.qa.bak index.html' EXIT
python3 - "$demo" "$lang" <<'PY'
import re, sys
demo, lang = sys.argv[1], sys.argv[2]
s = open("index.html").read()
q = r'(?:"|&quot;)'  # le CLI peut réécrire les guillemets de l'attribut en &quot;
s, n1 = re.subn(r'(' + q + r'default' + q + r':' + q + r')(analyse|entretien|lettre)', r'\g<1>' + demo, s, count=1)
s, n2 = re.subn(r'(' + q + r'default' + q + r':' + q + r')(fr|en)(?=' + q + r')', r'\g<1>' + lang, s, count=1)
if n1 != 1 or n2 != 1:
    sys.exit("qa.sh : variables demo/lang introuvables dans index.html")
open("index.html", "w").write(s)
PY
if [ "$action" = "check" ]; then
  npx -y hyperframes@0.8.80 check "$@"
else
  rm -rf "snapshots/$demo-$lang"
  npx -y hyperframes@0.8.80 snapshot "$@"
  mkdir -p "snapshots/$demo-$lang" && mv snapshots/frame-*.png snapshots/contact-sheet*.jpg "snapshots/$demo-$lang/" 2>/dev/null || true
fi
