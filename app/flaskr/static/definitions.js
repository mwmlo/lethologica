const showMoreButton = document.getElementById("show_more");
const definitionCards = document.getElementsByClassName("def_card");
const exploreButtons = document.getElementsByClassName("explore-button");
const exploreSpellcheck = document.getElementsByClassName("explore-spellcheck");

if (showMoreButton) { showMoreButton.addEventListener('click', showMore); }

for (var i = 0; i < definitionCards.length; i++) {
    definitionCards[i].addEventListener('click', toggleDefinition);
}
for (var i = 0; i < exploreButtons.length; i++) {
    exploreButtons[i].addEventListener('click', exploreDefinition);
}
for (var i = 0; i < exploreSpellcheck.length; i++) {
    exploreSpellcheck[i].addEventListener('click', exploreDefinition);
}

const results = JSON.parse(document.getElementById('results_access').textContent);

function toggleDefinition() {
    const res = this.querySelector(".res_word");
    const def = this.querySelector(".definition");
    var selection = window.getSelection();
    if (selection.type == "Range") {
        return;
    }
    if (def.style.display == "block") {
        res.style.fontWeight = "normal";
        def.style.display = "none";
        this.style.borderColor = "";
    } else {
        res.style.fontWeight = "bold";
        def.style.display = "block";
        this.style.borderColor = "#ffcf4c";
    }
}

let next_result = 10;
function showMore(event) {
    next_result += 20;
    filter();
}

function exploreDefinition(event) {
    const def = this.id;
    document.getElementById("def").value = def;
    event.stopPropagation();
    window.scrollTo(0, 0);
}

let filters = document.getElementById("filters").querySelectorAll("input");
for (var i = 0; i < filters.length; i++) {
    filters[i].addEventListener("change", filter);
}

function filter() {
    var displayed = 0;
    showMoreButton.hidden = true;
    for (i = 0; i < results.length; i++) {
        var result_card = document.getElementById("card_" + i);
        if ((document.getElementById("show_common").checked || (!results[i].common)) &&
            (document.getElementById("show_noun").checked || (results[i].pos != "noun")) &&
            (document.getElementById("show_verb").checked || (results[i].pos != "verb")) &&
            (document.getElementById("show_adj").checked || (results[i].pos != "adj")) &&
            (document.getElementById("show_adv").checked || (results[i].pos != "adv")) &&
            (document.getElementById("show_misc").checked || (results[i].pos != "other")) &&
            (displayed < next_result)) {
            displayed++;
            result_card.hidden = false;
        }
        else {
            result_card.hidden = true;
            if (displayed >= next_result) {
                showMoreButton.hidden = false;
            }
        }
    }
    document.getElementById("filter-hint").hidden = !(displayed === 0);
}

filter();
