(function () {
  const pageRoot = document.getElementById("watchlist-page");
  if (!pageRoot) {
    return;
  }

  const pageData = {
    userId: Number(pageRoot.dataset.userId),
    watchedBusinesses: JSON.parse(pageRoot.dataset.watchedBusinesses || "[]"),
  };

  const modal = document.querySelector("[data-watchlist-delete-modal]");
  const confirmButton = document.querySelector(
    "[data-watchlist-modal-confirm]",
  );
  const cancelButton = document.querySelector("[data-watchlist-modal-cancel]");
  const closeButton = document.querySelector("[data-watchlist-modal-close]");
  const modalName = document.getElementById("watchlist-delete-modal-name");
  const modalAddress = document.getElementById(
    "watchlist-delete-modal-address",
  );
  const emptyState = document.getElementById("watched-business-empty-state");

  let watchedBusinesses = Array.isArray(pageData.watchedBusinesses)
    ? [...pageData.watchedBusinesses]
    : [];
  let selectedBusiness = null;

  function openModal(business) {
    if (!modal || !confirmButton) {
      return;
    }

    selectedBusiness = business;
    modalName.textContent = business.etablissement || "";
    modalAddress.textContent = business.adresse || "";
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    modal.setAttribute("aria-hidden", "false");
    confirmButton.disabled = false;
    confirmButton.focus();
  }

  function closeModal() {
    if (!modal || !confirmButton) {
      return;
    }

    selectedBusiness = null;
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    modal.setAttribute("aria-hidden", "true");
    confirmButton.disabled = false;
  }

  function renderEmptyState() {
    if (!emptyState) {
      return;
    }

    emptyState.classList.toggle("hidden", watchedBusinesses.length > 0);
  }

  document
    .querySelectorAll("[data-watchlist-remove-button]")
    .forEach(function (button) {
      button.addEventListener("click", function () {
        openModal({
          business_id: Number(button.dataset.businessId),
          etablissement: button.dataset.etablissement || "",
          adresse: button.dataset.adresse || "",
        });
      });
    });

  if (cancelButton) {
    cancelButton.addEventListener("click", closeModal);
  }

  if (closeButton) {
    closeButton.addEventListener("click", closeModal);
  }

  if (modal) {
    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });
  }

  document.addEventListener("keydown", function (event) {
    if (
      event.key === "Escape" &&
      modal &&
      !modal.classList.contains("hidden")
    ) {
      closeModal();
    }
  });

  if (confirmButton) {
    confirmButton.addEventListener("click", async function () {
      if (!selectedBusiness) {
        return;
      }

      confirmButton.disabled = true;
      hideFeedbackMessage("#watched-business-message");

      const nextWatchList = watchedBusinesses.filter(function (business) {
        return (
          Number(business.business_id) !== Number(selectedBusiness.business_id)
        );
      });

      try {
        const response = await fetch(`/user_watch_list/${pageData.userId}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            liste_etablissements_surveiller: nextWatchList,
          }),
        });

        const data = await response.json();
        if (!response.ok) {
          const details = data.errors ? ` ${data.errors.join(" ")}` : "";
          throw new Error(
            (data.error || "Une erreur est survenue lors de la suppression.") +
              details,
          );
        }

        watchedBusinesses = nextWatchList;
        const article = document.getElementById(
          `watched_business-${selectedBusiness.business_id}`,
        );
        if (article) {
          article.remove();
        }
        renderEmptyState();
        closeModal();
        showFeedbackMessage(
          "#watched-business-message",
          data.message || "Établissement retiré de la liste de surveillance.",
          "success",
          { autoHide: true, delay: 3500 },
        );
      } catch (error) {
        confirmButton.disabled = false;
        showFeedbackMessage(
          "#watched-business-message",
          error.message,
          "error",
        );
      }
    });
  }
})();
