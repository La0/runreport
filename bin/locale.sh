#!/bin/bash
HELP_TPL="templates/help.html"

if [[ -f $HELP_TPL ]]; then
  rm $HELP_TPL
fi

# Extract from help macros
git grep -h 'macros.help' templates | \
  sed 's/{{ macros.help(user, //g' | \
  sed 's/ }}//g' | \
  sed 's/, _(/ }} {{ _(/g' | \
  sed 's/$/ }}/g' | \
  sed 's/^\s*/{{ /g' \
  > $HELP_TPL

# Run translation detection
./manage.py makemessages -v 1 -l fr -l en -i "*.txt" -i "*.json" -i "*.md"  -i "celery*" -i "*.sh" -i "medias" -i "final" -i "mails_debug" --keep-obsolete --no-location

# Cleanup
rm $HELP_TPL
