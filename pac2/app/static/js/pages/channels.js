async function list_channel(client_id){
  add_teams = function(name){
    let details = document.createElement('details');
    let summary = document.createElement('summary');
    summary.innerHTML = name;
    let table = document.createElement('table');
    table.setAttribute('id', name);
    details.appendChild(summary);
    details.appendChild(table);
    document.body.appendChild(details);
  }

  add_channels = function(client_id, team_name, channel_id, channel_name){
    let tableElem = document.getElementById(team_name);
    let trElem = tableElem.insertRow(-1);
    let cellElem = trElem.insertCell(0);
    cellElem.setAttribute('id', channel_id);
    let div = document.createElement('div');
    div.setAttribute('onclick', `window.parent.messages.src='/portal/messages?client_id=${client_id}&channel_id=${channel_id}&team_name=${team_name}&channel_name=${channel_name}'`);
    div.innerHTML = channel_name;
    cellElem.appendChild(div);
  }

  try {
    const response1 = await fetch(`/api/teams/teams?client_id=${client_id}`);
    if(response1.ok) {
      const teams = await response1.json();
      for(team of teams) {
        let team_name = team.display_name;
        add_teams(team_name);
        const response2 = await fetch(`/api/teams/channels?teams_id=${team.teams_id}`);
        if(response2.ok) {
          const channels = await response2.json();
          for(channel of channels) {
            add_channels(client_id, team_name, channel.channel_id, channel.display_name);
          }
        } else {
          console.log(`Error to get channels: ${response2.status}`);
        }
      }
    } else {
      console.log(`Error to get teams: ${response1.status}`);
    }
  } catch(error) {
    console.log(`Fetch failed: ${error}`);
  }
}
