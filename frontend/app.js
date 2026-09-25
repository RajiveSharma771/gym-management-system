// =====================================================
// Cloud Run Backend URL
// =====================================================

const API_URL = "";


// =====================================================
// Load All Members
// =====================================================

async function loadMembers() {

    const message = document.getElementById("message");
    const table = document.getElementById("membersTable");

    message.innerText = "Loading members...";

    try {

        const response = await fetch(
            `${API_URL}/api/members`
        );

        if (!response.ok) {

            throw new Error(
                `HTTP error: ${response.status}`
            );

        }

        const data = await response.json();

        table.innerHTML = "";

        data.members.forEach(member => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${member.id}</td>

                <td>${member.name}</td>

                <td>${member.email}</td>

                <td>${member.phone}</td>

                <td>${member.join_date}</td>

                <td>${member.status}</td>

                <td>

                    <button
                        type="button"
                        onclick="editMember(${member.id})"
                    >
                        Edit
                    </button>

                    <button
                        type="button"
                        onclick="deleteMember(${member.id})"
                    >
                        Delete
                    </button>

                </td>
            `;

            table.appendChild(row);

        });

        message.innerText =
            `${data.members.length} member(s) loaded.`;

    }

    catch (error) {

        console.error(error);

        message.innerText =
            "Unable to connect to the backend API.";

    }
}


// =====================================================
// Add New Member
// =====================================================

document
    .getElementById("memberForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const formMessage =
            document.getElementById("formMessage");

        const name =
            document.getElementById("name").value;

        const email =
            document.getElementById("email").value;

        const phone =
            document.getElementById("phone").value;

        formMessage.innerText =
            "Creating member...";

        try {

            const response = await fetch(
                `${API_URL}/api/members`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Failed to create member"
                );

            }

            formMessage.innerText =
                "Member created successfully!";

            document
                .getElementById("memberForm")
                .reset();

            await loadMembers();

        }

        catch (error) {

            console.error(error);

            formMessage.innerText =
                error.message;

        }

    });


// =====================================================
// Edit Member - Load Existing Data
// =====================================================

async function editMember(memberId) {

    const editSection =
        document.getElementById("editSection");

    const editMessage =
        document.getElementById("editMessage");

    editMessage.innerText =
        "Loading member...";

    try {

        const response = await fetch(
            `${API_URL}/api/members/${memberId}`
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to load member"
            );

        }

        // Fill edit form

        document.getElementById("editId").value =
            data.id;

        document.getElementById("editName").value =
            data.name;

        document.getElementById("editEmail").value =
            data.email;

        document.getElementById("editPhone").value =
            data.phone;

        document.getElementById("editStatus").value =
            data.status;


        // Show edit section

        editSection.style.display = "block";

        editMessage.innerText =
            `Editing member #${data.id}`;

        // Scroll to edit section

        editSection.scrollIntoView({
            behavior: "smooth"
        });

    }

    catch (error) {

        console.error(error);

        editMessage.innerText =
            error.message;

    }
}


// =====================================================
// Update Member
// =====================================================

document
    .getElementById("editMemberForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const editMessage =
            document.getElementById("editMessage");

        const memberId =
            document.getElementById("editId").value;

        const name =
            document.getElementById("editName").value;

        const email =
            document.getElementById("editEmail").value;

        const phone =
            document.getElementById("editPhone").value;

        const status =
            document.getElementById("editStatus").value;

        editMessage.innerText =
            "Updating member...";

        try {

            const response = await fetch(
                `${API_URL}/api/members/${memberId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone,
                        status: status
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Failed to update member"
                );

            }

            editMessage.innerText =
                "Member updated successfully!";

            await loadMembers();

        }

        catch (error) {

            console.error(error);

            editMessage.innerText =
                error.message;

        }

    });


// =====================================================
// Cancel Edit
// =====================================================

function cancelEdit() {

    document.getElementById(
        "editSection"
    ).style.display = "none";

    document.getElementById(
        "editMemberForm"
    ).reset();

    document.getElementById(
        "editMessage"
    ).innerText = "";

}


// =====================================================
// Delete Member
// =====================================================

async function deleteMember(memberId) {

    const confirmed = confirm(
        `Are you sure you want to delete member #${memberId}?`
    );

    if (!confirmed) {

        return;

    }

    try {

        const response = await fetch(
            `${API_URL}/api/members/${memberId}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to delete member"
            );

        }

        alert(
            "Member deleted successfully!"
        );

        await loadMembers();

    }

    catch (error) {

        console.error(error);

        alert(
            `Delete failed: ${error.message}`
        );

    }
}


// =====================================================
// Initial Page Load
// =====================================================

loadMembers();
