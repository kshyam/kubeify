document.addEventListener("DOMContentLoaded", function () {
  var cookieConsent = document.getElementById("cookieConsent");

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

    // Properly hide Bootstrap 3 modal
    $("#cookieDetailsModal").modal("hide");

    // Cleanup: force-remove leftover modal classes and elements
    $("body").removeClass("modal-open");
    $(".modal-backdrop").remove();
  }

  var ids = [
    "acceptCookies",
    "denyCookies",
    "acceptCookiesmobile",
    "denyCookiesmobile",
  ];
  ids.forEach(function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.addEventListener("click", function () {
        handleCookieChoice(id.includes("accept"));
      });
    }
  });

  var closeBtn = document.getElementById("closeCookieBox");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      cookieConsent.style.display = "none";
    });
  }

  var showDetails = document.getElementById("show-details");
  if (showDetails) {
    showDetails.addEventListener("click", function () {
      cookieConsent.style.display = "none";
      // Bootstrap's data-toggle will automatically show modal
    });
  }

  // Optional: also clean up after modal is closed any other way
  $("#cookieDetailsModal").on("hidden.bs.modal", function () {
    $("body").removeClass("modal-open");
    $(".modal-backdrop").remove();
  });
});
