/**
 * Created by Starforge on 19.03.2017.
 */
IP = '';
IPField = GetObject("IP");
function Start() {
    IP = document.getElementById("IP").value.toString().trim();
    if (!CheckIP()) {
        alert("Недопустимый адрес")
        return;
    }
    IP = document.getElementById("IP").value.toString().trim();
    window.location.href  = '/?ip='+IP;
}
function KeyStart(e) {
    if (e.keyCode == 13) {
        Start()
    }
}
function CheckIP() {
    IP = IP.replace(/[,\/ ю]/gi, ".").trim();
    var ret = true;
    if (IP.substr(0, 3) == "172") {
        alert("Диагностика сети 172 невозможна.\rПопробуйте использовать полное сетевое имя ")
        ret = false;
    }
    var reg = /(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([\w_-]{1,15}\.\w{3,8}\.oao\.rzd)/

    var r = reg.exec(IP)
    if (r == null) {
        ret = false
    }
    else {
        reg = /127\.\d{1,3}\.\d{1,3}\.\d{1,3}/
        if (reg.test(r)) {
            ret = false;
        }
        else {
            IPField.value = IP = r[0];
        }
    }
    return ret;
}
function GetObject(Name) {
    return document.getElementById(Name+"")
}
function doHeadlineVisibility() {
    IPField = GetObject("IP");
    var headline = document.getElementById("headline");
    var ieline = document.getElementById("ieline");
    var userAgent = navigator.userAgent;
    if ((userAgent.indexOf('MSIE 8.0') != -1) || (userAgent.indexOf('compatible') != -1) ) {
        headline.style.display = "none";
        ieline.style.display = "table-row";
    }
    else{
        ieline.style.display = "none";
        headline.style.display = "table-row";
    }
}