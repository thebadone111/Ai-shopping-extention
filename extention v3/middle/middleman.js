function change_link(newLink) {
  const link_element = document.querySelector(".middle-link");
  link_element.textContent = newLink;
  link_element.setAttribute("href", newLink)
  const container = document.querySelector(".mega-container")
  container.addEventListener("click", (event) => {
    close_and_redirect(event, newLink);
  });
  

}

function close_and_redirect(event, link) {
  console.log("Redirecting... 1/2")
  event.preventDefault()
  chrome.runtime.sendMessage({ action: "redirect", link: link }, response => {
    if(response.done){
      window.close()
    }
  });
}

chrome.runtime.sendMessage({action: "getLink"}, response => {
  console.log(response.link);
  change_link(response.link);
})