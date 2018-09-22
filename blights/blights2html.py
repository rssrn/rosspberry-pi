import json
from string import Template

page_template = Template('''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Blights</title>
    <style>
    body {
        font-size: 200%;
    }
    table {
        border-spacing: 5px;
        width: 90%;
    }
    td {
        border-radius: 10px;
        width: 45px;
    }
    </style>
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
        <!-- position: $position -->
        <td style="background-color: $color"></td>
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
