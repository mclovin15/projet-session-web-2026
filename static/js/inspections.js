/**
 * Gère le formulaire de demande d'inspection et le modal de suppression
 * des plaintes affichées sur la page des inspections.
 */
(function () {
  const formDemandeInspection = document.getElementById(
    "form-demande-inspection",
  );
  const etablissementInput = document.getElementById(
    "demande-inspection-etablissement",
  );
  const etablissementHiddenInput = document.getElementById(
    "demande-inspection-etablissement-hidden",
  );
  const etablissementOptions = Array.from(
    document.querySelectorAll(
      "#demande-inspection-etablissement-options option",
    ),
  );
  const adresseInput = document.getElementById("demande-inspection-adresse");
  const villeInput = document.getElementById("demande-inspection-ville");
  const businessIdHiddenInput = document.getElementById(
    "demande-inspection-business-id",
  );

  const adresseAfficheeInput = document.getElementById(
    "demande-inspection-adresse-affichee",
  );
  const villeAfficheeInput = document.getElementById(
    "demande-inspection-ville-affichee",
  );

  const modal = document.querySelector("[data-inspection-delete-modal]");
  const confirmButton = document.querySelector(
    "[data-inspection-modal-confirm]",
  );
  const cancelButton = document.querySelector("[data-inspection-modal-cancel]");
  const closeButton = document.querySelector("[data-inspection-modal-close]");
  const modalName = document.getElementById("inspection-delete-modal-name");
  const modalAddress = document.getElementById(
    "inspection-delete-modal-address",
  );
  const emptyState = document.getElementById("inspection-empty-state");

  if (!modal || !confirmButton) {
    return;
  }

  let selectedInspection = null;

  /** Ouvre le modal de confirmation pour la plainte sélectionnée. */
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

  /** Referme le modal et nettoie la sélection courante. */
  function closeModal() {
    selectedInspection = null;
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    modal.setAttribute("aria-hidden", "true");
    confirmButton.disabled = false;
  }
  /** Réinitialise les champs dépendants de l'établissement sélectionné. */
  function resetEtablissementSelection() {
    etablissementHiddenInput.value = "";
    villeInput.value = "";
    villeAfficheeInput.value = "";
    adresseInput.value = "";
    adresseAfficheeInput.value = "";
    businessIdHiddenInput.value = "";
  }

  /** Recopie les données de l'option choisie vers les champs du formulaire. */
  function syncEtablissementSelection() {
    const selectedValue = etablissementInput.value.trim();
    const selectedOption = etablissementOptions.find(
      (option) => option.value === selectedValue,
    );

    if (!selectedOption) {
      resetEtablissementSelection();
      return false;
    }

    etablissementHiddenInput.value = selectedOption.dataset.etablissement || "";
    const adresse = selectedOption.dataset.adresse || "";
    const ville = selectedOption.dataset.ville || "";
    const businessId = selectedOption.dataset.business_id || "";
    villeInput.value = ville;
    villeAfficheeInput.value = ville;
    adresseInput.value = adresse;
    adresseAfficheeInput.value = adresse;
    businessIdHiddenInput.value = businessId;
    return true;
  }

  if (
    etablissementInput &&
    adresseInput &&
    adresseAfficheeInput &&
    villeInput &&
    villeAfficheeInput
  ) {
    etablissementInput.addEventListener("input", function () {
      if (!this.value.trim()) {
        resetEtablissementSelection();
      }
    });

    etablissementInput.addEventListener("change", function () {
      syncEtablissementSelection();
    });
  }

  if (formDemandeInspection) {
    formDemandeInspection.addEventListener("submit", async function (event) {
      event.preventDefault();

      const payload = {
        business_id: Number(businessIdHiddenInput.value),
        nom_complet_client: document
          .getElementById("demande-inspection-nom-complet")
          .value.trim(),
        date_visite: document.getElementById("demande-inspection-date-visite")
          .value,
        etablissement: etablissementHiddenInput.value,
        adresse: adresseInput.value,
        ville: villeInput.value,
        description_prob: document
          .getElementById("demande-inspection-descriptions")
          .value.trim(),
      };

      hideFeedbackMessage("#demande-inspection-message-form");

      try {
        if (!syncEtablissementSelection()) {
          throw new Error(
            "Veuillez sélectionner un établissement dans la liste.",
          );
        }

        payload.etablissement = etablissementHiddenInput.value;
        payload.adresse = adresseInput.value;
        payload.ville = villeInput.value;
        payload.business_id = Number(businessIdHiddenInput.value);

        const response = await fetch("/demande-inspection", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          const erreurs = data.errors ? ` ${data.errors.join(" ")}` : "";
          throw new Error(
            (data.error || "Erreur lors de l'envoi de la demande.") + erreurs,
          );
        }

        showFeedbackMessage(
          "#demande-inspection-message-form",
          data.message || "Demande envoyée avec succès.",
          "success",
          { autoHide: true, delay: 4000 },
        );
        formDemandeInspection.reset();
        resetEtablissementSelection();
      } catch (error) {
        showFeedbackMessage(
          "#demande-inspection-message-form",
          error.message,
          "error",
        );
      }
    });
  }

  /** Affiche l'état vide lorsqu'il ne reste plus de plaintes visibles. */
  function renderEmptyState() {
    if (!emptyState) {
      return;
    }

    const remainingCards = document.querySelectorAll("[id^='plainte-']");
    emptyState.classList.toggle("hidden", remainingCards.length > 0);
  }

  document
    .querySelectorAll("[data-inspection-remove-button]")
    .forEach(function (button) {
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
      const response = await fetch(
        `/demande-inspection/${selectedInspection.id}`,
        {
          method: "DELETE",
        },
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          (data && data.error) ||
            "Une erreur est survenue lors de la suppression.",
        );
      }

      const plainteCard = document.getElementById(
        `plainte-${selectedInspection.id}`,
      );
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
      showFeedbackMessage(
        "#demande-inspection-message",
        error.message,
        "error",
      );
    }
  });
})();
