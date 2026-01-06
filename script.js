function selectParty(element) {
    // remove selection from all parties
    document.querySelectorAll(".party").forEach(p => {
        p.classList.remove("selected");
    });

    // add selection to clicked party
    element.classList.add("selected");

    // auto-select radio button
    element.querySelector('input[type="radio"]').checked = true;
}

function submitVote() {
    let selected = document.querySelector('input[name="vote"]:checked');

    if (!selected) {
        alert("Please select a party");
        return;
    }

    fetch("/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate: selected.value })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "already_voted") {
            document.getElementById("msg").innerText = "❌ You already voted!";
        } else {
            document.getElementById("msg").innerText = "✅ Vote submitted successfully!";
        }
    });
}
