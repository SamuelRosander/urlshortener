function dismiss(element){
    element.parentNode.classList.add("hidden");
};

flashes = document.getElementsByClassName("flash");
for (let i=0; i<flashes.length; i++) {
    flashes[i].addEventListener("transitionend", () =>  { 
        flashes[i].style.display = "none"; 
    }) 
}

function toggleUserMenu() {
    document.getElementById("user-menu").classList.toggle("visible");
    document.getElementById("user-icon").classList.toggle("active");
}

document.onmouseup = function(e) {
    e.preventDefault()
    if ((e.target.id != "menu-icon") 
            && (e.target.id != "user-icon")
            && (e.target.parentElement.id != "user-menu")) {
        document.getElementById("user-menu").classList.remove("visible");
        document.getElementById("user-icon").classList.remove("active");

    }
}

function copyURL(clickedButton, short_url) {
    let allClickedButtons = document.getElementsByClassName("clicked")

    for (var i=allClickedButtons.length-1; i>=0; i--) {
        let icon = allClickedButtons[i].getElementsByClassName("bx-check")[0]
        icon.classList.replace("bx-check", "bx-copy")
        allClickedButtons[i].classList.remove("clicked")
    }
  
    let activeIcon = clickedButton.getElementsByTagName("i")[0]
    activeIcon.classList.replace("bx-copy", "bx-check")
    clickedButton.classList.add("clicked")

    let copyText = 
        document.getElementById("short_url-" + short_url);
    navigator.clipboard.writeText(copyText.innerText);
}