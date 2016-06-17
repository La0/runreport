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

# Add premium levels
for level in free premium_s premium_m premium_l ; do
  for part in name description price ; do
    echo "{{ _('premium.${level}.${part}') }}" >> $HELP_TPL
  done
done

# Run translation detection
./src/manage.py makemessages -v 1 -l fr -l en -i "*.txt" -i "*.json" -i "*.md"  -i "celery*" -i "*.sh" -i "medias" -i "final" -i "mails_debug" --no-location

# Cleanup
rm $HELP_TPL
