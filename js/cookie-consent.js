document.addEventListener("DOMContentLoaded", function () {
  var cookieConsent = document.getElementById("cookieConsent");
  var cookieDetailsModal = document.getElementById("cookieDetailsModal");

  // Show cookie popup after 15 seconds (once per session)
  if (
    (!localStorage.getItem("cookiesAccepted") ||
      localStorage.getItem("cookiesAccepted") === "false") &&
    !sessionStorage.getItem("cookiePopupShown")
  ) {
    setTimeout(function () {
      cookieConsent.style.display = "block";
      sessionStorage.setItem("cookiePopupShown", "true");
    }, 15000);
  }

  function handleCookieChoice(accepted) {
    localStorage.setItem("cookiesAccepted", accepted ? "true" : "false");
    cookieConsent.style.display = "none";

    // Hide modal if open
    const modalInstance = bootstrap.Modal.getInstance(cookieDetailsModal);
    if (modalInstance) {
      modalInstance.hide();
    }
  }

  // Handle accept/deny buttons
  [
    "acceptCookies",
    "denyCookies",
    "acceptCookiesmobile",
    "denyCookiesmobile",
  ].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.addEventListener("click", function () {
        handleCookieChoice(id.includes("accept"));
      });
    }
  });

  // Close button on banner
  var closeBtn = document.getElementById("closeCookieBox");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      cookieConsent.style.display = "none";
    });
  }

  // Handle "Show details" link
  var showDetails = document.getElementById("show-details");
  if (showDetails) {
    showDetails.addEventListener("click", function (e) {
      e.preventDefault();
      cookieConsent.style.display = "none";

      const modal = new bootstrap.Modal(cookieDetailsModal);
      modal.show();
    });
  }

  // Optional: cleanup after modal is closed
  cookieDetailsModal.addEventListener("hidden.bs.modal", function () {
    // modal closed, no need to remove any backdrop manually in Bootstrap 5
  });
});
