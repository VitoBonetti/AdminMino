document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector("#description-table");

  table.addEventListener("click", function (event) {
    if (event.target.closest(".edit-button")) {
      event.preventDefault();
      const descriptionId = event.target.closest("tr").dataset.descriptionId;
      getDescriptionData(descriptionId);
    } else if (event.target.closest(".delete-button")) {
      event.preventDefault();
      const descriptionId = event.target.closest("tr").dataset.descriptionId;
      if (confirm('Are you sure you want to delete this record?')) {
          deleteDescription(descriptionId);
      }
    }
  });
});

function getDescriptionData(descriptionId) {
  fetch(`/costs/descriptions/get-description/${descriptionId}`)
    .then((response) => response.json())
    .then((data) => {
      populateDescriptionForm(data);
    });
}

function populateDescriptionForm(data) {
  const categoryID = document.querySelector("#id_categoryID");
  const descriptionInput = document.querySelector("#id_description");
  const form = document.querySelector("#description-form");
  const hiddenInput = document.querySelector("input[name='id']");

  categoryID.value = data.category_id;
  descriptionInput.value = data.description;

  if (!hiddenInput) {
    const newHiddenInput = document.createElement("input");
    newHiddenInput.type = "hidden";
    newHiddenInput.name = "id";
    newHiddenInput.value = data.id;
    form.appendChild(newHiddenInput);
  } else {
    hiddenInput.value = data.id;
  }
}

function deleteDescription(descriptionId) {
  fetch(`/costs/descriptions/delete/${descriptionId}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        const rowToDelete = document.querySelector(`[data-description-id="${descriptionId}"]`);
        rowToDelete.remove();
        clearForm();
      }
    });
}

function clearForm() {
  const categoryID = document.querySelector("#id_categoryID");
  const descriptionInput = document.querySelector("#id_description");
  const hiddenInput = document.querySelector("input[name='id']");

  categoryID.value = "";
  descriptionInput.value = "";

  if (hiddenInput) {
    hiddenInput.remove();
  }
}