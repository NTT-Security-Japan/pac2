import json
from pypowerautomate.actions import *

task = Actions()
task += GetAllTeamsAction("GetAllTeams")

http_action = HttpAction("PostData","https://example.com/","POST")

http_action.set_body(f"@body('GetAllTeams')")

task += http_action

s = json.dumps(task.export(),indent=2)
print(s)