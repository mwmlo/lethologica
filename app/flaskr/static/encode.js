import Transformer from "./transformer.js";
import { spellcheck } from "./spellcheck.js";
import "https://cdn.jsdelivr.net/npm/dompurify@3.0.9/dist/purify.min.js";

const transformer = new Transformer();
var extractorPromise = transformer.create_extractor();
const maxQueryLength = 120;

function handleSubmit(event) {
    event.preventDefault();

    var input = document.getElementById("def").value;
    var defForm = document.getElementById("def_form");

    // Append CSRF token to form data: some browsers don't do this automatically
    var csrfToken = document.querySelector('input[name="csrf_token"]').value;
    var csrfInput = document.createElement("input");
    csrfInput.setAttribute("type", "hidden");
    csrfInput.setAttribute("name", "csrf_token");
    csrfInput.setAttribute("value", csrfToken);
    defForm.appendChild(csrfInput);
    encodeInput(input, defForm);
}

async function encodeInput(input, defForm) {

    // Encodes input definition and adds the encoding as a new attribute in the
    // form which then gets sent to frontend as a post request

    if (!input == "") {
        if (input == "lethologicats") {
            // Easter egg: display running cats!
            var cats = document.getElementsByClassName("cat");
            for (var i = 0; i < cats.length; i++) {
                cats[i].style.display = 'block';
            }
        } else {
            // Show loading animation and remove previous results
            var loaders = document.getElementsByClassName('loader');
            for (var i = 0; i < loaders.length; i++) {
                loaders[i].style.display = 'block';
            }

            document.getElementById('query_results').style.display = 'none';
            document.getElementById('spellcheck').style.display = 'none';

            // Sanitise user input and truncate if too long
            input = DOMPurify.sanitize(input);
            document.getElementById("def").value = input
            if (input.length > maxQueryLength) {
                input = input.substring(0, maxQueryLength);
                document.getElementById("def").value = input + "...";
            }

            // Spellcheck
            var spellcheckedInput = document.createElement("input");
            spellcheckedInput.setAttribute("name", "spellchecked_input");
            spellcheckedInput.setAttribute("value", spellcheck(input));
            spellcheckedInput.setAttribute("type", "hidden");
            defForm.appendChild(spellcheckedInput);

            // Encode
            await extractorPromise;
            var embedding = await transformer.encode(input);
            var embeddingInput = document.createElement("input");
            embeddingInput.setAttribute("name", "embedding_input");
            embeddingInput.setAttribute("value", JSON.stringify(embedding));
            embeddingInput.setAttribute("type", "hidden");
            defForm.appendChild(embeddingInput);

            defForm.submit();
        }
    }
}

document.getElementById("def_form").addEventListener("submit", handleSubmit);

// Remove loading animation when POST request succeeds
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('query_results').style.display = 'block';
    document.getElementById('spellcheck').style.display = 'flex';
    var loaders = document.getElementsByClassName('loader');
    for (var i = 0; i < loaders.length; i++) {
        loaders[i].style.display = 'none';
    }
});
