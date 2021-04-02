#!/bin/bash

echo "<odoo><data>"
while read line
do
  nombre=$(echo $line | cut -d',' -f1)
  dni=$(echo $line | cut -d',' -f2)
  year=$(echo $line | cut -d',' -f3)
  echo "<record id='student$dni' model='school.student'>"
  echo "<field name='name'>$nombre</field>"
  echo "<field name='dni'>$dni</field>"
  echo "<field name='birth_year'>$year</field>"
  echo "<field name='classroom' ref='school.classroom1'></field>"
  echo "<field name='photo'>$(base64 student.png)</field>"
  echo "</record>"
done
echo "</data></odoo>"