async function fetchTasksForClientAndCreateTable() {
  var client_id = new URL(document.location.href).searchParams.get('client_id');
  try {
    // /api/taskへアクセスしてデータを取得
    const response = await fetch(`/api/task?client_id=${client_id}`);
    if (response.ok) {
      const jsonData = await response.json();

      // テーブルにタイトルを追加
      let table = "<h2>Client Tasks</h2>";

      // HTMLテーブルを生成
      table += "<table border='1'><thead><tr>\
                <th>Task</th>\
                <th>Status</th>\
                <th>Task ID</th>\
                <th></th>\
                </tr></thead><tbody>";

      // JSONデータを行に変換
      for (const task of jsonData) {
        table += `<tr>
                    <td>${task.task_type}</td>
                    <td>${task.state}${addWaitingIcon(task.state)}</td>
                    <td>${task.task_id}</td>
                    <td><button onclick="deleteTask('${task.task_id}')" ${task.state=="processing"?' disabled':''}>Delete</button></td>
                  </tr>`;
      }
      table += "</tbody></table>";

      // tableを更新
      const clientTable = document.getElementById('task-table');
      if (clientTable) {
        clientTable.innerHTML = table;
      }
    } else {
      console.log(`Error: ${response.status}`);
    }
  } catch (error) {
    console.log(`Fetch failed: ${error}`);
  }
}

// /api/actions から取得できる実行可能ペイロードを表示する
// data format:
//   [{
//       "action":<payload class name:str>, 
//       "args":[
//           [<arugument type:str>, <arugument name:str>],
//           [<arugument type:str>, <arugument name:str>],
//           ...
//       ],...
//   }]
async function fetchPayloadTemplatesAndCreateTable() {
  try {
    const response = await fetch(`/api/actions`);
    if (response.ok) {
      const actions = await response.json();
      let maxArgs = checkMaxArgs(actions);

      // テーブルにタイトルを追加
      let table = "<h2>Payload List</h2>";

      // HTMLテーブルを生成
      table += "<table border='1'><thead><tr>\
              <th>Action</th>";
      for (i = 1; i <= maxArgs; i++) {
        table += `<th>Option ${i}</th>`;
      }
      table += "<th>Submit</th>\
              </tr></thead><tbody>";

      for (const action of actions) {
        table += `<tr><td>${action.action}</td>`;
        table += createActionForm(action, maxArgs);
        table += '</tr>';
      }
      table += "</tbody></table>";
      // 生成したテーブルを特定の<div>の末尾に挿入
      const tableContainer = document.getElementById('payload-table');
      if (tableContainer) {
        tableContainer.innerHTML = table;
      }
      // datalistを更新する
      for (const action of actions){
        for (const [argType, argName] of action.args){
          if (argType == "list"){
            fetchDatalistByArgName(argName);
          }
        }
      }
    }
    
  } catch (error) {
    console.log(`Fetch failed: ${error}`);
  }
}

function checkMaxArgs(actions) {
  var max = 0;
  for (const action of actions) {
    var cnt = 0
    for (arg of action.args) {
      if (arg[0] == "hidden") {
        continue;
      }
      cnt += 1;
    }
    if (max < cnt) {
      max = cnt;
    }
  }
  return max;
}

function createActionForm(action, maxArgs) {
  var form = '';
  var pos = 1;
  var id = 1;
  var argSize = action.args.length;
  for (arg of action.args) {
    var type = arg[0];
    var argName = arg[1];
    switch (type) {
      case 'hidden':
        console.log(type + ":" + argName);
        form += `<input id="${action.action}-${id}" type="hidden" name="${argName}" value="${getHiddenValueByArgName(argName)}">`;
        pos--;
        break;
      case 'list':
        console.log(type + ":" + argName);
        form += `<td>${argName}&nbsp;<input id="${action.action}-${id}" type="text" name="${argName}" autocomplete="on" list="${argName}-datalist"></td>`;
        form += `<datalist id="${argName}-datalist"></datalist>`
        break;
      case 'text':
        form += `<td>${argName}&nbsp;<input id="${action.action}-${id}" type="text" name="${argName}"></td>`;
        break;
      case 'checkbox':
        form += `<td>${argName}&nbsp;<input id="${action.action}-${id}" type="checkbox" name="${argName}"></td>`;
        break;
      case 'date':
        form += `<td>${argName}&nbsp;<input id="${action.action}-${id}" type="date" name="${argName}"></td>`;
        break;
      default:
        form += '<td></td>';
        break;
    }
    id++;
    pos++;
  }
  let pad = maxArgs - pos + 1;
  for (i = 0; i < pad; i++) {
    form += '<td>-</td>'
  }
  form += `<td><button onclick="addTask('${action.action}',${argSize});" id="${action.action}-button">Add</button></td>`;
  return form;
}

function getHiddenValueByArgName(name) {
  switch(name){
    case 'client_id':
      return new URL(document.location.href).searchParams.get('client_id');
    case 'c2_url':
      return new URL(document.location.href).origin;
    default:
      return '';
  }
}

async function fetchDatalistByArgName(name) {
  const dataList = document.getElementById(`${name}-datalist`);
  console.log(dataList);
  const client_id = new URL(document.location.href).searchParams.get('client_id');
  switch (name){
    case "teams_id":
      apiUrl =  `/api/teams/teams?client_id=${client_id}`;
      break;
    case "channel_id":
      apiUrl = `/api/teams/channels?client_id=${client_id}`
      break
    case "chat_id":
      apiUrl = `/api/teams/chats?client_id=${client_id}`
      break
    default:
      break;
  }
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    // JSONデータをdatalistオプションとして追加
    data.forEach(item => {
      const option = document.createElement('option');
      option.value = item[name];
      option.innerText = item["display_name"];
      dataList.append(option);
    });
    } catch (error) {
      console.error(`Error fetching and populating datalist for :${name}`, error);
  }
}

async function addTask(id,argSize) {
  // /api/task へPOST
  // Bodyに以下のJSONを期待する
  //   {
  //       "task_type": TASK_TYPE,
  //       "task_args": {
  //           "client_id": CLIENT_ID,
  //           "arg1" : ARG1,
  //           "arg2" : ARG2,
  //           ...
  //   }
  let body = {};
  let task_args = {};

  for (i = 1; i <= argSize; i++) {
    let name = document.getElementById(`${id}-${i}`).name;
    let value = document.getElementById(`${id}-${i}`).value;
    task_args[name] = value;
  }
  body["task_type"] = id;
  body["task_args"] = task_args;
  console.log(body);
  try {
    const response = await fetch("/api/task", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (response.ok) {
      const data = await response.json();
      console.log(data['message']);
      if (data['message'] == 'Submit new task.') {
        // テーブルのリフレッシュ
        fetchTasksForClientAndCreateTable();
      } else if (data['message'] == 'Task already exists.'){
        displayDialog("Task already exist.","warning")
      } else {
        displayDialog("Failed to add the action to a queue.");
      }
    } else {
      displayDialog("Failed to POST request");
    }
  } catch (error) {
    displayDialog("Failed to add the action to a queue.");
  }
}

async function addRawTask(raw_task) {
  let body = {};
  let task_args = {};
  let client_id = new URL(document.location.href).searchParams.get('client_id');
  task_args["client_id"] = client_id;
  body["task_type"] = "Raw";
  body["task_args"] = task_args;
  body["task_raw"] = raw_task;
  try {
    const response = await fetch("/api/task", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (response.ok) {
      const data = await response.json();
      console.log(data['message']);
      if (data['message'] == 'Submit new task.') {
        // テーブルのリフレッシュ
        fetchTasksForClientAndCreateTable();
      } else if (data['message'] == 'Task already exists.'){
        displayDialog("Task already exist.","warning");
      } else if (data['message'] == 'Invalide raw task format.'){
        displayDialog("Invalide raw task format.","warning");
      } else {
        displayDialog("Failed to add the action to a queue.");
      }
    } else {
      displayDialog("Failed to POST request");
    }
  } catch (error){
    displayDialog("Failed to add the action to a queue.");
  }
}

async function deleteTask(task_id) {
  // /api/taskへDELETE
  try {
    const response = await fetch(`/api/task?task_id=${task_id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      const data = await response.json();
      if (data.message == "Deleted.") {
        // テーブルのリフレッシュ
        fetchTasksForClientAndCreateTable();
      } else {
        displayDialog("Failed to POST request.");
      }
    } else {
      displayDialog("Failed to delete the task from a queue.");
    }
  } catch (error) {
    displayDialog("Failed to POST request.");
  }
}

document.getElementById("submit-json").addEventListener("click", function() {
  var jsonInput = document.getElementById("json-input").value;
  try {
    let raw_task = JSON.parse(jsonInput);
    document.getElementById("validation-message").innerHTML = "Valid JSON";
    addRawTask(raw_task);
  } catch(e) {
    displayDialog("Invalid JSON: " + e.message);
    document.getElementById("validation-message").innerHTML = "Invalid JSON: " + e.message;
  }
});

// main logic for client page
fetchTasksForClientAndCreateTable();
fetchPayloadTemplatesAndCreateTable();

// Update Task Data every minute
setInterval(fetchTasksForClientAndCreateTable, 60*1000);