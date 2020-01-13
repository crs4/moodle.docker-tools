#!/bin/bash

cd "${MOODLE_WWW_ROOT}"
while [[ ! -f "config.php" ]]; do
    echo "Waiting for 'config.php' configuration file..."
    sleep 5
done

if ! grep "questionbankcolumn" config.php; then 
    sed -i '/^require_once.*/i $CFG->questionbankcolumns = "checkbox_column,question_type_column,question_name_column,edit_action_column,preview_action_column,copy_action_column,delete_action_column,creator_name_column,modifier_name_column,local_questionbanktagfilter_question_bank_column";' config.php
else
    echo "'config.php' already up to date."
fi