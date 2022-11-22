const VISIBLE_CLASSNAME = "show";
const HIDDEN_CLASSNAME = "hide";
const SELECTED_CLASSNAME = "selected";

function getSelectedComputerId() {
  return document.location.hash.substring(1) || "";
}

window.onload = () => {
  if (window.innerWidth > 1024) {
    document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);
  }

  let selectedId = getSelectedComputerId();

  if (selectedId) {
    document.getElementById(selectedId).classList.add(VISIBLE_CLASSNAME);
  }

  window.addEventListener("hashchange", (event) => {
    if (selectedId) {
      document.getElementById(selectedId).classList.remove(VISIBLE_CLASSNAME);
    }
    selectedId = getSelectedComputerId();
    document.getElementById(selectedId).classList.add(VISIBLE_CLASSNAME);
  });

  document.body.addEventListener("click", (event) => {
    const backButtonClicked = event.target.matches(".back");

    if (event.target.matches(".list-item")) {
      const currentlySelected = document.querySelector(
        `.${SELECTED_CLASSNAME}`
      );
      if (currentlySelected) {
        document
          .querySelector(`.${SELECTED_CLASSNAME}`)
          .classList.remove(SELECTED_CLASSNAME);
      }
      if (!backButtonClicked) {
        event.target.classList.add(SELECTED_CLASSNAME);
      }
      document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);
    }

    if (event.target.matches(".back")) {
      const currentlySelected = document.querySelector(
        `.${SELECTED_CLASSNAME}`
      );
      if (currentlySelected) {
        document
          .querySelector(`.${SELECTED_CLASSNAME}`)
          .classList.remove(SELECTED_CLASSNAME);
      }
      document.querySelector(".details").classList.add(HIDDEN_CLASSNAME);
    }
  });
};
