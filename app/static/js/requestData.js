
function loginEvent(){

    var url = 'http://'+document.location.host
    var usernameText = document.getElementById("username").value;
    var username = usernameText;
    var passwordText = document.getElementById("password").value;
    var json_upload = JSON.stringify({account: usernameText, password :passwordText});
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", url+'/loginInfo', false);
    xmlHttp.send(json_upload);
    var json = JSON.parse(xmlHttp.responseText);
    window.alert(json.res)
    if (json.res == "Login Success"){
      window.location.href = url+'/bankPage'
    }
    return xmlHttp.responseText;
}

function dataLoads(){
   var url = 'http://'+document.location.host
   var xmlHttp = new XMLHttpRequest();
   xmlHttp.open("GET", url+'/balanceRequest',false);
   xmlHttp.send();
   var jsonResponse = JSON.parse(xmlHttp.responseText);
   document.getElementById("available").innerHTML = "$"+jsonResponse["balance"]
   document.getElementById("balance").innerHTML = "$"+jsonResponse["balance"]
   document.getElementById("current").innerHTML = "$"+jsonResponse["balance"]
   document.getElementById("total").innerHTML = "$"+jsonResponse["balance"]
   // var json = JSON.parse(xmlHttp.responseText);
   // document.getElementById("balance").innerHTML  = json.balance;
   return xmlHttp.responseText;
}


function transfer(){
  var url = 'http://'+document.location.host
  var accountText = document.getElementById("account").value;
  var amountText = document.getElementById("amount").value;
  var json_upload = JSON.stringify({account: accountText, amount : amountText});
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("POST", url+'/transferEvent', false);
  xmlHttp.send(json_upload);
  return xmlHttp.responseText;
}
