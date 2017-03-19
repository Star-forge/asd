/**
 * Created by Starforge on 19.03.2017.
 */

function doHeadlineVisibility() {
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