async function fetchClientsAndCreateTable() {
  try {
    const response = await fetch('/api/clients');
    if (response.ok) {
      const jsonData = await response.json();

      // テーブルにタイトルを追加
      let table = "<h2>Client Information</h2>";

      // HTMLテーブルを生成
      table += `<table border='1'><thead><tr>\
                    <th>Client ID</th>\
                    <th>Method</th>\
                    <th>XOR Encode</th>\
                    <th>Username</th>\
                    <th>Email</th>\
                    <th>Tenant ID</th>\
                    <th>Last Update</th>\
                    <th></th>\
                  </tr></thead><tbody>`;

      // JSONデータを行に変換
      for (const client of jsonData) {
        table += `<tr>
                    <td>${client.client_id}</td>
                    <td>${client.method}</td>
                    <td>${client.is_encoded ? 'Yes' : 'No'}</td>
                    <td><a href="/portal/client?client_id=${client.client_id}" target="_blank">${client.username}</a></td>
                    <td>${client.email}</td>
                    <td>${client.tenant_id}</td>
                    <td>${client.updated_at}</td>
                    <td><button onclick="deleteClient('${client.client_id}')">Delete</button></td>
                  </tr>`;
      }
      table += "</tbody></table>";
      // tableを更新
      const clientTable = document.getElementById('client-table');
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

async function fetchTasksAndCreateTable() {
  try {
    // /api/taskへアクセスしてデータを取得
    const response = await fetch('/api/tasks');
    if (response.ok) {
      const jsonData = await response.json();

      // テーブルにタイトルを追加
      let table = "<h2>Current Tasks</h2>";

      // HTMLテーブルを生成
      table += "<table border='1'><thead><tr>\
                <th>Client ID</th>\
                <th>Task</th>\
                <th>Status</th>\
                <th>Task ID</th>\
                </tr></thead><tbody>";

      // JSONデータを行に変換
      for (const task of jsonData) {
        table += `<tr>
                    <td>${task.client_id}</td>
                    <td>${task.task_type}</td>
                    <td>${task.state}${addWaitingIcon(task.state)}</td>
                    <td>${task.task_id}</td>
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

async function deleteClient(client_id) {
  // /api/clientへDELETE
  try {
    const response = await fetch(`/api/client?client_id=${client_id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      const data = await response.json();
      if (data.message == "Deleted.") {
        // テーブルのリフレッシュ
        fetchTasksAndCreateTable();
        fetchClientsAndCreateTable();
      } else {
        displayDialog("Failed to send DELETE request.");
      }
    } else {
      displayDialog("Failed to delete the task from a queue.");
    }
  } catch (error) {
    displayDialog("Failed to send DELETE request.");
  }
}

function inputChange(event){
  let isDropbox = event.currentTarget.value == "dropbox"
  document.getElementById('sendtoLabel').textContent = isDropbox ? "Dropbox Connection ID" : "POST URL"; 
}

function downloadButonCallback(event) {
  event.preventDefault();
  const sendto = document.getElementById('sendto').value;
  const mngID = document.getElementById('mngID').value;
  let isDropbox = document.getElementById('method').value == "dropbox";
  if (!isValidFlowManagementConnectionId(mngID)) {
    if (!isValidConnectionId(mngID)) {
      displayDialog('Invalid Flow Management Connection ID.');
      return;
    }
  }
  if (isDropbox) {
    if (!isValidConnectionId(sendto)) {
      displayDialog('Invalid Dropbox Connection ID.');
      return;
    }
  } else {
    if (!isValidUrl(sendto)) {
      displayDialog('Invalid URL.');
      return;
    }
  }
  document.getElementById("getInitalPayloadForm").submit();
  
  // post-download process
  document.getElementById('sendto').value = "";
  document.getElementById('mngID').value = "";
  setTimeout(fetchClientsAndCreateTable, 1*1000);
}

/* ----------
/* Main logic
/* ---------- */

fetchClientsAndCreateTable();
fetchTasksAndCreateTable();

// Change display text of sendto element. 
let method = document.getElementById('method');
method.addEventListener('change', inputChange);

// Add Validation before submit action
let downlaod_button = document.getElementById('getInitalPayloadForm')
downlaod_button.addEventListener('submit', function(event){
  downloadButonCallback(event);
});

// Update Task Data every minute
setInterval(fetchTasksAndCreateTable, 60*1000);
