(function () {
  const modal = document.querySelector("[data-inspection-delete-modal]");
  const confirmButton = document.querySelector("[data-inspection-modal-confirm]");
  const cancelButton = document.querySelector("[data-inspection-modal-cancel]");
  const closeButton = document.querySelector("[data-inspection-modal-close]");
  const modalName = document.getElementById("inspection-delete-modal-name");
  const modalAddress = document.getElementById("inspection-delete-modal-address");
  const emptyState = document.getElementById("inspection-empty-state");

  if (!modal || !confirmButton) {
    return;
  }

  let selectedInspection = null;

  function openModal(inspection) {
    selectedInspection = inspection;
    modalName.textContent = inspection.etablissement || "";
    modalAddress.textContent = inspection.adresse || "";
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    modal.setAttribute("aria-hidden", "false");
    confirmButton.disabled = false;
    confirmButton.focus();
  }

  function closeModal() {
    selectedInspection = null;
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    modal.setAttribute("aria-hidden", "true");
    confirmButton.disabled = false;
  }

  function renderEmptyState() {
    if (!emptyState) {
      return;
    }

    const remainingCards = document.querySelectorAll("[id^='plainte-']");
    emptyState.classList.toggle("hidden", remainingCards.length > 0);
  }

  document.querySelectorAll("[data-inspection-remove-button]").forEach(function (button) {
    button.addEventListener("click", function () {
      openModal({
        id: Number(button.dataset.id),
        etablissement: button.dataset.etablissement || "",
        adresse: button.dataset.adresse || "",
      });
    });
  });

  cancelButton.addEventListener("click", closeModal);
  if (closeButton) {
    closeButton.addEventListener("click", closeModal);
  }

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  confirmButton.addEventListener("click", async function () {
    if (!selectedInspection) {
      return;
    }

    confirmButton.disabled = true;
    hideFeedbackMessage("#demande-inspection-message");

    try {
      const response = await fetch(`/demande-inspection/${selectedInspection.id}`, {
        method: "DELETE",
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          (data && data.error) || "Une erreur est survenue lors de la suppression.",
        );
      }

      const plainteCard = document.getElementById(`plainte-${selectedInspection.id}`);
      if (plainteCard) {
        plainteCard.remove();
      }

      renderEmptyState();
      closeModal();
      showFeedbackMessage(
        "#demande-inspection-message",
        data.message || "Plainte supprimée avec succès.",
        "success",
        { autoHide: true, delay: 3500 },
      );
    } catch (error) {
      confirmButton.disabled = false;
      showFeedbackMessage("#demande-inspection-message", error.message, "error");
    }
  });
})();
