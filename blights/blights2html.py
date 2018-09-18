import json
from string import Template

page_template = Template('''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
  </head>
  <body>
    <table>
    $content
    </table>
  </body>
</html>
''')

row_template = Template('''
      <tr>
        <td> $position </td>
        <td style="background-color: $color "> $color </td>
        <td> $status </td>
      </tr>''')

with open('mon.json') as json_data:
    d = json.load(json_data)

rows = ''
for alert in d['alerts']:
    rows += row_template.substitute(
        position = alert['position'],
        color    = alert['spec']['color'],
        status   = alert['reason']
    )

print(page_template.substitute(content=rows))
