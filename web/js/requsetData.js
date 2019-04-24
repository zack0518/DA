var url = 'http://localhost:8081'

function loginEvent(){
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
      console.log("login")
      window.location.replace("e_bank.html");
    }
    return xmlHttp.responseText;
}

function dataLoads(){
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
  var accountText = document.getElementById("account").value;
  var amountText = document.getElementById("amount").value;
  var json_upload = JSON.stringify({account: accountText, amount : amountText});
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("POST", url+'/transferEvent', false);
  xmlHttp.send(json_upload);
  return xmlHttp.responseText;
}
