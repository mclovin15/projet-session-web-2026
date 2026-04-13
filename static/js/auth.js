(function () {
  const MAX_AVATAR_SIZE_BYTES = 1300000;
  const ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png"];

  async function readFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () =>
        reject(new Error("Impossible de lire le fichier sélectionné."));
      reader.readAsDataURL(file);
    });
  }

  function getErrorMessage(data, fallbackMessage) {
    if (!data) {
      return fallbackMessage;
    }

    const details =
      Array.isArray(data.errors) && data.errors.length
        ? ` ${data.errors.join(" ")}`
        : "";

    return `${data.error || fallbackMessage}${details}`;
  }

  function isSupportedAvatarFile(file) {
    return Boolean(file && ALLOWED_AVATAR_TYPES.includes(file.type));
  }

  // LOGIN
  function initLoginForm() {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) {
      return;
    }

    loginForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      hideFeedbackMessage("#login-message");

      const payload = {
        email: document.getElementById("login-email").value.trim(),
        password: document.getElementById("login-password").value,
      };

      if (!payload.email || !payload.password) {
        showFeedbackMessage(
          "#login-message",
          "Veuillez remplir votre courriel et votre mot de passe.",
          "error",
        );
        return;
      }

      try {
        const response = await fetch("/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            getErrorMessage(data, "Erreur lors de la connexion."),
          );
        }

        showFeedbackMessage(
          "#login-message",
          data.message || "Connexion réussie.",
          "success",
          {
            autoHide: true,
            delay: 1200,
          },
        );

        window.setTimeout(function () {
          window.location.href = "/";
        }, 900);
      } catch (error) {
        showFeedbackMessage("#login-message", error.message, "error");
      }
    });
  }

  // SIGNIN
  function initSigninForm() {
    const signinForm = document.getElementById("signin-form");
    if (!signinForm) {
      return;
    }

    const selectionInput = document.getElementById(
      "signin-etablissement-search",
    );
    const addButton = document.getElementById("signin-add-etablissement");
    const selectedContainer = document.getElementById(
      "signin-selected-etablissements",
    );
    const emptyState = document.getElementById("signin-empty-state");
    const options = Array.from(
      document.querySelectorAll("#signin-etablissement-options option"),
    );
    const avatarInput = document.getElementById("signin-avatar");
    const selectedEtablissements = [];

    function renderSelectedEtablissements() {
      selectedContainer
        .querySelectorAll("[data-selected-etablissement]")
        .forEach((element) => {
          element.remove();
        });

      if (!selectedEtablissements.length) {
        emptyState.classList.remove("hidden");
        return;
      }

      emptyState.classList.add("hidden");

      selectedEtablissements.forEach((etablissement, index) => {
        const item = document.createElement("div");
        item.setAttribute("data-selected-etablissement", "true");
        item.className =
          "flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:flex-row md:items-center md:justify-between";

        const content = document.createElement("div");

        const name = document.createElement("p");
        name.className = "text-sm font-semibold text-slate-900";
        name.textContent = etablissement.etablissement;

        const address = document.createElement("p");
        address.className = "mt-1 text-sm text-slate-500";
        address.textContent = etablissement.adresse;

        const businessId = document.createElement("p");
        businessId.className =
          "mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400";
        businessId.textContent = `Business ID ${etablissement.business_id}`;

        content.appendChild(name);
        content.appendChild(address);
        content.appendChild(businessId);

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className =
          "inline-flex items-center justify-center rounded-full bg-red-100 px-4 py-2 text-sm font-semibold text-red-600 shadow-sm transition hover:bg-slate-100";
        removeButton.setAttribute("data-remove-index", String(index));
        removeButton.innerHTML = '<i class="fa-solid fa-trash-can"></i>';

        item.appendChild(content);
        item.appendChild(removeButton);
        selectedContainer.appendChild(item);
      });
    }

    function addSelectedEtablissement() {
      const selectedValue = selectionInput.value.trim();
      const selectedOption = options.find(
        (option) => option.value === selectedValue,
      );

      if (!selectedOption) {
        showFeedbackMessage(
          "#signin-message",
          "Veuillez choisir un établissement présent dans la liste.",
          "error",
        );
        return false;
      }

      const businessId = Number(selectedOption.dataset.business_id);
      if (
        selectedEtablissements.some((item) => item.business_id === businessId)
      ) {
        showFeedbackMessage(
          "#signin-message",
          "Cet établissement est déjà dans votre liste.",
          "warning",
          {
            autoHide: true,
            delay: 2500,
          },
        );
        return false;
      }

      selectedEtablissements.push({
        business_id: businessId,
        etablissement: selectedOption.dataset.etablissement || "",
        adresse: selectedOption.dataset.adresse || "",
      });

      selectionInput.value = "";
      renderSelectedEtablissements();
      hideFeedbackMessage("#signin-message");
      return true;
    }

    addButton.addEventListener("click", addSelectedEtablissement);

    selectionInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        addSelectedEtablissement();
      }
    });

    selectedContainer.addEventListener("click", function (event) {
      const removeButton = event.target.closest("[data-remove-index]");
      if (!removeButton) {
        return;
      }

      const index = Number(removeButton.dataset.removeIndex);
      selectedEtablissements.splice(index, 1);
      renderSelectedEtablissements();
    });

    signinForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      hideFeedbackMessage("#signin-message");

      const password = document.getElementById("signin-password").value;
      const passwordConfirmation = document.getElementById(
        "signin-password-confirmation",
      ).value;

      if (password !== passwordConfirmation) {
        showFeedbackMessage(
          "#signin-message",
          "Les mots de passe ne correspondent pas.",
          "error",
        );
        return;
      }

      if (!selectedEtablissements.length) {
        showFeedbackMessage(
          "#signin-message",
          "Ajoutez au moins un établissement à surveiller.",
          "error",
        );
        return;
      }

      let avatar = null;
      const avatarFile = avatarInput.files && avatarInput.files[0];
      if (avatarFile) {
        if (!isSupportedAvatarFile(avatarFile)) {
          showFeedbackMessage(
            "#signin-message",
            "L'avatar doit être au format JPG ou PNG.",
            "error",
          );
          return;
        }

        if (avatarFile.size > MAX_AVATAR_SIZE_BYTES) {
          showFeedbackMessage(
            "#signin-message",
            "L'avatar est trop volumineux. Utilisez une image de moins de 1.3 Mo.",
            "error",
          );
          return;
        }

        try {
          avatar = await readFileAsDataUrl(avatarFile);
        } catch (error) {
          showFeedbackMessage("#signin-message", error.message, "error");
          return;
        }
      }

      const payload = {
        nom: document.getElementById("signin-nom").value.trim(),
        prenom: document.getElementById("signin-prenom").value.trim(),
        email: document.getElementById("signin-email").value.trim(),
        password,
        liste_etablissements_surveiller: selectedEtablissements,
      };

      if (avatar) {
        payload.avatar = avatar;
      }

      if (
        !payload.nom ||
        !payload.prenom ||
        !payload.email ||
        !payload.password
      ) {
        showFeedbackMessage(
          "#signin-message",
          "Veuillez remplir tous les champs obligatoires.",
          "error",
        );
        return;
      }

      try {
        const response = await fetch("/user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            getErrorMessage(data, "Erreur lors de la création du compte."),
          );
        }

        showFeedbackMessage(
          "#signin-message",
          data.message || "Compte créé avec succès.",
          "success",
          {
            autoHide: true,
            delay: 1500,
          },
        );

        signinForm.reset();
        selectedEtablissements.splice(0, selectedEtablissements.length);
        renderSelectedEtablissements();

        // On redirige vers page d'accueil
        window.setTimeout(function () {
          window.location.href = "/";
        }, 1000);
      } catch (error) {
        showFeedbackMessage("#signin-message", error.message, "error");
      }
    });
  }

  initLoginForm();
  initSigninForm();
})();
