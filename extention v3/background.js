// Generate a random identifier
const identifier = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

// Set the cookie with the identifier
function set_cookie() {
  console.log("Setting Cookies");
  const data = "user_id=" + identifier;
  return new Promise((resolve, reject) => {
    chrome.cookies.set({
      url: "https://amazon.com/",
      domain: "amazon.com",
      name: "Main-cookie",
      value: data
    }, (cookie) => {
      if (cookie) {
        resolve(data);
      } else {
        reject(new Error("Failed to set cookie"));
      }
    });
  });
}
  

  function get_cookie() {
    console.log("Getting cookie");
    return new Promise((resolve, reject) => {
      chrome.cookies.get({name: "Main-cookie", url: "https://amazon.com/"}, function(cookie) {
        if (cookie) {
          resolve(cookie.value);
        } else {
          console.log("Cookie not found");
          resolve("");
        }
      });
    });
}

var CURRENT_LINK = ""

function openPopup(link) {
  const width = 500;
  const height = 800;
  chrome.windows.getCurrent(function(currentWindow) {
    const left = Math.round(currentWindow.left + (currentWindow.width - width) / 2);
    const top = Math.round(currentWindow.top + (currentWindow.height - height) / 2);
    CURRENT_LINK = link
    chrome.windows.create({
      type: "popup",
      url: "middle/middleman.html",
      width,
      height,
      left,
      top
    });
  });
}


function redirect(link) {
  console.log("Redirecting... 2/2")
  chrome.tabs.create({ url: link }, function(tab) {
      chrome.tabs.update(tab.id, { active: true });
  });
}
  
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "openPopup") {
      openPopup(request.link);
    } else if (request.action === "getLink"){
      sendResponse({ link: CURRENT_LINK })
    }
    else if (request.action === "redirect") {
      redirect(request.link);
      sendResponse({done: true})
    }
    else if (request.action === "get_cookie") {
      get_cookie().then(
        cookie_value => {
          sendResponse({ cookie_value })
        }
      ).catch(error => {
        console.log("Error getting cookie")
        console.log(error)
      }
      );
    }
    else if (request.action === "set_cookie") {
      set_cookie().then(cookie_value => {
        console.log("Cookie set")
        sendResponse({ cookie_value })
      }).catch(error => {
        console.log("Error setting cookie")
        console.log(error)
      })
    }
    return true
});
  

