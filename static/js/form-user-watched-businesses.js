(function () {
  const pageRoot = document.getElementById("watchlist-form-page");
  if (!pageRoot) {
    return;
  }

  const formAddWatchList = document.getElementById("form-add-watch-list");
  const etablissementInput = document.getElementById(
    "add-watched-business-etablissement",
  );
  const etablissementHiddenInput = document.getElementById(
    "add-watched-business-etablissement-hidden",
  );
  const etablissementOptions = Array.from(
    document.querySelectorAll(
      "#add-watched-business-etablissement-options option",
    ),
  );
  const adresseInput = document.getElementById("add-watched-business-adresse");
  const businessIdHiddenInput = document.getElementById(
    "add-watched-business-business-id",
  );
  const adresseAfficheeInput = document.getElementById(
    "add-watched-business-adresse-affichee",
  );

  const currentWatchedBusinesses = JSON.parse(
    pageRoot.dataset.currentWatchedBusinesses || "[]",
  );
  const updateUrl = pageRoot.dataset.updateUrl;
  const redirectUrl = pageRoot.dataset.redirectUrl;

  function resetEtablissementSelection() {
    etablissementHiddenInput.value = "";
    adresseInput.value = "";
    adresseAfficheeInput.value = "";
    businessIdHiddenInput.value = "";
  }

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
    const businessId = selectedOption.dataset.business_id || "";
    adresseInput.value = adresse;
    adresseAfficheeInput.value = adresse;
    businessIdHiddenInput.value = businessId;
    return true;
  }

  if (etablissementInput && adresseInput && adresseAfficheeInput) {
    etablissementInput.addEventListener("input", function () {
      if (!this.value.trim()) {
        resetEtablissementSelection();
      }
    });

    etablissementInput.addEventListener("change", function () {
      syncEtablissementSelection();
    });
  }

  if (!formAddWatchList) {
    return;
  }

  formAddWatchList.addEventListener("submit", async function (event) {
    event.preventDefault();
    hideFeedbackMessage("#add-watched-business-message-form");

    try {
      if (!syncEtablissementSelection()) {
        throw new Error(
          "Veuillez sélectionner un établissement dans la liste.",
        );
      }

      const selectedBusiness = {
        business_id: parseInt(businessIdHiddenInput.value, 10),
        etablissement: etablissementHiddenInput.value.trim(),
        adresse: adresseInput.value.trim(),
      };

      if (
        !selectedBusiness.business_id ||
        !selectedBusiness.etablissement ||
        !selectedBusiness.adresse
      ) {
        throw new Error(
          "Les informations de l'établissement sélectionné sont incomplètes.",
        );
      }

      const alreadyWatched = currentWatchedBusinesses.some(function (business) {
        return Number(business.business_id) === selectedBusiness.business_id;
      });

      if (alreadyWatched) {
        throw new Error(
          "Cet établissement est déjà présent dans votre liste de surveillance.",
        );
      }

      const payload = {
        liste_etablissements_surveiller: [
          ...currentWatchedBusinesses,
          selectedBusiness,
        ],
      };

      const response = await fetch(updateUrl, {
        method: "PATCH",
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
        "#add-watched-business-message-form",
        data.message ||
          "Établissement ajouté à la liste de surveillance avec succès.",
        "success",
        { autoHide: true, delay: 4000 },
      );
      formAddWatchList.reset();
      resetEtablissementSelection();
      window.setTimeout(function () {
        window.location.href = redirectUrl;
      }, 1000);
    } catch (error) {
      showFeedbackMessage(
        "#add-watched-business-message-form",
        error.message,
        "error",
      );
    }
  });
})();
