// If cookie is not set, then set cookie
/*
let cookie_value;
chrome.runtime.sendMessage({ action: "get_cookie" },
  function (response) {
    if (response.data === "") {
      chrome.runtime.sendMessage({ action: "set_cookie" },
        function (response) {
          cookie_value = response.data;
          console.log(cookie_value);
        }
      );
    } else {
      cookie_value = response.data;
      console.log(cookie_value);
    }
  }
);
*/
// If cookie is not set, then set cookie
// If cookie is not set, then set cookie
let cookie_value;
chrome.runtime.sendMessage({ action: "get_cookie" }, response => {
  if (response && response.cookie_value === "") {
    chrome.runtime.sendMessage({ action: "set_cookie" }, response => {
      if (response) {
        cookie_value = response.cookie_value;
        console.log(cookie_value);
      } else {
        console.log("Error setting cookie value");
      }
    });
  } else if (response && response.cookie_value) {
    cookie_value = response.cookie_value;
    console.log(cookie_value);
  } else {
    console.log("Error getting cookie value");
  }
});


console.log(cookie_value)
// Create a new button element
const button_container = document.createElement("div");
button_container.classList.add("button_conatainer");

const button_img = document.createElement("img");
button_img.src = chrome.runtime.getURL("images/button-img.png");
button_img.classList.add("button_img");

const myButton = document.createElement("a");

myButton.appendChild(button_img)
button_container.appendChild(myButton)

// Insert the new button element after the Amazon search button
document.querySelector(".nav-input").parentNode.appendChild(button_container);



const big_container = document.querySelector(".nav-input")
big_container.addEventListener("click", function () {
  setTimeout(function () {
    const s_sug = document.querySelectorAll(".s-suggestion-trending span.s-heavy")
    const rec_prompts = ["Recommend me 3 baby monitors for around 60$", "Give me a great book for self improvment", "What would be a great gift for my step-fathers birthday", "What is a great beginner microphone for a new streamer"]

    for (i = 0; i < rec_prompts.length; i++) {
      s_sug[i].textContent = rec_prompts[i]
    }
  }, 700)
})

// Add an event listener to the new button
button_img.addEventListener("click", async () => {
  // Find the Amazon search bar element
  const amazonSearchBar = document.querySelector("#twotabsearchtextbox");

  // Find the autocomplete results container
  const autocompleteContainer = document.querySelector("div.autocomplete-results-container");

  // Create a new div element to hold the search item text
  const searchItemDiv = document.createElement("div");
  searchItemDiv.classList.add("search-item-div");

  // Insert the new search item div into the autocomplete container
  autocompleteContainer.parentNode.replaceChild(searchItemDiv, autocompleteContainer);

  // Loading script - create loading elements
  // Mega div for loading
  const loadingMega = document.createElement("div");
  loadingMega.classList.add("loading-mega");

  // Create loading animation
  const loadingBar = document.createElement("div");
  loadingBar.classList.add("loading-bar");

  // Create loading text 
  const loadingPara = document.createElement("p");
  loadingPara.classList.add("loading-text");

  // Update loading text every few seconds
  const loadingText = ["Searching millions of products", "Analyzing reviews worldwide", "Calculating the best options", "Finding the perfect match", "Processing your preferences and needs", "Customizing recommendations for you"];
  let index = 0;
  let loadingTextInterval = setInterval(() => {
    index = (index + 1) % loadingText.length;
    loadingPara.textContent = loadingText[index];
  }, 2000);

  // Show loading animation + text
  loadingMega.appendChild(loadingBar);
  loadingMega.appendChild(loadingPara)
  searchItemDiv.appendChild(loadingMega);

  // Refresh / exit button
  const ref_img_container = document.createElement("div");
  ref_img_container.classList.add("ref_img_container")

  const refresh_img = document.createElement("img");
  refresh_img.src = chrome.runtime.getURL("images/ref-img.png");
  refresh_img.classList.add("refresh_img")

  ref_img_container.appendChild(refresh_img);
  document.querySelector(".nav-input").parentNode.appendChild(ref_img_container);


  // Send query to server and update display with results
  const query = amazonSearchBar.value;

  refresh_img.addEventListener('click', function() {
    amazonSearchBar.value = "";
    amazonSearchBar.textContent = "";
    location.reload();
  });
  const response = await fetch(`https://arelatia-eu.com/?param=${query}?${cookie_value}`);
  if(response.status != 200) {
    const formattedData = `
    <div class="mega-container">
      <p class="Error-text">Internal server error, we are so sorry, please try again. <br> If this issue persists please contact support!</p>
    </div>
    `;
    searchItemDiv.innerHTML = formattedData;
    console.error(response.text())
  }
  const data = await response.json();
  // Remove loading animation and update display with results
  loadingBar.remove();
  clearInterval(loadingTextInterval)
  searchItemDiv.removeChild(loadingMega)

  if (data == "error") {
    const formattedData = `
    <div class="mega-container">
      <p class="Error-text">Internal server error, we are so sorry, please try again. <br> If this issue persists please contact support!</p>
    </div>
    `;
    searchItemDiv.innerHTML = formattedData;
  }

  // All the data in variables (arrays)
  // const prompt = data.products["Prompt"] NOT USED ATM  
  const productNames = [];
  const productLinks = [];
  const productReviews = [];
  const img_links = [];
  const prices = [];
  const ratings = [];

  // push data to array from json 
  for (i = 0; i < data.length; i++) {
    productNames.push(data[i.toString()]["title"])
    productLinks.push(data[i.toString()]["link"])
    productReviews.push(data[i.toString()]["review"])
    img_links.push(data[i.toString()]["img_link"])
    prices.push(data[i.toString()]["price"])
    ratings.push(data[i.toString()]["rating"])
  }
  let formattedRecommendations = '';
  for (let i = 0; i < productNames.length; i++) {
    const name = productNames[i]
    const text = productReviews[i];
    const link = productLinks[i]
    const imgSrc = img_links[i];
    const price = prices[i];
    const rating = ratings[i];

    formattedRecommendations += `
    <div class="Product">
      <a href="${link}" title="${name}" style="text-decoration: none;" class="product-link">
        <div class="Product-container">

          <div class="Product-image-container">
              <img src="${imgSrc}" alt="${name}" class="Product-image">
          </div>

          <div class="Middle-container">
            <div class="Product-title-container">
                <p class="Product-title">
                  ${name}<br>
                </p>
            </div>

            <div class="Product-recommendation-container">
                <p class="Product-recommendation">${text}<br></p>
            </div>
          </div>

          <div class="Product-price-container">
            <p class="Product-price">
              <span>
                ${price}&nbsp;$
              </span>
            </p>

            <p class="Product-rating">
              <span>
              ${rating}&nbsp;/5
              </span>
            </p>

          </div>

        </div>
      </a>
    </div>
    `;
  }

  const formattedData = `
  <div class="mega-container">
    ${formattedRecommendations}
  </div>
  `;
  searchItemDiv.innerHTML = formattedData;
  const a_elements = document.querySelectorAll('.product-link');
  a_elements.forEach(link => {
    link.addEventListener('click', openPopup);
  });

  function openPopup(event) {
    event.preventDefault();
    const link = event.currentTarget.href;
    chrome.runtime.sendMessage({ action: "openPopup", link: link });
  }

});





