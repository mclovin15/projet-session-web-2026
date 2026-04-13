(function () {
  const MAX_AVATAR_SIZE_BYTES = 1300000;
  const ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png"];
  const form = document.getElementById("edit-profile-form");
  if (!form) {
    return;
  }

  const userIdInput = document.getElementById("edit-profile-user-id");
  const avatarInput = document.getElementById("edit-profile-avatar");
  const currentAvatarInput = document.getElementById("edit-profile-current-avatar");
  const avatarPreview = document.getElementById("edit-profile-avatar-preview");
  const sidePreview = document.getElementById("edit-profile-avatar-preview-side");
  const prenomInput = document.getElementById("edit-profile-prenom");
  const nomInput = document.getElementById("edit-profile-nom");

  async function readFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () =>
        reject(new Error("Impossible de lire le fichier sélectionné."));
      reader.readAsDataURL(file);
    });
  }

  function updateAvatarPreview(src) {
    if (avatarPreview) {
      avatarPreview.src = src;
    }
    if (sidePreview) {
      sidePreview.src = src;
    }
  }

  function isSupportedAvatarFile(file) {
    return Boolean(file && ALLOWED_AVATAR_TYPES.includes(file.type));
  }

  if (avatarInput) {
    avatarInput.addEventListener("change", async function () {
      const avatarFile = avatarInput.files && avatarInput.files[0];
      if (!avatarFile) {
        updateAvatarPreview(currentAvatarInput.value || avatarPreview.src);
        return;
      }

      if (!isSupportedAvatarFile(avatarFile)) {
        showFeedbackMessage(
          "#edit-profile-message",
          "L'avatar doit être au format JPG ou PNG.",
          "error",
        );
        avatarInput.value = "";
        updateAvatarPreview(currentAvatarInput.value || avatarPreview.src);
        return;
      }

      if (avatarFile.size > MAX_AVATAR_SIZE_BYTES) {
        showFeedbackMessage(
          "#edit-profile-message",
          "L'avatar est trop volumineux. Utilisez une image de moins de 1.3 Mo.",
          "error",
        );
        avatarInput.value = "";
        updateAvatarPreview(currentAvatarInput.value || avatarPreview.src);
        return;
      }

      try {
        hideFeedbackMessage("#edit-profile-message");
        const dataUrl = await readFileAsDataUrl(avatarFile);
        updateAvatarPreview(dataUrl);
      } catch (error) {
        showFeedbackMessage("#edit-profile-message", error.message, "error");
      }
    });
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    hideFeedbackMessage("#edit-profile-message");

    const nom = nomInput.value.trim();
    const prenom = prenomInput.value.trim();
    if (!nom || !prenom) {
      showFeedbackMessage(
        "#edit-profile-message",
        "Le nom et le prénom sont obligatoires.",
        "error",
      );
      return;
    }

    const payload = { nom, prenom };
    const avatarFile = avatarInput.files && avatarInput.files[0];

    if (avatarFile) {
      if (!isSupportedAvatarFile(avatarFile)) {
        showFeedbackMessage(
          "#edit-profile-message",
          "L'avatar doit être au format JPG ou PNG.",
          "error",
        );
        return;
      }

      if (avatarFile.size > MAX_AVATAR_SIZE_BYTES) {
        showFeedbackMessage(
          "#edit-profile-message",
          "L'avatar est trop volumineux. Utilisez une image de moins de 1.3 Mo.",
          "error",
        );
        return;
      }

      try {
        payload.avatar = await readFileAsDataUrl(avatarFile);
      } catch (error) {
        showFeedbackMessage("#edit-profile-message", error.message, "error");
        return;
      }
    }

    try {
      const response = await fetch(`/user/${userIdInput.value}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        const details = data.errors ? ` ${data.errors.join(" ")}` : "";
        throw new Error((data.error || "Erreur lors de la mise à jour du profil.") + details);
      }

      if (payload.avatar) {
        currentAvatarInput.value = payload.avatar;
      }

      showFeedbackMessage(
        "#edit-profile-message",
        data.message || "Profil mis à jour avec succès.",
        "success",
        { autoHide: true, delay: 1500 },
      );

      window.setTimeout(function () {
        window.location.reload();
      }, 900);
    } catch (error) {
      showFeedbackMessage("#edit-profile-message", error.message, "error");
    }
  });
})();
