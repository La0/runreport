#!/bin/bash

function convert {
  NAME=$1
  SOURCE=$NAME.odt
  if [[ ! -f $SOURCE ]] ; then
    echo "Missing source to convert $SOURCE"
    exit 1
  fi

  # Convert to xhtml
  libreoffice --convert-to xhtml $SOURCE --headless

  # Cleanup through python
  # Dirty but quick.
  ../manage.py shell << EOF
from htmllaundry import sanitize
with open('$NAME.xhtml', 'r') as r:
  with open('$NAME.html', 'w') as w:
    w.write(sanitize(r.read()))

print 'done'
EOF

  # Cleanup
  rm $NAME.xhtml
}

# Main
#convert mentions
convert cgu
