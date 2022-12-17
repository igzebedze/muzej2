const VISIBLE_CLASSNAME = "show";
const HIDDEN_CLASSNAME = "hide";
const SELECTED_CLASSNAME = "selected";
const FILTERED_CLASSNAME = "filtered-out";

function getSelectedComputerId() {
  return document.location.hash.substring(2) || "";
}

function handleBackButtonClick() {
  const selected = document.querySelector(`.${SELECTED_CLASSNAME}`);
  if (selected) {
    document
      .querySelector(`.${SELECTED_CLASSNAME}`)
      .classList.remove(SELECTED_CLASSNAME);
  }

  document.querySelector(".details").classList.add(HIDDEN_CLASSNAME);
}

window.onload = () => {
  const id = getSelectedComputerId();
  let lastClick = id;

  var type='';
  if (window.location.href.indexOf("osebe") > -1) {
    type = 'oseba';
  }
  if (window.location.href.indexOf("app") > -1) {
    type = 'eksponat';
  }
  if (window.location.href.indexOf("proizvajalec") > -1) {
    type = 'proizvajalec';
  }

  if (id) {
    document
      .querySelector(`.list-item-${id}`)
      .classList.add(SELECTED_CLASSNAME);
    fetchAndRender(id, type);
  }

  document.body.addEventListener("click", (event) => {
    const target = event.target;
    // handle computer selection from list
    if (target.matches(".list-item")) {
      if (lastClick) {
        document
          .querySelector(`.list-item-${lastClick}`)
          .classList.remove(SELECTED_CLASSNAME);
      }

      let type = target.getAttribute("data-type");
      let selectedId = target.getAttribute("data-pk");
      fetchAndRender(selectedId, type);

      target.classList.add(SELECTED_CLASSNAME);
      document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);

      lastClick = selectedId;
    }

    // handle back button click
    if (target.matches(".back")) {
      handleBackButtonClick();
    }

    // handle organization filter click
    if (target.matches(".org-filter")) {
      event.preventDefault();

      const listItems = document.querySelectorAll(".list-item");
      const orgPk = event.target.href.split("#")[1];

      listItems.forEach((item) => {
        item.classList.remove(FILTERED_CLASSNAME);
      });

      listItems.forEach((item) => {
        const orgPks = item.dataset.orgPk.replaceAll(" ", "").split("D");

        if (!orgPks.includes(orgPk)) {
          item.classList.add(FILTERED_CLASSNAME);
        }
      });

      document.getElementById("clearFilters").classList.add(VISIBLE_CLASSNAME);

      if (window.innerWidth <= 1024) {
        handleBackButtonClick();
      }
    }

    // reset filters
    if (target.matches("#clearFilters")) {
      const listItems = document.querySelectorAll(".list-item");

      listItems.forEach((item) => {
        item.classList.remove(FILTERED_CLASSNAME);
      });

      document
        .getElementById("clearFilters")
        .classList.remove(VISIBLE_CLASSNAME);
    }
  });
};

function fetchAndRender(id, type) {
  var url = "/evidenca";

  if (type == "oseba") {
    url = url + "/oseba";
  }
  if (type == 'eksponat') {
    url = "/app";
  }
  if (type == 'proizvajalec') {
    url = "/app/proizvajalec";
  }

  fetch(`${url}/${id}/`)
    .then((response) => {
      return response.text();
    })
    .then((data) => {
      const target = document.getElementById("details");
      target.innerHTML = data;
    });

  if (window.innerWidth > 1024) {
    document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);
  }
}
