
function loginEvent(){
    var usernameText = document.getElementById("username").value;
    var passwordText = document.getElementById("password").value;
    var json_upload = JSON.stringify({account: usernameText, password :passwordText});
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", 'http://localhost:8080/loginInfo', false);
    xmlHttp.send(json_upload);
    window.alert(xmlHttp.responseText);
    return xmlHttp.responseText;
}
