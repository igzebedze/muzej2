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

      let selectedId = event.target.dataset.pk.substring(1);

      fetchAndRender(selectedId);

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

function fetchAndRender(id) {
  const target = document.getElementById("details");
  //target.innerHTML = "<div class='loading'>Nalagam podatke...</div>";
  fetch(`/evidenca/${id}/`)
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

function renderDetail(fields) {
  const { ime, nakup, nosilec } = fields;
  const target = document.getElementById("details");

  target.innerHTML = `
    <div class="computer">
      <button class="back">« Nazaj na seznam</button>
      <h2>${ime}</h2>
      <p>${nakup}</p>
      <dl>
        <dt>Nosilec:</dt>
        <dd><a href="/evidenca/organizacije/#${nosilec.pk}">${nosilec}</a></dd>
        {% if racunalnik.organizacija.count > 0 %}
        <dt>Uporabniki:</dt>
        <dd>
            {% for o in racunalnik.organizacija.all %}
            <a href="/evidenca/organizacije/#{{ o.pk }}">{{ o }}</a>
            {% if forloop.last %}{% else %}, {% endif %}
            {% endfor %}
        </dd>
        {% endif %}
        <dt>Lokacija:</dt>
        <dd>{{ racunalnik.kraj }}</dd>
        <dt>Proizvajalec:</dt>
        <dd>${proizvajalec}</dd>
        <dt>Pričetek:</dt>
        <dd>${nakup}</dd>
        {% if racunalnik.lastnistvo %}
        <dt>Status:</dt>
        <dd>{{ racunalnik.get_lastnistvo_display }}</dd>
        {% endif %}
        {% ifnotequal racunalnik.uporaba 'o' %}
        <dt>Uporaba:</dt>
        <dd>{{ racunalnik.get_uporaba_display }}</dd>
        {% endifnotequal %}
        {% if racunalnik.generacija %}
        <dt>Generacija:</dt>
        <dd>{{ racunalnik.get_generacija_display }}</dd>
        {% endif %}
        {% if racunalnik.tip %}
        <dt>Tip:</dt>
        <dd>{{ racunalnik.get_tip_display }}</dd>
        {% endif %}
        {% if racunalnik.opombe %}
        <dt>Opombe:</dt>
        <dd>{{ racunalnik.opombe }}</dd>
        {% endif %}
        {% if racunalnik.opis %}
        <dt>Opis:</dt>
        <dd>{{ racunalnik.opis }}</dd>
        {% endif %}
        <dt>Viri:</dt>
        <ul>
            {% for v in racunalnik.viri.all %}
            <li><a target='_blank' href='{{ v.url }}'>{{ v }}</a>
                <p>{{ v.vsebina }}</p>
            </li>
            {% endfor %}
        </ul>
    </dl> */
  </div>
  `;

  if (window.innerWidth > 1024) {
    document.querySelector(".details").classList.remove(HIDDEN_CLASSNAME);
  }
}

