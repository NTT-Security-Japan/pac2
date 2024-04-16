import {Runtime, Inspector} from "../utils/runtime.js"
import define from "../components/forcegraph.js"

async function getInfo(client_id, channel_id) {
  try {
    const response = await fetch(`/api/client?client_id=${client_id}`);
    if(response.ok) {
      const value = await response.json();
      let my_id = value.user_uuid;
      displayMessages(channel_id, my_id);
    } else {
      console.log(`Error: ${response.status}`);
    }
  } catch(error) {
    console.log(`Fetch failed: ${error}`);
  }
}

async function displayMessages(channel_id, my_id) {
  let add_msg = function(subject, msg, who, id, datetime){
    let msgs = document.getElementById('msgs');
    let li = document.createElement('li');
    li.classList.add("msgbox");
    if(my_id == id){
      li.classList.add("me");
    }else{
      li.classList.add("someone");
    }
    let div = document.createElement('div');
    div.className = 'datetime';
    div.innerHTML = `${who} ${datetime}`;
    let div_title = document.createElement('div');
    div_title.className = 'subject';
    div_title.innerHTML = `${subject}`
    let p = document.createElement('p');
    p.innerHTML = msg;
    p.className = 'msg';
    li.appendChild(div)
    li.appendChild(div_title);
    li.appendChild(p);
    msgs.appendChild(li);
  }
  try {
    const response = await fetch(`/api/teams/messages?channel_id=${channel_id}`);
    if(response.ok) {
      const messages = await response.json();

      let cmpTime = function(a, b) {
        var res = 0;
        if(a.create_datetime < b.create_datetime) {
          res = -1;
        } else if(a.create_datetime > b.create_datetime) {
          res = 1;
        }
        return res;
      }

      messages.sort(cmpTime);
      for(let message of messages) {
        let subject = message.subject;
        let text = message.body.content;
        if(text != "<systemEventMessage/>"){
          add_msg(subject, text, message.from.displayName, message.from.id, message.create_datetime);
        }
      }
    } else {
      console.log(`Error: ${response.status}`);
    }
  } catch(error) {
    console.log(`Fetch failed: ${error}`);
  }
}

// Sort out the left bar style
function sortLeftBar(channel_id) {
  let tables = window.parent.channels.contentDocument.getElementsByTagName("table");
  for (let table of tables) {
    if(!table.hasChildNodes()){
      continue;
    }
    let trs = table.children[0].children;
    let found = false;
    for (let tr of trs){
      let td = tr.children[0];
      if(td.id == channel_id) {
        td.style.backgroundColor = "#e0e0e0";
        table.parentNode.open = true;
        found = true;
      } else {
        td.style.backgroundColor = "#f0f0f0";
        td.addEventListener('mouseover', function() {
          td.style.backgroundColor = '#e0e0e0';
        });
        td.addEventListener('mouseleave', function() {
          td.style.backgroundColor = '#f0f0f0';
        });
      }
    }
    if(!found){
      table.parentNode.open = false;
    }
  }
}

// main logic for messages page

const channel_id = new URL(window.location.href).searchParams.get("channel_id");
const team_name = new URL(window.location.href).searchParams.get("team_name");
const channel_name = new URL(window.location.href).searchParams.get("channel_name");
const metaTag = document.querySelector('meta[name="clientid"]');
const client_id = metaTag ? metaTag.content : null;

if(channel_id == null) {
  document.getElementById("title").innerHTML = "Channels and Messages Tree";
  const runtime = new Runtime();
  const main = runtime.module(define, Inspector.into(document.body));
} else {
  document.getElementById("title").innerHTML = `Messages in ${team_name}: ${channel_name}`;
  await getInfo(client_id ,channel_id);
}
sortLeftBar(channel_id);