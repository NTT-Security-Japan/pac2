function closeTermOfUse() {
  const terms = document.getElementById('term-of-use');
  terms.style.display = 'none';
}

function displayTermOfUse() {
  const terms = document.getElementById('term-of-use');
  terms.style.display = 'block';
}

const loginButton = document.getElementById("login-button");
loginButton.addEventListener('click', function () {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  if (username == '' || password == '') {
    displayDialog("Username and password are required.", "error");
  } else {
    document.getElementById('hiddenUsername').value = username;
    document.getElementById('hiddenPassword').value = password;
    displayTermOfUse();
  }
});

const closeTermsButton = document.getElementsByClassName("close-dialog")[1];
closeTermsButton.addEventListener('click', function () { closeTermOfUse() });

const cancelLoginButton = document.getElementById("cancel-button");
cancelLoginButton.addEventListener('click', function () { closeTermOfUse() });
