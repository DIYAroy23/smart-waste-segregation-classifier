// Flask backend address
const API_URL = "http://127.0.0.1:5000";


// =========================
// GET HTML ELEMENTS
// =========================

const imageInput = document.getElementById("imageInput");

const previewImage = document.getElementById("previewImage");

const uploadPlaceholder =
    document.getElementById("uploadPlaceholder");

const classifyButton =
    document.getElementById("classifyButton");

const errorMessage =
    document.getElementById("errorMessage");

const resultCard =
    document.getElementById("resultCard");

const historyCard =
    document.getElementById("historyCard");

const historyButton =
    document.getElementById("historyButton");

const closeHistoryButton =
    document.getElementById("closeHistoryButton");

const historyList =
    document.getElementById("historyList");


// =========================
// IMAGE SELECTION
// =========================

imageInput.addEventListener("change", function () {

    const file = imageInput.files[0];

    if (!file) {
        return;
    }


    // Create image preview
    const imageURL = URL.createObjectURL(file);

    previewImage.src = imageURL;

    previewImage.style.display = "block";

    uploadPlaceholder.style.display = "none";


    // Enable classify button
    classifyButton.disabled = false;


    // Hide old result/error
    resultCard.style.display = "none";

    errorMessage.style.display = "none";
});


// =========================
// CLASSIFY IMAGE
// =========================

classifyButton.addEventListener("click", async function () {

    const file = imageInput.files[0];

    if (!file) {

        showError("Please select an image first.");

        return;
    }


    // Show loading state
    classifyButton.disabled = true;

    classifyButton.textContent = "Classifying...";

    errorMessage.style.display = "none";


    // Create FormData
    const formData = new FormData();

    // IMPORTANT:
    // "image" must match Flask request.files["image"]
    formData.append("image", file);


    try {

        // Send image to Flask
        const response = await fetch(
            `${API_URL}/predict`,
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Prediction failed."
            );
        }


        // Display result
        document.getElementById("prediction").textContent =
            data.prediction;

        document.getElementById("confidence").textContent =
            `${data.confidence}%`;

        document.getElementById("category").textContent =
            data.category;

        document.getElementById("bin").textContent =
            data.bin;

        document.getElementById("disposal").textContent =
            data.disposal;


        // Show result card
        resultCard.style.display = "block";

    }
    catch (error) {

        console.error(error);

        showError(
            "Could not connect to the backend. Make sure Flask is running."
        );

    }
    finally {

        classifyButton.disabled = false;

        classifyButton.textContent = "Classify Waste";
    }

});


// =========================
// SHOW ERROR
// =========================

function showError(message) {

    errorMessage.textContent = message;

    errorMessage.style.display = "block";
}


// =========================
// LOAD HISTORY
// =========================

historyButton.addEventListener(
    "click",
    loadHistory
);


async function loadHistory() {

    try {

        const response = await fetch(
            `${API_URL}/history`
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Could not load history."
            );
        }


        // Clear old history
        historyList.innerHTML = "";


        if (data.history.length === 0) {

            historyList.innerHTML =
                "<p>No scans found.</p>";

        }
        else {

            data.history.forEach(function (item) {

                const historyItem =
                    document.createElement("div");

                historyItem.className =
                    "history-item";


                historyItem.innerHTML = `

                    <div>

                        <h3>
                            ${item.prediction}
                        </h3>

                        <p>
                            ${item.filename}
                        </p>

                    </div>


                    <div>

                        <strong>
                            ${(item.confidence * 100).toFixed(2)}%
                        </strong>

                        <p>
                            ${item.category}
                        </p>

                    </div>


                    <div>

                        <strong>
                            ${item.bin_type}
                        </strong>

                        <p>
                            ${item.timestamp}
                        </p>

                    </div>

                `;


                historyList.appendChild(historyItem);

            });

        }


        // Show history
        historyCard.style.display = "block";

    }
    catch (error) {

        console.error(error);

        showError(
            "Could not load scan history."
        );

    }

}


// =========================
// CLOSE HISTORY
// =========================

closeHistoryButton.addEventListener(
    "click",
    function () {

        historyCard.style.display = "none";

    }
);