const billInput = document.getElementById("billFile");
const dropZone = document.getElementById("dropZone");
const table = document.getElementById("data");
const tbody = document.getElementsByTagName("tbody")[0];
const summary = document.getElementById("summary");

async function submitBill() {
    const bill = billInput.files[0];

    if (!bill) {
        alert("Please choose a file first.");
        return;
    }

    const formData = new FormData();
    formData.append("bill", bill);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const info = await response.json();
            console.log(typeof info);
            const parsed = JSON.parse(info);
            const fields = ["action", "exposure", "reason"]
            for (ticker in parsed["individual"]) {
                if (parsed["individual"][ticker]["exposure"] == "high") {
                    const row = document.createElement("tr");
                    const ticker_cell = document.createElement("td");
                    ticker_cell.innerHTML = ticker;
                    row.appendChild(ticker_cell);
                    for (i=0; i<3; i++) {
                        const cell = document.createElement("td");
                        cell.innerHTML = parsed["individual"][ticker][fields[i]];
                        if (i == 0) {
                            cell.style.color = cell.innerHTML == "buy" ? "lime" : "red";
                        }
                        row.appendChild(cell);
                    }
                    tbody.appendChild(row);
                }
            }
            dropZone.style.display = "none";
            table.style.display = "flex";
            summary.innerHTML = parsed["summary"];
            summary.style.display = "flex";
        }
        else {
            alert("Upload failed.");
        }
    }
    catch (error) {
        console.error("Error uploading file:", error);
        alert("An error occurred.");
    }
}

billInput.onchange = submitBill

dropZone.onclick = () => {
    document.getElementById("billFile").click();
}
