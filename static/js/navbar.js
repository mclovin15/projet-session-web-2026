(function () {
  const mobileMenuButton = document.querySelector("[data-mobile-menu-button]");
  const mobileMenuPanel = document.querySelector("[data-mobile-menu-panel]");
  const mobileMenuIcon = document.querySelector("[data-mobile-menu-icon]");
  const profileMenu = document.querySelector("[data-profile-menu]");
  const profileMenuButton = document.querySelector(
    "[data-profile-menu-button]",
  );
  const profileMenuPanel = document.querySelector("[data-profile-menu-panel]");

  function setMobileMenuState(isOpen) {
    if (!mobileMenuButton || !mobileMenuPanel || !mobileMenuIcon) {
      return;
    }

    mobileMenuButton.setAttribute("aria-expanded", String(isOpen));
    mobileMenuPanel.classList.toggle("hidden", !isOpen);
    mobileMenuIcon.classList.toggle("fa-bars", !isOpen);
    mobileMenuIcon.classList.toggle("fa-xmark", isOpen);
  }

  function setProfileMenuState(isOpen) {
    if (!profileMenuButton || !profileMenuPanel) {
      return;
    }

    profileMenuButton.setAttribute("aria-expanded", String(isOpen));
    profileMenuPanel.classList.toggle("hidden", !isOpen);
  }

  if (mobileMenuButton) {
    mobileMenuButton.addEventListener("click", function () {
      const isOpen = mobileMenuButton.getAttribute("aria-expanded") === "true";
      setMobileMenuState(!isOpen);
    });
  }

  if (profileMenuButton) {
    profileMenuButton.addEventListener("click", function () {
      const isOpen = profileMenuButton.getAttribute("aria-expanded") === "true";
      setProfileMenuState(!isOpen);
    });
  }

  document.addEventListener("click", function (event) {
    if (profileMenu && !profileMenu.contains(event.target)) {
      setProfileMenuState(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setMobileMenuState(false);
      setProfileMenuState(false);
    }
  });

  document.querySelectorAll("[data-logout-button]").forEach(function (button) {
    button.addEventListener("click", async function () {
      button.disabled = true;

      try {
        const response = await fetch("/logout", {
          method: "DELETE",
        });

        if (!response.ok && response.status !== 404) {
          const data = await response.json();
          throw new Error(
            (data && data.error) ||
              "Une erreur est survenue lors de la déconnexion.",
          );
        }

        window.location.href = "/login";
      } catch (error) {
        button.disabled = false;
        window.alert(error.message);
      }
    });
  });
})();
