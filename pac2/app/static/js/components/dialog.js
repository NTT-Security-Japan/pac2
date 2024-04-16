function closeDialog() {
  dialog.style.display = 'none';
}

function clickOutside(e) {
  if (e.target == dialog) {
    dialog.style.display = 'none';
  }
}

function displayDialog(msg, loglevel = "error") {
  document.getElementById("dialog-msg").innerHTML = msg;

  let header = document.querySelector('.content-header');
  let title = document.querySelector('.msg-title');

  switch (loglevel) {
    case 'error':
      header.style.background = 'IndianRed';
      title.innerHTML = 'Error';
      break;
    case 'warning':
      header.style.background = 'GoldenRod';
      title.innerHTML = 'Warning';
      break;
    case 'info':
      header.style.background = 'MediumSeaGreen';
      title.innerHTML = 'Information';
      break;
    default:
      header.style.background = 'IndianRed';
      title.innerHTML = 'Error';
  }

  dialog.style.display = 'block';
}

const dialog = document.getElementById('flat-dialog');
const closeButton = document.getElementsByClassName('close-dialog')[0];
closeButton.addEventListener('click', closeDialog);
document.addEventListener('click', clickOutside);