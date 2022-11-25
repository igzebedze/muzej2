const VISIBLE_CLASSNAME = "show";
const HIDDEN_CLASSNAME = "hide";
const SELECTED_CLASSNAME = "selected";

function getSelectedComputerId() {
  return document.location.hash.substring(2) || "";
}

window.onload = () => {
  const id = getSelectedComputerId();
  let lastClick = id;

  if (id) {
    document
      .querySelector(`.list-item-${id}`)
      .classList.add(SELECTED_CLASSNAME);
    fetchAndRender(id);
  }

  document.body.addEventListener("click", (event) => {
    if (event.target.matches(".list-item")) {
      if (lastClick) {
        document
          .querySelector(`.list-item-${lastClick}`)
          .classList.remove(SELECTED_CLASSNAME);
      }

      let type = event.target.getAttribute("data-type");
      let selectedId = event.target.getAttribute("data-oseba-pk");
      fetchAndRender(selectedId, type);

      event.target.classList.add(SELECTED_CLASSNAME);
      document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);

      lastClick = selectedId;
    }

    if (event.target.matches(".back")) {
      const selected = document.querySelector(`.${SELECTED_CLASSNAME}`);
      if (selected) {
        document
          .querySelector(`.${SELECTED_CLASSNAME}`)
          .classList.remove(SELECTED_CLASSNAME);
      }

      document.querySelector(".details").classList.add(HIDDEN_CLASSNAME);
    }
  });
};

function fetchAndRender(id,type) {
  const target = document.getElementById("details");
  var url = '/evidenca';
  if (type == 'oseba') { url = url + '/oseba'; }
  //target.innerHTML = "<div class='loading'>Nalagam podatke...</div>";
  fetch(`${url}/${id}/`)
    .then((response) => {
      return response.text();
    })
    .then((data) => {
//      renderDetail(data);
      const target = document.getElementById("details");
      target.innerHTML=data;
    });
    if (window.innerWidth > 1024) {
      document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);
    }
}
